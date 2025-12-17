
import os
import sys
import json
import httpx
import asyncio
from pdf2image import convert_from_path
import pytesseract
from tqdm import tqdm

# --- AYARLAR ---
BASE_DIR = r"c:\Users\90535\.gemini\antigravity\scratch"
DESKTOP_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "Esoteric_Library")

# PDF Scratch'te kalabilir (Tekrar indirmemek için) veya oraya da taşınabilir
PDF_FILENAME = "polygraphia.pdf"
PDF_PATH = os.path.join(BASE_DIR, PDF_FILENAME) 

# State dosyasını da Scratch'te tutalım ki karışmasın, kullanıcı sonucu görsün sadece
STATE_FILE = os.path.join(BASE_DIR, "polygraphia_state.json")

# ÇIKTI MASAÜSTÜNE
OUTPUT_MD = os.path.join(DESKTOP_DIR, "Polygraphia_Combined_OCR.md")

# Assets Masaüstüne
ASSETS_DIR = os.path.join(DESKTOP_DIR, "assets", "polygraphia")

PDF_URL = "https://archive.org/download/polygraphieetvni00trit/polygraphieetvni00trit.pdf"

# Tesseract ve Poppler Yolları
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
POPPLER_PATH = r'C:\Users\90535\poppler\Library\bin'

# Klasör Kontrolü
if not os.path.exists(ASSETS_DIR):
    os.makedirs(ASSETS_DIR)

async def download_pdf():
    if os.path.exists(PDF_PATH):
        print(f"✅ PDF zaten mevcut: {PDF_PATH}")
        return

    print("⬇️ PDF İndiriliyor (Bu işlem biraz sürebilir)...")
    async with httpx.AsyncClient(verify=False, follow_redirects=True, timeout=None) as client:
        async with client.stream("GET", PDF_URL) as response:
            total = int(response.headers.get("Content-Length", 0))
            
            with open(PDF_PATH, "wb") as f, tqdm(
                desc=PDF_FILENAME,
                total=total,
                unit="iB",
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                async for chunk in response.aiter_bytes():
                    size = f.write(chunk)
                    bar.update(size)
    print("✅ İndirme tamamlandı.")

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"last_page": 0}

def save_state(page_num):
    with open(STATE_FILE, "w") as f:
        json.dump({"last_page": page_num}, f)

def process_ocr_batch(start_page, batch_size=10):
    print(f"\n🔄 OCR İşlemi Başlıyor: Sayfa {start_page+1} - {start_page+batch_size}")
    
    try:
        # Sayfaları resme çevir
        # userpassword='' encrypted pdf hatası almamak için gerekebilir, ama archive.org pdf'leri genelde açıktır.
        images = convert_from_path(
            PDF_PATH, 
            first_page=start_page+1, 
            last_page=start_page+batch_size, 
            poppler_path=POPPLER_PATH,
            dpi=300
        )
    except Exception as e:
        print(f"❌ PDF Okuma Hatası: {e}")
        return False

    if not images:
        print("Bitti! İşlenecek sayfa kalmadı.")
        return False

    batch_text = ""
    for i, img in enumerate(images):
        current_page = start_page + i + 1
        print(f"   > Sayfa {current_page} taranıyor...")
        
        # OCR
        text = pytesseract.image_to_string(img, lang='eng+lat') # Latince desteği varsa iyi olur
        
        # Resmi Kaydet (İsteğe bağlı, her sayfayı kaydetmeyelim, sadece dolu olanları?)
        # Şimdilik hepsini 'preview' olarak kaydedelim, sonra sileriz veya seçeriz.
        # img_filename = f"page_{current_page:03d}.jpg"
        # img.save(os.path.join(ASSETS_DIR, img_filename), "JPEG")

        batch_text += f"\n\n## Sayfa {current_page}\n\n{text}\n"

    # Dosyaya ekle
    with open(OUTPUT_MD, "a", encoding="utf-8") as f:
        f.write(batch_text)

    save_state(start_page + len(images))
    return True

async def main():
    await download_pdf()
    
    state = load_state()
    current_page = state["last_page"]
    
    # Döngü içinde batch batch işle
    while True:
        try:
            success = process_ocr_batch(current_page, batch_size=20)
            if not success:
                break
            current_page += 20
            
            # Aşırı yüklenmeyi önlemek için küçük bir bekleme veya kullanıcı müdahalesi için durma?
            # Şimdilik 100 sayfada bir duralım ki kontrol edelim.
            # if current_page >= 100 and current_page % 100 == 0:
            #     print("⚠️ 100 sayfa işlendi. Güvenlik molası.")
            #     break
            pass # Sınırsız devam etsin
                
        except KeyboardInterrupt:
            print("\n🛑 İşlem kullanıcı tarafından durduruldu.")
            break
        except Exception as e:
            print(f"Beklenmeyen Hata: {e}")
            break

if __name__ == "__main__":
    asyncio.run(main())
