
import asyncio
import os
import sys
import json
import base64
import random
import datetime
import subprocess
from email.message import EmailMessage
from urllib.parse import urljoin, urlparse

try:
    import httpx
    from bs4 import BeautifulSoup
except ImportError:
    print("Gerekli kütüphaneler eksik. Lütfen 'pip install httpx beautifulsoup4' çalıştırın.")
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("Gerekli kütüphane eksik. Lütfen 'pip install Pillow' çalıştırın.")
    pass

# --- KONFİGÜRASYON ---
APP_TITLE = "HERMES CONSOLE v5.5 (Quality Inspector Update)"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# --- YOL AYARLARI ---
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")
BASE_LIB_PATH = os.path.join(DESKTOP_PATH, "Esoteric_Library")
DOWNLOADS_ROOT = os.path.join(BASE_LIB_PATH, "Kutuphane") # TÜRKÇE
FLIPBOOKS_ROOT = os.path.join(BASE_LIB_PATH, "Flipbooks") # ÖZEL FLIPBOOK KLASÖRÜ
MANIFEST_PATH = os.path.join(BASE_LIB_PATH, "library_manifest.json")
SETUP_SCRIPT_PATH = os.path.join(os.getcwd(), "setup_final_environment.py")

# --- RENKLER ---
C_HEADER = "\033[95m"
C_BLUE = "\033[94m"
C_GREEN = "\033[92m"
C_WARN = "\033[93m"
C_FAIL = "\033[91m"
C_RESET = "\033[0m"

# --- YARDIMCI FONSİYONLAR ---
def ensure_dirs(path):
    if not os.path.exists(path): os.makedirs(path)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def safe_filename(s):
    # Dosya adını güvenli hale getir
    s = str(s).strip().replace(" ", "_")
    return "".join([c for c in s if c.isalnum() or c in "._-"])

