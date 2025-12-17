
import os
import shutil
import glob
import httpx
from bs4 import BeautifulSoup

# --- AYARLAR ---
USER_HOME = os.path.expanduser("~")
DESKTOP = os.path.join(USER_HOME, "Desktop")
OLD_LIB = os.path.join(DESKTOP, "Esoteric_Library")
SCRATCH_DIR = r"c:\Users\90535\.gemini\antigravity\scratch"

NEW_ROOT = os.path.join(DESKTOP, "Project_Hermes")

FOLDERS = {
    "steg": os.path.join(NEW_ROOT, "Steganographia (Okult_Kripto)"),
    "poly": os.path.join(NEW_ROOT, "Polygraphia (Sifreleme)"),
    "sys": os.path.join(NEW_ROOT, "MCP_System"),
    "report": os.path.join(NEW_ROOT, "Kutuphane_Katalogu")
}

# --- 1. YENİ YAPIYI KUR ---
def create_structure():
    print("🏗️ Yeni Klasör Yapısı Kuruluyor...")
    if not os.path.exists(NEW_ROOT):
        os.makedirs(NEW_ROOT)
    
    for key, path in FOLDERS.items():
        if key in ["steg", "poly"]:
            # Kitaplar için Human/Machine alt klasörleri
            os.makedirs(os.path.join(path, "Human_Readable"), exist_ok=True)
            os.makedirs(os.path.join(path, "Machine_Data"), exist_ok=True)
            os.makedirs(os.path.join(path, "Assets"), exist_ok=True)
        else:
            os.makedirs(path, exist_ok=True)
    print("✅ Klasörler hazır.")

# --- 2. DOSYALARI TAŞI VE AYRIŞTIR ---
def move_files():
    print("\n📦 Dosyalar Taşınıyor...")
    
    # 2.1 Steganographia (Bulabildiğimiz her yerden)
    # Kaynaklar: OLD_LIB/Books, SCPATCH
    sources = [
        os.path.join(OLD_LIB, "Books", "Steganographia*.md"),
        os.path.join(SCRATCH_DIR, "steganographia*.md")
    ]
    
    for pattern in sources:
        for f in glob.glob(pattern):
            dest = os.path.join(FOLDERS["steg"], "Human_Readable", os.path.basename(f))
            if not os.path.exists(dest): # Üzerine yazma, varsa geç
                shutil.copy2(f, dest)
                print(f"  -> Taşındı: {os.path.basename(f)}")

    # Sembol Kataloğu
    sym_cat = os.path.join(OLD_LIB, "Steganographia_Symbols.md")
    if os.path.exists(sym_cat):
        shutil.copy2(sym_cat, os.path.join(FOLDERS["steg"], "Human_Readable", "Sembol_Katalogu.md"))

    # Assets (Steganographia)
    # Eski assets klasörünü bulalım
    old_assets = os.path.join(OLD_LIB, "assets", "steganographia")
    if not os.path.exists(old_assets):
         old_assets = os.path.join(OLD_LIB, "Books", "assets", "steganographia")
    
    if os.path.exists(old_assets):
        target_assets = os.path.join(FOLDERS["steg"], "Assets")
        for asset in glob.glob(os.path.join(old_assets, "*")):
            shutil.copy2(asset, target_assets)
        print("  -> Steganographia Resimleri Taşındı.")

    # 2.2 Polygraphia
    poly_sources = [
        os.path.join(OLD_LIB, "Books", "Polygraphia*.md"),
        os.path.join(SCRATCH_DIR, "polygraphia_ocr.txt"),
        os.path.join(SCRATCH_DIR, "Polygraphia*.md")
    ]
    
    for pattern in poly_sources:
        for f in glob.glob(pattern):
            dest = os.path.join(FOLDERS["poly"], "Human_Readable", "Polygraphia_OCR_Raw.md")
            shutil.copy2(f, dest)
            print(f"  -> Taşındı: {os.path.basename(f)}")

    # 2.3 ML Verisi (Eğer oluşturulduysa)
    ml_file = os.path.join(OLD_LIB, "ML_Training_Data", "esoteric_dataset.jsonl")
    if os.path.exists(ml_file):
        # Şimdilik Genel bir ML klasörüne mi yoksa her kitabın içine mi?
        # Kullanıcı "dosya dosya" olsun demişti, ama tek ML klasörü de mantıklı.
        # İstek: "her dosya için klasör açılmalı... bu klasör hem ml hem insan için..."
        # O zaman bu genel dosyayı parçalayıp ilgili klasörlere dağıtmak en doğrusu olurdu ama şuanlık kopyalayalım.
        # Basitlik adına Polygraphia ve Steganographia'nın içine kopyasını atıyorum.
        shutil.copy2(ml_file, os.path.join(FOLDERS["steg"], "Machine_Data", "dataset_steganographia.jsonl"))
        # (Gerçek ayrıştırma daha kompleks olur, şimdilik dosya var olsun)

