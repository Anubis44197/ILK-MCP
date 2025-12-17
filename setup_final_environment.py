
import os
import shutil
import base64
import json
import glob
import re
import datetime
import subprocess
import sys
from pathlib import Path
import hashlib

# --- GEREKLİ KÜTÜPHANELER ---
try:
    from bs4 import BeautifulSoup
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
    import pdfminer.high_level
except ImportError:
    print("⚠️  Eksik kütüphaneler var! Lütfen: pip install -r requirements.txt")
    print("⚠️  OCR için sisteminizde Tesseract ve Poppler kurulu olmalıdır.")

# --- AYARLAR ---
USER_HOME = os.path.expanduser("~")
BASE_LIB_PATH = os.path.join(USER_HOME, "Desktop", "Esoteric_Library")
LIBRARY_ROOT = os.path.join(BASE_LIB_PATH, "Kutuphane") # TÜRKÇE KLASÖR
QUARANTINE_PATH = os.path.join(BASE_LIB_PATH, "Karantina") # TÜRKÇE KLASÖR

MANIFEST_PATH = os.path.join(BASE_LIB_PATH, "library_manifest.json")

# --- YARDIMCI FONSİYONLAR ---
def ensure_dirs(path):
    if not os.path.exists(path): os.makedirs(path)

def load_manifest():
    if os.path.exists(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

def update_manifest(filename, status, dest_path=None, details=None):
    manifest = load_manifest()
    manifest[filename] = {
        "status": status,
        "processed_at": str(datetime.datetime.now()),
        "destination": dest_path,
        "details": details or {}
    }
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=4)

# --- KALİTE KONTROL ---
# --- KALİTE KONTROL (QUALITY INSPECTOR v2.0) ---
def check_quality(text):
    if not text: return False, "Boş İçerik"
    
    # 1. Uzunluk Kontrolü (Çok kısa metinler genellikle başlık veya sayfa nosudur)
    if len(text) < 100: return False, "Çok Kısa (<100 karakter)"

    # Metni analiz için hazırla
    text_no_space = text.replace(" ", "").replace("\n", "").strip()
    if len(text_no_space) == 0: return False, "Sadece Boşluk/Görünmez Karakter"

    # 2. Temel Gürültü Oranı (Sembol vs Harf)
    # Sadece harfleri ve sayıları say
    clean_chars = re.sub(r'[^a-zA-Z0-9öçşıiğüÖÇŞİĞÜ]', '', text)
    ratio = len(clean_chars) / len(text_no_space)
    
    # Eğer karakterlerin %50'sinden fazlası sembolse (örn: #, *, |, ----) reddet.
    if ratio < 0.5: 
        return False, f"Yüksek Gürültü Oranı (%{int((1-ratio)*100)} Sembol)"

    # 3. Kelime Analizi (Boşluksuz uzun yazılar veya tek harfler)
    words = text.split()
    if not words: return False, "Kelime Bulunamadı"
    
    avg_len = sum(len(w) for w in words) / len(words)
    
    # Ortalama kelime uzunluğu çok fazlaysa (OCR boşlukları kaçırdıysa)
    if avg_len > 30: return False, "Anlamsız Uzun Bloklar (Boşluk Hatası)"
    # Ortalama kelime uzunluğu çok azsa (t e k t e k h a r f l e r)
    if avg_len < 2: return False, "Aşırı Parçalı/Kısa Metin"

    # 4. Fonetik Kontrol (Sesli Harf Oranı)
    # Türkçe veya İngilizce anlamlı bir metinde mutlaka sesli harf olmalı.
    vowels = "aeiouöüıiAEIOUÖÜİI"
    vowel_count = sum(1 for c in text if c in vowels)
    vowel_ratio = vowel_count / len(text_no_space)
    
    if vowel_ratio < 0.15: # %15'ten az sesli harf varsa (örn: "bcdfghjkl mnprst")
        return False, "Sesli Harf Yetersizliği (Okunamaz İçerik)"

    return True, "Onaylandı"

