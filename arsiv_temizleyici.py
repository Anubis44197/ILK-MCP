
import os
import shutil
import re

USER_HOME = os.path.expanduser("~")
DESKTOP = os.path.join(USER_HOME, "Desktop")
TARGET_LIB = os.path.join(DESKTOP, "Esoteric_Library")
TARGET_BOOKS = os.path.join(TARGET_LIB, "Books")

SOURCES = [
    os.path.join(DESKTOP, "Esoteric_Library_Downloads"),
    TARGET_BOOKS 
]

def clean_name(s):
    # Sadece harf, rakam ve tire/alt çizgi kalsın.
    # "Agrippa: Book 1!" -> "Agrippa_Book_1"
    if not s: return "Unknown_Book"
    s = str(s).replace(":", " - ").replace("|", " - ")
    s = re.sub(r'[^\w\s-]', '', s)
    return s.strip().replace(" ", "_").replace("__", "_")

def simple_organizer():
    print("🧹 AKILLI ARŞİV DÜZENLEYİCİ (NET İSİMLER)...")
    
    if not os.path.exists(TARGET_BOOKS):
        print("Kütüphane boş veya bulunamadı.")
        return

    # 1. Klasörleri Gez
    for item in os.listdir(TARGET_BOOKS):
        path = os.path.join(TARGET_BOOKS, item)
        
        # Eğer bu bir klasörse ve adı "20231215_..." gibi saçma sapan bir şeyse
        # İçindeki dosyaya bakıp adını düzelteceğiz.
        if os.path.isdir(path):
            files = [f for f in os.listdir(path) if f.endswith(".md") or f.endswith(".pdf") or f.endswith(".html")]
            
            if not files: continue # Boş klasör
            
            # En büyük/önemli dosyayı bul (Genelde ana kitaptır)
            main_file = max(files, key=lambda f: os.path.getsize(os.path.join(path, f)))
            file_name_no_ext = os.path.splitext(main_file)[0]
            
            # Klasör adını dosya adına benzet
            new_folder_name = clean_name(file_name_no_ext)
            
            if new_folder_name.lower() == item.lower(): continue # Zaten doğru
            
            # Çakışma Kontrolü
            new_path = os.path.join(TARGET_BOOKS, new_folder_name)
            counter = 2
            while os.path.exists(new_path):
                new_path = os.path.join(TARGET_BOOKS, f"{new_folder_name}_v{counter}")
                counter += 1
                
            try:
                os.rename(path, new_path)
                print(f"✅ Klasör Adı Düzeltildi: '{item}' -> '{os.path.basename(new_path)}'")
            except Exception as e:
                print(f"❌ Hata: {e}")

    # 2. Başıboş Dosyaları Klasörle
    # (Önceki kodun aynısı ama isim mantığı düzeltildi)
    
    print("\n✨ Düzenleme Bitti.")
    input("Enter...")

if __name__ == "__main__":
    simple_organizer()
