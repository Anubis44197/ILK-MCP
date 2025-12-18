# 📜 Project Hermes: Esoteric Data Refinery & Automation

Bu proje, internet üzerindeki herhangi bir kaynaktan (Web, PDF, E-Kitap, Flipbook) bilgi toplamak, bu bilgiyi temizlemek (Rafine Etmek) ve Yapay Zeka (LLM) eğitimine uygun, yüksek kaliteli veri setlerine dönüştürmek için tasarlanmış tam otomatik bir **Veri Mühendisliği Boru Hattıdır (Data Engineering Pipeline)**.

**Güncel Sürüm:** v6.0 (2-Platform Sistem: Fliphtml5 + Ata E-Kitap)

---

## 📋 İçindekiler

1. [Sistem Mimarisi](#sistem-mimarisi)
2. [Desteklenen Formatlar](#desteklenen-formatlar)
3. [Özellikler](#özellikler)
4. [Kurulum](#kurulum)
5. [Kullanım](#kullanım)
6. [Teknik Detaylar](#teknik-detaylar)
7. [Sürüm Tarihi](#sürüm-tarihi)

---

## 🏗️ Sistem Mimarisi

```
INPUT (İnternet Kaynakları)
  ├─ Fliphtml5 Kütüphaneleri (fliphtml5.com) ✅
  ├─ Ata E-Kitap (ataekitap.com) ✅
  ├─ Doğrudan PDF Dosyaları
  └─ Genel Flipbook Platformları

        ↓ [FORMAT DETECTION - 3-Seviye Kaskad]

DOWNLOADER (indir.py)
  ├─ Fliphtml5: WebP → PDF Dönüştürme
  ├─ Ata E-Kitap: HTML Extract + PDF Bundle
  ├─ PDF Direct: İndirme + Validasyon
  └─ Generic: İmaj Seri → PDF

        ↓ [CLEANUP - arsiv_temizleyici.py]

PROCESSOR
  ├─ OCR (PaddleOCR)
  ├─ Metin Normalizasyonu
  ├─ Dil Algılama & Transliterasyonu
  └─ Metadata Çıkarımı

        ↓ [QUALITY CONTROL]

OUTPUT (LLM-Ready Dataset)
  └─ Türkçe Akademik Metin Veri Seti
```

---

## 📥 Desteklenen Formatlar (v6.0 - 2 Platform)

### 1️⃣ **Fliphtml5 (YENİ - v5.8)**
- **URL Örneği:** `https://online.fliphtml5.com/ysmd/wwrg/#p=1`
- **Algılama:** URL'de "fliphtml5.com" kelimesi ✅
- **İndirme Metodu:**
  - Config dosyası fetshi: `/javascript/config.js`
  - JSON parsing: `htmlConfig` değişkeni
  - Sayfa listesi: `config['fliphtml5_pages']` array'i
  - WebP download: `/files/large/{filename}.webp`
  - Rate limiting: Her 20 sayfada 1 saniyelik pause
  - PDF dönüştürme: PIL (Pillow) ile WebP sırası → PDF
- **Test Sonucu:** 193 sayfa → 44.37 MB PDF (~60 saniye)
- **Detay:** indir.py satırları 283-365

### 2️⃣ **Ata E-Kitap (Orijinal)**
- **URL Örneği:** `https://online.ataekitap.com/kitaplar/...`
- **Algılama:** HTML'de `data-ebook-path` attribute'ü ✅
- **İndirme Metodu:**
  - HTML parsing → `data-ebook-path` çıkarımı
  - Base path tespiti
  - Sayfa bitmap'leri bundle'ı download
  - PDF bundlesi oluşturma
- **Detay:** indir.py satırı 253

### 3️⃣ **Doğrudan PDF**
- **URL Örneği:** `https://example.com/book.pdf`
- **Algılama:** URL `.pdf` ile bitiyorsa ✅
- **İndirme Metodu:** Doğrudan HTTP GET
- **Detay:** indir.py satırları 485-488

### 4️⃣ **Genel Flipbook (Fallback)**
- **Algılama:** Diğer hiçbiri uyuşmazsa
- **İndirme Metodu:** İmaj seri algılaması → PDF dönüştürme

---

## ✨ Ana Özellikler

### 🤖 Bot Detection Evasion (Alegoriklik)
```python
# Modern Chrome User-Agent + Rate Limiting
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': base_url,
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache'
}
# Max 3 concurrent, 60s timeout, 1s pause/20 sayfa
```

### 🔄 Multi-Format Cascading Detection
```python
# indir.py içinde (satırlar 461-513)
if detect_fliphtml5(flipbook_url):         # Fliphtml5 mı?
    return await download_fliphtml5_book()  # Evet → WebP→PDF
elif await extract_ebook_path(...):        # Ata E-Kitap mı?
    # PDF process devam et
elif flipbook_url.endswith('.pdf'):        # Doğrudan PDF mı?
    # PDF download
else:                                       # Fallback
    # Generic flipbook handler
```

### 📊 Format Detection Test Sonuçları (v5.8)
```
✅ Fliphtml5 Tespiti: https://online.fliphtml5.com/ysmd/wwrg/#p=1
   detect_fliphtml5() = True
   İndirilen Sayfalar: 193
   Son PDF: 44.37 MB
   İşlem Süresi: ~60 saniye
   
✅ Ata E-Kitap Tespiti: https://online.ataekitap.com/kitaplar/...
   detect_fliphtml5() = False (Doğru!)
   Fallback Handler: Ata E-Kitap Extract
   Durum: ÇALIŞIYOR ✓
   
✅ Format Cascading: Tüm 4 format senaryosu test edildi
   Status: VERIFIED ✓
```

### 🧹 Otomatik Temizlik Pipeline
- **arsiv_temizleyici.py:** PDF'ler üzerinde:
  - Metadata temizleme
  - Gömülü yazı tiplerini optimize etme
  - Resim sıkıştırması
  - Aşamalı silme (corrupt dosya ayıklama)

### 🔍 OCR + NLP Processing
- **PaddleOCR:** Türkçe metin algılama
- **Dil Algılama:** tr/en/ar otomatik
- **Transliterasyon:** Arap → Latin dönüştürme
- **Metin Normalizasyonu:** Boşluk, satır sonu, özel karakterler

---

## 🚀 Kurulum

### Gereksinimler
```bash
Python 3.8+
pip install -r requirements.txt
```

### requirements.txt İçeriği
```
httpx>=0.24.0           # Async HTTP client + modern User-Agent
beautifulsoup4>=4.12.0  # HTML parsing
lxml>=4.9.0             # BS4 backend
Pillow>=9.5.0           # WebP → PDF conversion
PaddleOCR>=2.7.0.3      # OCR (Türkçe support)
paddlepaddle>=2.5.0     # PaddleOCR dependency
```

### Kurulum Adımları
```bash
# 1. Repo klonla
git clone https://github.com/...
cd ILK-MCP-main

# 2. Virtual environment oluştur (önerilir)
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 3. Bağımlılıkları yükle
pip install -r requirements.txt

# 4. Menu'den başlat (Türkçe arayüz)
python menu.py
```

---

## 💻 Kullanım

### 🎯 Menü Modları (menu.py)

#### 1. **Manuel Mode** (Önerilen - Başlayanlar İçin)
```
[Seçenek 1: Manual Mode]
├─ URL girin (Fliphtml5/Ata E-Kitap/PDF)
├─ Sistem otomatik format algılar
├─ İndirme başlar (konsolda detay görürsünüz)
└─ Çıkış klasörü: ./test_output/
```

**Örnek Çalışma:**
```bash
$ python menu.py
> Seçim: 1
> Kitap URL'sini girin: https://online.fliphtml5.com/ysmd/wwrg/
> Fliphtml5 algılandı! ✅
> İndiriliyor: Sayfa 1/193...
> İndiriliyor: Sayfa 50/193...
> PDF oluşturuluyor...
> Başarı! Çıktı: test_output/Fliphtml5_Downloaded.pdf (44.37 MB)
```

#### 2. **Batch Mode** (İleri Kullanıcılar)
- CSV dosyasından URL listesi oku
- Tüm kitapları birbirinden bağımsız indir
- Paralel işleme (3 concurrent)

#### 3. **Archive Cleaning** (Post-Processing)
```bash
python arsiv_temizleyici.py
> Klasör seçin: ./test_output/
> Tüm PDF'ler optimize edildi ✅
```

---

## 🔧 Teknik Detaylar

### Fliphtml5 Handler (indir.py, satırlar 287-365)

**Step 1: Config Fetshi**
```python
config_url = f"{base_url_clean}/javascript/config.js"
# base_url_clean = base_url.split("#")[0]  # Fragment temizleme
response = await client.get(config_url)
```

**Step 2: JSON Extraction**
```python
# config.js içinde: var htmlConfig = {...};
pattern = r'var htmlConfig = (\{.*?\});'
match = re.search(pattern, response.text)
config = json.loads(match.group(1))
```

**Step 3: Page List Parsing**
```python
pages = config['fliphtml5_pages']
# Her sayfa: {'n': ['filename.webp'], 't': './files/thumb/...'}
for i, page_item in enumerate(pages):
    page_filename = page_item['n'][0]  # Dict'ten string al
```

**Step 4: WebP Download (Rate Limited)**
```python
for i, page_item in enumerate(pages):
    page_filename = page_item['n'][0]
    page_url = f"{base_url_clean}/files/large/{page_filename}"
    response = await client.get(page_url)
    images.append(Image.open(BytesIO(response.content)))
    
    if (i + 1) % 20 == 0:
        await asyncio.sleep(1)  # Bot evasion
```

**Step 5: PDF Creation**
```python
# Pillow kullanarak WebP array'ini PDF'ye dönüştür
images[0].save(output_path, save_all=True, append_images=images[1:])
```

### URL Fragment Handling (Kritik Fix - v5.8)
```python
# PROBLEM: https://online.fliphtml5.com/ysmd/wwrg/#p=1
#          config.js fetch'i başarısız (#p=1 fragment'i sorun çıkartıyor)

# ÇÖZÜM:
base_url_clean = base_url.split("#")[0]  # Fragment temizle
# SONUÇ: https://online.fliphtml5.com/ysmd/wwrg/
```

### Format Detection Cascading (v5.8)
```python
# Detaylı kod: indir.py satırları 461-513

async def download_worker_full(flipbook_url, ...):
    # Step 1: Fliphtml5 mı? (SYNC CHECK - En hızlı)
    if detect_fliphtml5(flipbook_url):
        result = await download_fliphtml5_book(...)
        
    # Step 2: Ata E-Kitap mı? (HTML PARSE REQUIRED)
    else:
        ebook_path = await extract_ebook_path(...)
        if ebook_path:
            # PDF processing devam et
            
    # Step 3: Doğrudan PDF mı?
    elif flipbook_url.endswith('.pdf'):
        # Direct download
        
    # Step 4: Fallback generic handler
    else:
        # Generic flipbook processing
```

### Gerekli Bağımlılıklar (Minimal Stack)

| Kütüphane | Sürüm | Kullanım | Not |
|-----------|-------|---------|-----|
| httpx | ≥0.24.0 | Async HTTP + Modern UA | Bot evasion headers |
| BeautifulSoup4 | ≥4.12.0 | HTML Parsing | Ata E-Kitap extract |
| Pillow (PIL) | ≥9.5.0 | WebP → PDF | Fliphtml5 conversion |
| lxml | ≥4.9.0 | BS4 backend | HTML parser |
| PaddleOCR | ≥2.7.0.3 | OCR | Türkçe support |

---

## 📝 Sürüm Tarihi

### v5.8 (Son - Fliphtml5 Tam Desteği)
**Eklenen Özellikler:**
- ✅ Fliphtml5 Kütüphane Desteği (fliphtml5.com)
- ✅ Multi-Format Cascading Detection (4-level)
- ✅ WebP → PDF Dönüştürme Pipeline
- ✅ URL Fragment Cleanup (#p=1 fix)
- ✅ Rate Limiting & Bot Evasion

**Test Sonuçları:**
```
Fliphtml5_Esoteric.pdf
├─ Toplam Sayfalar: 193
├─ Dosya Boyutu: 44.37 MB
├─ İndirme Süresi: ~60 saniye
├─ Format Algılama: ✅ PASSED
├─ PDF Kalitesi: ✅ PERFECT (Acrobat Reader'da doğru açılıyor)
└─ Hata Oranı: 0/193
```

**Test Sayfası:**
```
URL: https://online.fliphtml5.com/ysmd/wwrg/#p=1
Test Tarihi: [Son Çalıştırma]
Sonuç: SUCCESS ✓
```

**Kod Değişiklikleri:**
- indir.py: +83 satır (Fliphtml5 handler eklenmiş)
- indir.py satırı 283: `detect_fliphtml5()` function
- indir.py satırı 287: `download_fliphtml5_book()` handler
- indir.py satırı 461: Manual mode cascading detection

**Temizlik (Cleanup):**
- ❌ Silinen: 9x Fliphtml5 investigation script
- ❌ Silinen: 5x test script (.mypy_cache, __pycache__)
- ✅ Sonuç: Production-ready state

### v5.5 (Önceki)
- Quality Inspector Update
- OCR optimization

### v5.0+
- Original Ata E-Kitap support
- Archive cleaner
- Basic NLP pipeline

---

## 🐛 Bilinen Sorunlar & Çözümleri

### ✅ URL Fragment Problemi (v5.8 FIXED)
```
Problem: https://online.fliphtml5.com/ysmd/wwrg/#p=1
Error: config.js fetch başarısız (#p=1 fragment sorun çıkartıyor)
Çözüm: base_url.split("#")[0] ile temizle
Status: FIXED ✓
```

### ✅ Page Item Structure (v5.8 FIXED)
```
Problem: pages['n'] string yerine dict yapısı
Error: TypeError: 'dict' object is not subscriptable
Çözüm: page_item['n'][0] ile dict'ten string al
Status: FIXED ✓
```

### ✅ Async Function Type (v5.8 FIXED)
```
Problem: detect_fliphtml5() async def olarak tanımlandı
Error: await gereksiz, sync check yeterli
Çözüm: async def → def değiştirildi
Status: FIXED ✓
```

---

## 📞 Destek & İletişim

**İssue Rapor Etmek:**
1. GitHub Issues'te bug açın
2. Detaylı URL ve hata mesajı ekleyin
3. test_output klasörü .zip'lemesi ekleyin

**Öneriler & Gelişmeler:**
- Discussion tab'ında fikirlerinizi paylaşın
- Feature request'leri açın (başlık: [FEATURE])

---

## 📄 Lisans

Bu proje **esoteric kütüphanelerin dijitalleştirilmesi** için tasarlanmıştır.
Lütfen yerel yasalara ve platform kullanım koşullarına uyunuz.

---

## 🙏 Teşekkür

- Fliphtml5 mimarisi reverse-engineering'i: Sistematik investigation scriptleri
- WebP format support: PIL/Pillow
- Türkçe OCR: PaddleOCR Community
- Async concurrency: httpx + asyncio

---

**Son Güncelleme:** v6.0 - İsem Dijital Kaldırıldı, 2-Platform Sistem (Fliphtml5 + Ata E-Kitap)
**Durum:** Production Ready ✅
**Test Coverage:** 
  - 193 sayfa Fliphtml5 ✅
  - 900+ sayfa Ata E-Kitap ✅
  - 3-level Cascading Detection ✅

---

## 📋 Sürüm Tarihi (Changelog)

### v6.0 (18 Aralık 2025) - PRODUCTION READY
**Büyük Değişiklik: İsem Dijital Desteği Kaldırıldı**

#### ✅ Yapılan İşlemler:
- ❌ İsem Dijital (isemdijital.com) platformu tamamen kaldırıldı
- 🗑️ 30+ İsem test dosyası silindi
- 🗑️ 4 İsem test klasörü silindi
- 🗑️ 100+ eski debug/test dosyası silindi
- 🧹 Steganographia assets klasörü temizlendi
- ✅ Cascade detection optimize edildi (4-seviye → 3-seviye)
- ✅ Kod temizlendi (İsem referansı = 0)
- ✅ README.md v6.0'a güncellendi

#### 📊 Güncel Platform Desteği:
| Platform | Durum | Test | Not |
|----------|-------|------|-----|
| Fliphtml5 | ✅ Aktif | 193 sayfa | Production Ready |
| Ata E-Kitap | ✅ Aktif | 900+ sayfa | Production Ready |
| Generic Flipbook | ✅ Fallback | - | Backup Handler |

#### 🔧 Core Functions (v6.0):
1. `detect_fliphtml5(url)` - Fliphtml5 algılama
2. `download_fliphtml5_book()` - Fliphtml5 indirme
3. `extract_ebook_path()` - Ata E-Kitap algılama  
4. `download_flipbook_images()` - Generic indirme

#### 🚀 Sistem Durumu:
- ✅ Python Syntax: OK (4 modül)
- ✅ Import Test: OK
- ✅ Cascade Detection: 3/3 Platform
- ✅ Code Quality: Clean
- ✅ Deployment: READY

---

### v5.9 (Önceki) - İsem Dijital Experimental
- İsem Dijital desteği eklendi (proprietary format)
- 312 sayfa PDF oluşturma başarılı
- Screenshot-based extraction yöntemi
- **Not:** Bu sürüm production'da instable olduğu için v6.0'da kaldırıldı

---

## 🔄 Geçiş Kılavuzu (v5.x → v6.0)

İsem Dijital linklerini kullanıyorsanız:
- **UYARI:** v6.0'da İsem Dijital desteği kaldırıldı
- **Çözüm:** Fliphtml5 veya Ata E-Kitap alternatifleri kullanın

Sistem otomatik olarak fallback handler ile genel flipbook olarak işleyecektir.

---

### v6.1 (18 Aralık 2025) - PORTABILITY & WINDOWS SUPPORT
**Windows üzerinde kolay kurulum ve çalışma için iyileştirmeler yapıldı.**

#### ✅ Yapılan İyileştirmeler:
- **Otomatik Dizin Algılama:** `menu.py` artık hardcoded (sabit) dosya yolları yerine, çalıştığı dizini otomatik olarak algılıyor. Bu sayede uygulama Masaüstü veya herhangi bir klasörden sorunsuz çalıştırılabilir.
- **Sanal Ortam Entegrasyonu:** `Baslat.bat`, sistem genelindeki Python yerine doğrudan proje içindeki `.venv` sanal ortamını kullanacak şekilde güncellendi.
- **Kolay Başlatma:** Masaüstü kısayolu oluşturma desteği eklendi.
- **Bağımlılıklar:** `requirements.txt` üzerinden eksik kütüphanelerin (httpx, beautifulsoup4, pillow) otomatik yüklenmesi desteklendi.

#### 🔧 Nasıl Güncellenir?
Eğer eski bir sürümden geliyorsanız:
1. Projeyi son sürüme çekin (`git pull`).
2. `.venv` klasörü varsa, `Baslat.bat` dosyasını çalıştırın; gerekli ayarlar otomatik yapılacaktır.

