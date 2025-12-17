#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import os
import sys
import httpx
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from PIL import Image

# --- KONFİGÜRASYON ---
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# --- HELPERS ---
def ensure_dirs(path):
    if not os.path.exists(path): 
        os.makedirs(path)

def safe_filename(s):
    s = str(s).strip().replace(" ", "_")
    return "".join([c for c in s if c.isalnum() or c in "._-"])

# --- EXTRACT EBOOK PATH ---
async def extract_ebook_path(client, url):
    """Ata E-Kitap gibi sitelerden data-ebook-path çıkar"""
    try:
        resp = await client.get(url)
        if resp.status_code != 200:
            return None
        
        soup = BeautifulSoup(resp.content, "html.parser")
        
        # Ata E-Kitap pattern
        link = soup.find("a", {"data-ebook-path": True})
        if link:
            path = link.get("data-ebook-path")
            if path:
                print(f"      ✅ E-Kitap path bulundu: {path[:80]}")
                parsed = urlparse(url)
                base = f"{parsed.scheme}://{parsed.netloc}"
                full_url = urljoin(base, path)
                return full_url
        
        return None
    except Exception as e:
        print(f"      ⚠️  Path extraction error: {e}")
        return None

# --- PATTERN DETECTION ---
async def download_flipbook_images(client, base_url, target_dir, title):
    print(f"\n      📚 Flipbook Modu: Resim serisi taranıyor...")
    print(f"         URL: {base_url[:80]}")

    found_images = []
    page_num = 1
    consecutive_errors = 0
    
    # URL cleanup
    if base_url.endswith("index.html") or base_url.endswith(".php"):
        base_url = base_url.rsplit('/', 1)[0]
    
    if not base_url.endswith('/'): 
        base_url += '/'
    
    # Pattern detection
    patterns = ["files/mobile/", "files/large/", "mobile/", "files/shot/", "pages/", "", "files/page/"]
    valid_pattern = None
    
    print(f"         🔍 Desen aranıyor...")
    for pat in patterns:
        test_url = urljoin(base_url, f"{pat}1.jpg")
        try:
            r = await client.get(test_url)
            if r.status_code == 200:
                print(f"         ✅ Desen bulundu: {pat}")
                valid_pattern = pat
                break
        except: 
            pass
        
    if not valid_pattern:
        print(f"         ❌ Otomatik desen bulunamadı.")
        return []

    print(f"         📥 Sayfalar indiriliyor...")
    
    while True:
        img_url = urljoin(base_url, f"{valid_pattern}{page_num}.jpg")
        try:
            resp = await client.get(img_url, timeout=10)
            if resp.status_code != 200:
                img_url = urljoin(base_url, f"{valid_pattern}{page_num}.png")
                resp = await client.get(img_url, timeout=10)
            
            if resp.status_code == 200:
                fname = f"{page_num:04d}.jpg" 
                fpath = os.path.join(target_dir, fname)
                with open(fpath, "wb") as f: 
                    f.write(resp.content)
                found_images.append(fpath)
                print(f"            Sayfa {page_num} - {len(resp.content)} bytes OK", end="\r")
                page_num += 1
                consecutive_errors = 0
            else:
                consecutive_errors += 1
                if consecutive_errors > 5: 
                    break
        except Exception as e:
            break
             
    print(f"\n         ✅ Toplam {len(found_images)} sayfa indirildi.     ")
    return found_images

# --- PDF CREATION ---
def create_pdf_from_images(image_paths, output_pdf_path):
    if not image_paths: 
        return False
    print(f"         📚 PDF oluşturuluyor... ({len(image_paths)} sayfa)")
    try:
        images = []
        for p in image_paths:
            img = Image.open(p)
            if img.mode != 'RGB': 
                img = img.convert('RGB')
            images.append(img)
            
        if images:
            images[0].save(output_pdf_path, "PDF", resolution=100.0, save_all=True, append_images=images[1:])
            print(f"         ✨ PDF hazırlandı: {os.path.basename(output_pdf_path)}")
            return True
    except Exception as e:
        print(f"         ❌ PDF hatası: {e}")
        return False
    return False

# --- MAIN TEST ---
async def test_download():
    url = "https://www.ataekitap.com/kitaplar/7-sinif-ben-korkmam-fen-bilimleri-soru-bankasi"
    folder_name = "e kitap test"
    
    target_dir = os.path.join(".", safe_filename(folder_name))
    ensure_dirs(target_dir)
    
    print("\n" + "="*80)
    print("🚀 MANUEL İNDİRME BAŞLATILIYOR")
    print("="*80)
    print(f"📎 URL: {url}")
    print(f"📂 Klasör: {os.path.abspath(target_dir)}")
    
    async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}, verify=False, timeout=60, follow_redirects=True) as client:
        # 0. E-Kitap Path Kontrolü
        print("\n1️⃣  E-Kitap kaynağı kontrol ediliyor...")
        actual_url = url
        ebook_path = await extract_ebook_path(client, url)
        if ebook_path:
            print(f"      ✅ E-Kitap yolu bulundu, güncellenmiş URL kullanılıyor")
            actual_url = ebook_path
        else:
            print(f"      ℹ️  E-Kitap yolu bulunamadı, orijinal URL kullanılıyor")
        
        # 2. Flipbook indirme
        print("\n2️⃣  Flipbook indirmesi başlıyor...")
        images = await download_flipbook_images(client, actual_url, target_dir, folder_name)
        
        if images:
            print(f"\n3️⃣  PDF oluşturuluyor...")
            pdf_name = f"{safe_filename(folder_name)}.pdf"
            pdf_path = os.path.join(target_dir, pdf_name)
            if create_pdf_from_images(images, pdf_path):
                # Cleanup
                for img in images:
                    try: 
                        os.remove(img)
                    except: 
                        pass
                print(f"         🧹 Geçici dosyalar silindi")
                print(f"\n✅ BAŞARILI!")
                print(f"📂 Dosya Yolu: {os.path.abspath(pdf_path)}")
            else:
                print(f"\n❌ PDF oluşturulamadı")
        else:
            print(f"\n❌ Hiçbir görüntü indirilemedi")

# --- RUN ---
if __name__ == "__main__":
    asyncio.run(test_download())