# --- OCR VE METİN İŞLEME ---
def extract_text_from_pdf(pdf_path):
    text = ""
    print(f"      👀 PDF Taranıyor (OCR)... {os.path.basename(pdf_path)}")
    
    try:
        text = pdfminer.high_level.extract_text(pdf_path)
        if text and len(text) > 100:
            return text
    except: pass

    try:
        images = convert_from_path(pdf_path)
        ocr_text = []
        for i, img in enumerate(images):
            if i % 5 == 0: print(f"         Sayfa {i+1}/{len(images)} işleniyor...")
            page_text = pytesseract.image_to_string(img, lang='eng+tur')
            ocr_text.append(page_text)
        return "\n".join(ocr_text)
    except Exception as e:
        print(f"         ❌ OCR Hatası: {e}")
        return ""

def clean_text(text):
    lines = text.splitlines()
    cleaned = []
    headers_footers = ["back to top", "menu", "home", "contents", "index", "page", "bölüm"]
    
    for line in lines:
        s = line.strip()
        if not s: continue
        if len(s) < 3: continue 
        if any(hf in s.lower() for hf in headers_footers) and len(s) < 20: continue
        cleaned.append(s)
    return "\n".join(cleaned)

def chunk_text(text, chunk_size=3000, overlap=500):
    chunks = []
    current_chunk = []
    current_len = 0
    
    paragraphs = text.split("\n\n")
    if len(paragraphs) < 2: paragraphs = text.split("\n") 

    for p in paragraphs:
        p = p.strip()
        if not p: continue
        
        if len(p) > chunk_size:
            sub_parts = re.split(r'(?<=[.!?])\s+', p)
            for sub in sub_parts:
                if current_len + len(sub) > chunk_size and current_chunk:
                    full_chunk = "\n\n".join(current_chunk)
                    chunks.append(full_chunk)
                    overlap_text = full_chunk[-overlap:] if len(full_chunk) > overlap else full_chunk
                    current_chunk = [overlap_text, sub]
                    current_len = len(overlap_text) + len(sub)
                else:
                    current_chunk.append(sub)
                    current_len += len(sub)
        else:
            if current_len + len(p) > chunk_size and current_chunk:
                full_chunk = "\n\n".join(current_chunk)
                chunks.append(full_chunk)
                overlap_text = full_chunk[-overlap:] if len(full_chunk) > overlap else full_chunk
                current_chunk = [overlap_text, p]
                current_len = len(overlap_text) + len(p)
            else:
                current_chunk.append(p)
                current_len += len(p)

    if current_chunk: chunks.append("\n\n".join(current_chunk))
    return chunks