def log_to_manifest(title, url, local_path, file_type):
    ensure_dirs(BASE_LIB_PATH)
    data = {}
    if os.path.exists(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f: data = json.load(f)
        except: data = {}
    
    data[url] = {
        "title": title,
        "local_path": local_path,
        "type": file_type,
        "date": str(datetime.datetime.now()),
        "status": "downloaded"
    }
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- NUMARALANDIRMA SİSTEMİ ---
def get_next_folder_prefix():
    # Kutuphane klasöründeki mevcut klasörleri tara
    # "001_KitapAdi" formatına bak ve en son numarayı bul.
    ensure_dirs(DOWNLOADS_ROOT)
    max_num = 0
    if os.path.exists(DOWNLOADS_ROOT):
        for name in os.listdir(DOWNLOADS_ROOT):
            if os.path.isdir(os.path.join(DOWNLOADS_ROOT, name)):
                parts = name.split('_')
                if parts and parts[0].isdigit():
                    try:
                        num = int(parts[0])
                        if num > max_num: max_num = num
                    except: pass
    return f"{max_num + 1:03d}"

# --- 1. AGRESİF ÖRÜMCEK (Deep Spider) ---
async def fetch_page(client, url):
    try:
        resp = await client.get(url)
        return BeautifulSoup(resp.content, "html.parser"), resp.status_code
    except: return None, 0

async def scan_worker(client, url, allowed_domain, seen_urls, found_items):
    # URL Normalizasyonu
    url = url.split('#')[0]
    if url.endswith("/"): url = url[:-1]
    
    if url in seen_urls: return
    seen_urls.add(url)
    
    soup, status = await fetch_page(client, url)
    if not soup or status != 200: return

    # Sayfa Başlığı
    page_title = soup.title.string.strip() if soup.title else "Bilinmeyen Sayfa"
    print(f"   🕷️  Taranıyor: {page_title[:40]}... ({url})")

    # Linkleri Topla
    local_links = []
    
    for a in soup.find_all("a", href=True):
        href = a["href"]
        full_url = urljoin(url, href)
        
        full_url = full_url.split('#')[0]
        if full_url.endswith("/"): full_url = full_url[:-1]
        
        text = a.get_text(" ", strip=True) or os.path.basename(href)
        t_low = text.lower()
        u_low = full_url.lower()
        
        if href.startswith(("#", "javascript:", "mailto:", "tel:")): continue
        
        current_domain = urlparse(full_url).netloc
        if allowed_domain not in current_domain: continue

        item_type = None; icon = "🔗"; prio = 0
        
        if u_low.endswith(".pdf"):
            item_type = "PDF"; icon = "📕"; prio = 6
        elif u_low.endswith((".zip", ".rar", ".7z")):
            item_type = "ARCHIVE"; icon = "📦"; prio = 5
        elif u_low.endswith((".epub", ".mobi")):
            item_type = "EBOOK"; icon = "📘"; prio = 6
        elif u_low.endswith((".jpg", ".png", ".gif")):
             pass 
        else:
            if full_url not in seen_urls:
                local_links.append(full_url)
            
            series_keys = ["book", "part", "volume", "liber", "appendix", "chapter", "index", "contents"]
            if any(k in t_low for k in series_keys):
                item_type = "BOOK_PART"; icon = "📚"; prio = 4
            elif "read" in t_low or "view" in t_low:
                item_type = "RESOURCE"; icon = "📄"; prio = 3

        if item_type:
            if not any(x['url'] == full_url for x in found_items):
                found_items.append({
                    "title": text[:80],
                    "url": full_url,
                    "type": item_type,
                    "icon": icon,
                    "prio": prio,
                    "source_page": page_title
                })

    return local_links

async def deep_crawl(start_url, max_depth=2):
    print(f"\n{C_BLUE}🕸️  [ÖRÜMCEK AĞI] Başlatılıyor... Derinlik: {max_depth}{C_RESET}")
    
    netloc = urlparse(start_url).netloc
    parts = netloc.split('.')
    if len(parts) > 2: allowed_domain = ".".join(parts[-2:]) 
    else: allowed_domain = netloc
    
    seen_urls = set()
    found_items = []
    
    queue = [(start_url, 0)]
    
    max_pages = 300 
    visited_pages = 0
    
    async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}, verify=False, timeout=15, follow_redirects=True) as client:
        while queue:
            if visited_pages >= max_pages:
                print(f"{C_WARN}⚠️  Maksimum sayfa limitine ({max_pages}) ulaşıldı. Tarama kesiliyor.{C_RESET}")
                break
                
            current_url, depth = queue.pop(0) 
            
            if depth > max_depth: continue
            
            new_links = await scan_worker(client, current_url, allowed_domain, seen_urls, found_items)
            visited_pages += 1
            
            if new_links and depth < max_depth:
                for link in new_links:
                    if link.split('#')[0] not in seen_urls: 
                        queue.append((link, depth + 1))
    
    found_items.sort(key=lambda x: x["prio"], reverse=True)
    
    main_title = "Bilinmeyen Arşiv"
    if found_items: main_title = found_items[0]['source_page']
    
    return main_title, found_items