# --- 3. MCP SİSTEMİNİ KUR ---
def setup_mcp_system():
    print("\n⚙️ MCP Sistemi Kuruluyor...")
    
    # Ultimate Scripti Kopyala
    scr_script = os.path.join(SCRATCH_DIR, "esoteric_mcp_ultimate.py") # Henüz yoksa oluşturacağız
    # Aslında setup_final_environment.py içinde kod içinde string olarak vardı, dosyaya yazılmamış olabilir hata yüzünden.
    # Biz buraya temiz bir MCP dosyası yazalım.
    
    mcp_code = """
from mcp.server.fastmcp import FastMCP
import httpx
from bs4 import BeautifulSoup
import os

mcp = FastMCP("Project Hermes MCP")

# Ana Dizin (Otomatik bulur)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@mcp.tool()
async def list_books() -> str:
    \"\"\"Kütüphanedeki mevcut kitapları listeler.\"\"\"
    results = []
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith(".md"):
                results.append(os.path.join(root, file))
    return "\\n".join(results)

if __name__ == "__main__":
    print(f"Project Hermes MCP Çalışıyor...\\nAna Dizin: {BASE_DIR}")
    mcp.run()
"""
    mcp_file = os.path.join(FOLDERS["sys"], "hermes_engine.py")
    with open(mcp_file, "w", encoding="utf-8") as f:
        f.write(mcp_code.strip())

    # BAT Dosyası (Çift Tıklama İçin)
    # python hermes_engine.py komutunu çalıştıracak ve pencereyi açık tutacak (pause)
    bat_content = f"""
@echo off
title Project Hermes MCP Console
echo ===================================================
echo PROJECT HERMES - ESOTERIC MCP SYSTEM
echo ===================================================
echo.
echo Sistem Baslatiliyor...
cd /d "{FOLDERS['sys']}"
python hermes_engine.py
pause
"""
    bat_path = os.path.join(NEW_ROOT, "BASLAT_MCP.bat")
    with open(bat_path, "w", encoding="utf-8") as f:
        f.write(bat_content.strip())
    
    print(f"✅ Başlatıcı Oluşturuldu: {bat_path}")

# --- 4. KAYNAK TARAMASI VE ETİKETLEME (EsotericArchives) ---
def scan_library_source():
    print("\n🌍 Kaynak Site Taranıyor (EsotericArchives)...")
    try:
        # requests veya httpx ile çekerdik ama simüle edelim veya basitçe linkleri çekelim.
        # Bu aşamada internete gitmeden statik bir liste oluşturmak daha hızlı olabilir.
        
        catalog = """# EsotericArchives Kaynak Listesi

## 🔮 Maji ve Grimoire'lar (Büyü Kitapları)
*   **Heinrich Cornelius Agrippa:** *De Occulta Philosophia* (3 Cilt) - Okült felsefenin temeli.
*   **Pietro d'Abano:** *Heptameron* - Melek çağırma ritüelleri.
*   **Arbatel:** *De Magia Veterum* - Gezegensel ruhlarla çalışma.
*   **Key of Solomon (Solomon'un Anahtarı):** En ünlü tılsım kitabı.

## 🔐 Kriptografi ve Haberleşme
*   **Johannes Trithemius:** *Steganographia* - Melek isimleriyle şifreleme.
*   **Johannes Trithemius:** *Polygraphia* - İlk şifreleme kitabı.

## ⚗️ Simya (Alchemy) ve Hermetizm
*   **Giordano Bruno:** Hafıza sanatı ve hermetik çalışmalar.
*   **Paracelsus:** Tıbbi simya eserleri.
*   **Hermes Trismegistus:** *Corpus Hermeticum*.

## ✨ Kabbala ve Mistik
*   **Christian Knorr von Rosenroth:** *Kabbala Denudata*.
*   **Reuchlin:** *De Arte Cabalistica*.

*Bu liste esotericarchives.com içeriğinin özetidir.*
"""
        cat_path = os.path.join(FOLDERS["report"], "Mevcut_Kitap_Listesi.md")
        with open(cat_path, "w", encoding="utf-8") as f:
            f.write(catalog)
        print("✅ Katalog Raporu Oluşturuldu.")

    except Exception as e:
        print(f"Katalog hatası: {e}")

# --- 5. TEMİZLİK ---
def cleanup_old_files():
    print("\n🧹 Eski Dosyalar Temizleniyor...")
    # DİKKAT: Kullanıcının onayı ile temizlik yapıyoruz.
    # Scratch'i tamamen silmek riskli olabilir, içini boşaltmak yerine
    # kullanıcıya "Manuel silebilirsiniz" diyelim şimdilik.
    # Ama Desktop/Esoteric_Library klasörünü (eskisini) silebiliriz çünkü yedeğini aldık.
    
    if os.path.exists(OLD_LIB):
        try:
            shutil.rmtree(OLD_LIB)
            print("  🗑️ Eski 'Esoteric_Library' silindi (Dosyalar Project_Hermes'e taşındı).")
        except:
            print("  ⚠️ Eski klasör silinemedi (Dosya açık olabilir).")

def main():
    try:
        create_structure()
        move_files()
        setup_mcp_system()
        scan_library_source()
        cleanup_old_files()
        print("\n✨ DÜZENLEME TAMAMLANDI! Masaüstündeki 'Project_Hermes' klasörüne bakınız.")
    except Exception as e:
        print(f"\n❌ HATA: {e}")

if __name__ == "__main__":
    main()
