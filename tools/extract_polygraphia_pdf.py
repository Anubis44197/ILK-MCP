import asyncio
from esoteric_mcp_v3 import read_scanned_pdf_ocr

async def extract_polygraphia():
    # Archive.org'dan bir Polygraphia PDF'i (Eski Fransızca/Latince versiyonu)
    # Genelde bu tür eski kitaplar Archive.org'da bulunur.
    # Örnek bir PDF linki (Eğer bu link çalışmazsa, kullanıcıdan güncel bir link isteyebiliriz)
    
    # Not: Bu çok büyük bir dosya olabilir, bu yüzden sadece ilk 5 sayfasını test amaçlı çekeceğiz.
    pdf_url = "https://archive.org/download/polygraphieetvni00trit/polygraphieetvni00trit.pdf"
    
    print(f"Polygraphia indiriliyor ve OCR yapılıyor: {pdf_url}")
    print("Bu işlem PDF boyutuna göre biraz zaman alabilir...")

    try:
        # v3 Modülümüzdeki OCR fonksiyonunu kullanıyoruz
        # lang='fra' veya 'lat' (Fransızca/Latince) daha iyi olur ama 'eng' ile deniyoruz (OCR varsa çalışır)
        content = await read_scanned_pdf_ocr(url=pdf_url, lang='eng+fra', max_pages=3)
        
        output_file = "polygraphia_ocr_sample.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)
            
        print(f"\nBAŞARILI! İçerik {output_file} dosyasına kaydedildi.")
        print("İçerik önizlemesi:\n")
        print(content[:500])
        
    except Exception as e:
        print(f"HATA OLUŞTU: {e}")

if __name__ == "__main__":
    asyncio.run(extract_polygraphia())