# --- 2. SEÇİM ARAYÜZÜ ---
def selection_menu(items, source_title):
    selected_indices = set()
    cursor = 0
    
    while True:
        clear_screen()
        print(f"{C_HEADER}=== {APP_TITLE} ==={C_RESET}")
        print(f"Kaynak: {source_title}")
        print(f"Toplam: {len(items)} | Seçilen: {len(selected_indices)}")
        print(f"{C_WARN}[↑/↓] Gez | [SPACE] İşaretle | [ENTER] İndir | [A] Tümünü Seç | [ESC] Geri{C_RESET}")
        print("-" * 60)
        
        window = 18
        start = max(0, cursor - window // 2)
        end = min(len(items), start + window)
        
        for i in range(start, end):
            item = items[i]
            chk = f"{C_GREEN}[X]{C_RESET}" if i in selected_indices else "[ ]"
            if i == cursor and i not in selected_indices: chk = f"{C_WARN}[?]{C_RESET}"
            
            prefix = "-> " if i == cursor else "   "
            print(f"{prefix}{chk} {item['icon']} {item['type']}: {item['title']}")
            
        try:
            import msvcrt
            key = msvcrt.getch()
            if key == b'\xe0': 
                k = msvcrt.getch()
                if k == b'H': cursor = max(0, cursor - 1)
                elif k == b'P': cursor = min(len(items)-1, cursor + 1)
            elif key == b' ':
                if cursor in selected_indices: selected_indices.remove(cursor)
                else: selected_indices.add(cursor)
            elif key == b'a' or key == b'A':
                if len(selected_indices) == len(items): selected_indices.clear()
                else: selected_indices.update(range(len(items)))
            elif key == b'\r':
                if not selected_indices: return [items[cursor]]
                return [items[i] for i in selected_indices]
            elif key == b'\x1b': return None
        except: return items

# --- 2.3 HELPER: E-Kitap Path Çıkarıcı ---
async def extract_ebook_path(client, url):
    """
    Ata E-Kitap gibi sitelerden data-ebook-path özelliğini çıkar.
    Örn: /e-books/2023-2024/Ortaokul/7-sinif/.../index.html
    """
    try:
        resp = await client.get(url)
        if resp.status_code != 200:
            return None
        
        soup = BeautifulSoup(resp.content, "html.parser")
        
        # Ata E-Kitap pattern: <a data-ebook-path="/e-books/...">
        link = soup.find("a", {"data-ebook-path": True})
        if link:
            path = link.get("data-ebook-path")
            if path:
                print(f"      ✅ E-Kitap path bulundu: {path[:80]}")
                # Construct full URL
                from urllib.parse import urljoin, urlparse
                parsed = urlparse(url)
                base = f"{parsed.scheme}://{parsed.netloc}"
                full_url = urljoin(base, path)
                return full_url
        
        return None
    except:
        return None

# --- FLIPHTML5 (FARKLI YAP) İNDİRİCİ ---
def detect_fliphtml5(url):
    """Fliphtml5 linki mi kontrol et"""
    return "fliphtml5.com" in url.lower() or "fliphtm" in url.lower()

async def download_fliphtml5_book(client, base_url, target_dir, title):
    """Fliphtml5 kitabını sayfalar halinde indir ve PDF'ye çevir"""
    print(f"\n{C_BLUE}📚 Fliphtml5 Modu Aktif: Config aranıyor...{C_RESET}")
    
    # URL'den fragment kaldır (# ve sonrası)
    base_url_clean = base_url.split("#")[0] if "#" in base_url else base_url
    
    try:
        # Config.js'i al
        config_url = f"{base_url_clean.rstrip('/')}/javascript/config.js"
        config_resp = await client.get(config_url, timeout=10)
        
        if config_resp.status_code != 200:
            print(f"{C_WARN}⚠️  Config alınamadı ({config_resp.status_code}){C_RESET}")
            return []
        
        # JSON parse et
        import re
        match = re.search(r'var htmlConfig = (\{.*?\});', config_resp.text, re.DOTALL)
        if not match:
            print(f"{C_WARN}⚠️  Config parse hatası{C_RESET}")
            return []
        
        config = json.loads(match.group(1))
        pages = config.get("fliphtml5_pages", [])
        page_count = config.get("meta", {}).get("pageCount", len(pages))
        
        if page_count == 0:
            print(f"{C_WARN}⚠️  Sayfa bulunamadı{C_RESET}")
            return []
        
        print(f"      ✅ {page_count} sayfa bulundu")
        print("      📥 Sayfalar indiriliyor...")
        
        # Sayfaları indir
        downloaded_pages = []
        consecutive_errors = 0
        
        for idx, page_info in enumerate(pages, 1):
            try:
                # Rate limiting (her 20 sayfa sonra bekleme)
                if idx % 20 == 0:
                    await asyncio.sleep(1)
                
                page_filename = page_info['n'][0]
                page_url = f"{base_url_clean.rstrip('/')}/files/large/{page_filename}"
                
                resp = await client.get(page_url, timeout=15)
                
                if resp.status_code != 200:
                    consecutive_errors += 1
                    if consecutive_errors > 5:
                        print(f"         ⚠️  Ardışık 5 hata, durduriliyor")
                        break
                    continue
                
                consecutive_errors = 0
                
                # Dosyayı kaydet
                fname = f"{idx:04d}.webp"
                fpath = os.path.join(target_dir, fname)
                with open(fpath, "wb") as f:
                    f.write(resp.content)
                
                downloaded_pages.append(fpath)
                
                # Progress göster
                if idx % 20 == 0 or idx == 1 or idx == page_count:
                    pct = (idx / page_count) * 100
                    print(f"         Sayfa {idx}/{page_count} ({pct:.0f}%)", end="\r")
                
            except asyncio.TimeoutError:
                consecutive_errors += 1
            except Exception as e:
                consecutive_errors += 1
        
        print(f"\n      ✅ Toplam {len(downloaded_pages)} sayfa indirildi")
        return downloaded_pages
        
    except Exception as e:
        print(f"{C_FAIL}      ❌ Fliphtml5 Hatası: {e}{C_RESET}")
        return []

# --- 2.5 FLIPBOOK (RESİM SERİSİ) İNDİRİCİ ---
async def download_flipbook_images(client, base_url, target_dir, title):
    print(f"\n{C_BLUE}📚 Flipbook Modu Aktif: Resim serisi taranıyor...{C_RESET}")
    print("      (Bu işlem, sayfa yapısını tahmin etmeye çalışır)")

    found_images = []
    page_num = 1
    consecutive_errors = 0
    
    # URL TEMİZLİĞİ: index.html varsa at
    if base_url.endswith("index.html") or base_url.endswith(".php"):
        base_url = base_url.rsplit('/', 1)[0]
    
    parsed = urlparse(base_url)
    if not base_url.endswith('/'): base_url += '/'
    
    # GÜNCELLENMİŞ DESENLER
    patterns = ["files/mobile/", "files/large/", "mobile/", "files/shot/", "pages/", "", "files/page/"]
    valid_pattern = None
    
    for pat in patterns:
        test_url = urljoin(base_url, f"{pat}1.jpg")
        try:
            r = await client.get(test_url)
            if r.status_code == 200:
                print(f"      ✅ Desen Bulundu: {pat}1.jpg")
                valid_pattern = pat
                break
        except: pass
        
    if not valid_pattern:
        print(f"{C_WARN}⚠️  Otomatik desen bulunamadı. Standart tarama yapılacak.{C_RESET}")
        return []

    print("      📥 Sayfalar indiriliyor...")
    
    while True:
        img_url = urljoin(base_url, f"{valid_pattern}{page_num}.jpg")
        try:
            resp = await client.get(img_url)
            if resp.status_code != 200:
                img_url = urljoin(base_url, f"{valid_pattern}{page_num}.png")
                resp = await client.get(img_url)
            
            if resp.status_code == 200:
                fname = f"{page_num:04d}.jpg" 
                fpath = os.path.join(target_dir, fname)
                with open(fpath, "wb") as f: f.write(resp.content)
                found_images.append(fpath)
                print(f"         Sayfa {page_num} OK", end="\r")
                page_num += 1
                consecutive_errors = 0
            else:
                consecutive_errors += 1
                if consecutive_errors > 5: 
                    break
        except: break
             
    print(f"\n      ✅ Toplam {len(found_images)} sayfa indirildi.")
    return found_images

def create_pdf_from_images(image_paths, output_pdf_path):
    if not image_paths: return False
    print(f"      📚 PDF Ciltleniyor... ({len(image_paths)} sayfa)")
    try:
        images = []
        for p in image_paths:
            img = Image.open(p)
            if img.mode != 'RGB': img = img.convert('RGB')
            images.append(img)
            
        if images:
            images[0].save(output_pdf_path, "PDF", resolution=100.0, save_all=True, append_images=images[1:])
            print(f"      ✨ PDF Hazır: {os.path.basename(output_pdf_path)}")
            return True
    except Exception as e:
        print(f"      ❌ PDF Hatası: {e}")
        return False
    return False

# --- 3. İNDİRME VE KAYDETME ---
async def download_worker_full(items, folder_name_raw, is_flipbook=False, flipbook_url=None):
    if is_flipbook: 
        # --- EVRENSEL MANUEL İNDİRME MODU ---
        clean_folder_name = safe_filename(folder_name_raw)
        target_dir = os.path.join(FLIPBOOKS_ROOT, clean_folder_name)
        ensure_dirs(target_dir) 
        
        print(f"\n{C_GREEN}🚀 Manuel İndirme Başlatılıyor...{C_RESET}")
        print(f"📂 Hedef: {target_dir}")
        print(f"📄 İsim: {clean_folder_name}")
        
        async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}, verify=False, timeout=60, follow_redirects=True) as client:
            if flipbook_url:
                # 0. Fliphtml5 Algılaması (Özel Handler)
                if detect_fliphtml5(flipbook_url):
                    print("      🌐 Tür: Fliphtml5 - Özel Handler Kullanılıyor...")
                    downloaded = await download_fliphtml5_book(client, flipbook_url, target_dir, clean_folder_name)
                    if downloaded:
                        pdf_name = f"{clean_folder_name}.pdf"
                        pdf_path = os.path.join(target_dir, pdf_name)
                        if create_pdf_from_images(downloaded, pdf_path):
                            # Temizlik
                            for img in downloaded:
                                try: os.remove(img)
                                except: pass
                            print("      🧹 Geçici dosyalar silindi.")
                        return
                    else:
                        print(f"      ❌ Fliphtml5 sayfaları indirilemedi.")
                        return

                # 1. E-Kitap Path Kontrolü (Ata E-Kitap vs.)
                print("      🔍 E-Kitap kaynağı kontrol ediliyor...")
                actual_url = flipbook_url
                ebook_path = await extract_ebook_path(client, flipbook_url)
                if ebook_path:
                    print(f"      ✅ E-Kitap yolu bulundu, güncellenmiş URL kullanılıyor")
                    actual_url = ebook_path
                
                # 2. Direkt PDF Kontrolü
                if actual_url.lower().endswith(".pdf"):
                    print("      📕 Tür: Direkt PDF. İndiriliyor...")
                    try:
                        resp = await client.get(actual_url)
                        if resp.status_code == 200:
                            pdf_path = os.path.join(target_dir, f"{clean_folder_name}.pdf")
                            with open(pdf_path, "wb") as f: f.write(resp.content)
                            print(f"      ✅ İndirme Tamamlandı.")
                            # log_to_manifest(clean_folder_name, flipbook_url, pdf_path, "MANUAL_PDF")  # KORUMA KALDIRIRILDI
                        else: print(f"      ❌ Hata: {resp.status_code}")
                    except Exception as e: print(f"      ❌ Hata: {e}")
                    return

                # 3. Resim Serisi (Flipbook) Olarak Tara (Yayıncı Farketmez)
                images = await download_flipbook_images(client, actual_url, target_dir, clean_folder_name)
                if images:
                    pdf_name = f"{clean_folder_name}.pdf"
                    pdf_path = os.path.join(target_dir, pdf_name)
                    if create_pdf_from_images(images, pdf_path):
                        # Temizlik
                        for img in images:
                            try: os.remove(img)
                            except: pass
                        print("      🧹 Geçici dosyalar silindi.")
                        # log_to_manifest(clean_folder_name, flipbook_url, pdf_path, "FLIPBOOK_PDF")  # KORUMA KALDIRIRILDI
                else:
                    print(f"{C_WARN}⚠️  İndirilemedi. Link bir PDF veya okunabilir kitap değil.{C_RESET}")
            return
            
    else: 
        # --- NORMAL KÜTÜPHANE MODU ---
        prefix = get_next_folder_prefix()
        clean_folder_name = safe_filename(folder_name_raw)
        final_folder_name = f"{prefix}_{clean_folder_name}"
        
        target_dir = os.path.join(DOWNLOADS_ROOT, final_folder_name)
        assets_dir = os.path.join(target_dir, "assets")
        ensure_dirs(target_dir)

        print(f"\n{C_GREEN}🚀 İndirme Başlıyor...{C_RESET}")
        print(f"📂 Hedef: {target_dir}")

        async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}, verify=False, timeout=60, follow_redirects=True) as client:
            for idx, item in enumerate(items):
                print(f"   [{idx+1}/{len(items)}] {item['icon']} {item['type']}: {item['title'][:40]}...")
                try:
                    resp = await client.get(item["url"])
                    file_name_base = safe_filename(item["title"])
                    if not file_name_base or len(file_name_base) < 3:
                         file_name_base = safe_filename(os.path.basename(urlparse(item["url"]).path))

                    final_fname = file_name_base
                    if item["type"] in ["PDF", "EBOOK", "ARCHIVE"]:
                         ext = os.path.splitext(urlparse(item["url"]).path)[1] or ".pdf"
                         if not final_fname.endswith(ext): final_fname += ext
                    else:
                         if not final_fname.endswith(".md"): final_fname += ".md"

                    full_path = os.path.join(target_dir, final_fname)
                    
                    if item["type"] in ["PDF", "EBOOK", "ARCHIVE", "IMAGE"]:
                        with open(full_path, "wb") as f: f.write(resp.content)
                    else:
                        ensure_dirs(assets_dir)
                        soup = BeautifulSoup(resp.content, "html.parser")
                        for t in soup(["script", "style", "nav", "iframe"]): t.decompose()
                        text = soup.get_text("\n", strip=True)
                        with open(full_path, "w", encoding="utf-8") as f:
                            f.write(f"# {item['title']}\nKaynak: {item['url']}\n\n{text}")

                    print(f"      ✅ Kaydedildi: {final_fname}")
                    # log_to_manifest(item["title"], item["url"], full_path, item["type"])  # KORUMA KALDIRIRILDI
                except Exception as e:
                    print(f"      ❌ Hata: {e}")
        
        # Sadece normal indirmede rafineriyi tetikle
        print(f"\n{C_GREEN}✨ İndirme Grubu Tamamlandı. Dosyalar, Ham Kaynaklar ve İşlenmiş Veriler Olarak Arşivleniyor...{C_RESET}")
        try:
            subprocess.run([sys.executable, SETUP_SCRIPT_PATH], check=False)
        except Exception as e:
            print(f"{C_FAIL}Rafineri Hatası: {e}{C_RESET}")
        input("\nListeye dönmek için Enter...")