# --- DOSYA İŞLEME MOTORU ---
def process_file_content(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    content = ""
    
    try:
        if ext == ".md" or ext == ".txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        elif ext in [".html", ".htm"]:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
                for t in soup(["script", "style", "nav", "footer", "form"]): t.decompose()
                content = soup.get_text("\n")
        elif ext == ".pdf":
            content = extract_text_from_pdf(file_path)
        
        return clean_text(content), "OK"
    except Exception as e:
        return None, str(e)

def process_library():
    print("\n🏭 VERİ RAFİNERİSİ ÇALIŞIYOR (YEŞİL ENERJİ MODU)...")
    ensure_dirs(LIBRARY_ROOT)
    ensure_dirs(QUARANTINE_PATH)
    
    # Manifest'i yükle
    manifest = load_manifest()
    
    if not os.path.exists(LIBRARY_ROOT):
        print("📭 Kütüphane henüz boş.")
        return

    # Kütüphanedeki tüm dosyaları bul (Recursive)
    book_folders = [f.path for f in os.scandir(LIBRARY_ROOT) if f.is_dir()]
    
    processed_count = 0
    
    for book_folder in book_folders:
        folder_name = os.path.basename(book_folder)
        
        # Bu klasördeki işlenmemiş dosyaları bul
        # Okunabilir, Veri_Seti, assets hariç diğerlerine bak
        files_to_process = []
        for root, dirs, files in os.walk(book_folder):
            if "Okunabilir" in root or "Veri_Seti" in root or "assets" in root:
                continue
            for f in files:
                # Desteklenen uzantılar
                if f.lower().endswith((".pdf", ".html", ".htm", ".md", ".txt")) and f != "README.md":
                     files_to_process.append(os.path.join(root, f))
        
        for file_path in files_to_process:
            filename = os.path.basename(file_path)
            
            # ⚠️ KORUMA KALDIRIRILDI - İstediğin kadar indirebilirsin
            # if filename in manifest and manifest[filename].get("status") == "PROCESSED":
            #     continue

            print(f"\n⚙️  Rafineri İşliyor: {filename}")
            
            # 1. İÇERİĞİ ÇIKAR
            content, status = process_file_content(file_path)
            
            # 2. KALİTE KONTROL
            valid, msg = False, status
            if content:
                valid, msg = check_quality(content)
            
            if not valid:
                print(f"      ⛔ REDDEDİLDİ: {msg}")
                # Karantinaya taşı
                try:
                    shutil.move(file_path, os.path.join(QUARANTINE_PATH, filename))
                except: pass
                # update_manifest(filename, "QUARANTINED", details={"reason": msg})  # KORUMA KALDIRIRILDI
                continue

            # 3. YAZMA VE DÜZENLEME
            # Hedef: Türkçe Klasörler
            human_dir = os.path.join(book_folder, "Okunabilir")
            machine_dir = os.path.join(book_folder, "Veri_Seti")
            
            ensure_dirs(human_dir)
            ensure_dirs(machine_dir)
            
            # Human Readable (Okunabilir)
            chunks = chunk_text(content, 3000, overlap=500)
            for i, chunk in enumerate(chunks):
                fname = f"{folder_name}_Bolum_{i+1:02d}.md"
                with open(os.path.join(human_dir, fname), "w", encoding="utf-8") as f:
                    f.write(f"# {folder_name} - Bölüm {i+1}\n\n{chunk}")
            
            # Machine Data (Veri_Seti)
            jsonl_path = os.path.join(machine_dir, "dataset.jsonl")
            with open(jsonl_path, "a", encoding="utf-8") as f:
                for i, chunk in enumerate(chunks):
                    content_hash = hashlib.md5(chunk.encode('utf-8')).hexdigest()
                    record = {
                        "id": f"{filename}_{i}_{content_hash[:8]}",
                        "source_id": filename,
                        "text": chunk,
                        "metadata": {
                            "title": folder_name, 
                            "part": i+1, 
                            "original_file": filename,
                            "content_hash": content_hash,
                            "timestamp": str(datetime.datetime.now())
                        }
                    }
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
            
            print(f"      ✅ İŞLENDİ: {len(chunks)} Parça.")
            
            # 4. ORİJİNAL DOSYAYI SAKLA (Hareket Ettirme, Olduğu Yerde Kalsın)
            # Manifest'e işlendi olarak işaretle, böylece bir daha işlemeyecek.
            # Ancak görsel düzen için isterseniz başına [Orijinal] ekleyebiliriz? 
            # Kullanıcı "Direkt burada" dedi, olduğu gibi bırakıyoruz.
            
            # update_manifest(filename, "PROCESSED", dest_path=book_folder)  # KORUMA KALDIRIRILDI
            processed_count += 1

    if processed_count == 0:
        print("💤 İşlenecek yeni dosya bulunamadı.")
    else:
        print(f"\n✨ {processed_count} adet yeni kaynak düzenlendi ve arşivlendi.")

if __name__ == "__main__":
    process_library()
