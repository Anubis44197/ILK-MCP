
import os
import re
import glob

# Ayarlar
BASE_DIR = r"c:\Users\90535\.gemini\antigravity\scratch"
ASSETS_DIR = "assets/steganographia"
OUTPUT_FILE = os.path.join(BASE_DIR, "steganographia_symbols.md")

MARKDOWN_FILES = [
    "steganographia_v3_bk1.md",
    "steganographia_v3_bk2.md",
    "steganographia_v3_bk3.md"
]

def create_catalog():
    catalog_content = ["# Steganographia Sembol ve Çizim Kataloğu\n"]
    catalog_content.append(f"Oluşturulma Tarihi: {os.path.basename(OUTPUT_FILE)}\n")
    catalog_content.append("Bu belge, Steganographia kitaplarındaki görselleri, orijinal bağlamları ve yerel dosya yollarıyla listeler.\n")

    total_images = 0

    for md_file in MARKDOWN_FILES:
        full_path = os.path.join(BASE_DIR, md_file)
        if not os.path.exists(full_path):
            continue

        book_name = md_file.replace("steganographia_v3_", "").replace(".md", "").upper()
        catalog_content.append(f"\n## 📚 {book_name}\n")
        
        with open(full_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            # Resim bul: ![Alt](Url)
            match = re.search(r'!\[(.*?)\]\((.*?)\)', line)
            if match:
                alt_text = match.group(1)
                url = match.group(2)
                
                # Dosya adını bul
                filename = url.split("/")[-1]
                # Temizle (indirirken yaptığımız gibi)
                clean_filename = re.sub(r'[^\w\-\.]', '_', filename)
                if not clean_filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                    clean_filename += ".jpg"
                
                local_path = f"{ASSETS_DIR}/{clean_filename}"
                
                # Context (Önceki ve sonraki dolu satırlar)
                prev_ctx = ""
                next_ctx = ""
                
                # Geriye doğru bak
                for k in range(1, 4):
                    if i - k >= 0 and lines[i-k].strip() and "![" not in lines[i-k]:
                        prev_ctx = lines[i-k].strip()
                        break
                
                # İleriye doğru bak
                for k in range(1, 4):
                    if i + k < len(lines) and lines[i+k].strip() and "![" not in lines[i+k]:
                        next_ctx = lines[i+k].strip()
                        break
                
                total_images += 1
                
                entry = f"""
### 🖼️ Sembol {total_images}: {clean_filename}
*   **Orijinal Alt Metin:** {alt_text}
*   **Dosya Konumu:** `antigravity/scratch/{local_path}`
*   **Bağlam (Öncesi):** _{prev_ctx}_
*   **Bağlam (Sonrası):** _{next_ctx}_

![{alt_text}]({local_path})

---
"""
                catalog_content.append(entry)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(catalog_content))

    print(f"✅ Katalog oluşturuldu: {OUTPUT_FILE}")
    print(f"Toplam {total_images} görsel işlendi.")

if __name__ == "__main__":
    create_catalog()