# --- ANA DÖNGÜ ---
async def main():
    while True:
        clear_screen()
        # v5.6 Modern Arayüz
        print(f"{C_HEADER}" + "="*60)
        print(f"         HERMES VERİ KONSOLU v5.6 (Universal Edition)")
        print(f"="*60 + f"{C_RESET}")
        print("")
        print(f"{C_BLUE}  [1] 🏛️  OTOMATİK KÜTÜPHANE MODU{C_RESET}")
        print(f"      (EsotericArchives arşivini tarar, indirir ve yapay zeka verisine dönüştürür)")
        print("")
        print(f"{C_WARN}  [2] 🌐 EVRENSEL İNDİRİCİ (Manuel Mod){C_RESET}")
        print(f"      (Flipbook, PDF veya Web Linki verin -> Direkt İndirip Arşivlesin)")
        print("")
        print(f"{C_FAIL}  [3] 🚪 ÇIKIŞ{C_RESET}")
        print("-" * 60)
        
        c = input("Seçiminiz [1-3]: ")
        
        if c == '1': 
            url = "https://www.esotericarchives.com/esoteric.htm"
            is_flip_mode = False
        elif c == '2': 
            # DİREKT MANUEL MOD (Sorgusuz)
            url = input("URL Girin: ").strip()
            if not url.startswith("http"): 
                print("Geçersiz URL."); continue
            
            custom_title = input("Dosya İsmi: ").strip()
            if not custom_title: custom_title = "Dosya"
            safe_title = safe_filename(custom_title)
            
            # Direkt İndiriciye Gönder
            await download_worker_full([], safe_title, is_flipbook=True, flipbook_url=url)
            input("\nTamamlandı. Enter...")
            continue
        elif c == '3': sys.exit()
        else: continue
        
        if is_flip_mode:
            title = input("Kitap için bir isim girin: ") or "Flipbook_Document"
            safe_title = safe_filename(title)
            await download_worker_full([], safe_title, is_flipbook=True, flipbook_url=url)
            input("\nFlipbook işlemi tamamlandı. Enter...")
        else:
            while True:
                title, items = await deep_crawl(url, max_depth=1)
                if not items:
                    input("Bulunamadı. Enter...")
                    break
                selected = selection_menu(items, title)
                if not selected: break 
                safe_title = safe_filename(title)
                await download_worker_full(selected, safe_title)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt: pass
