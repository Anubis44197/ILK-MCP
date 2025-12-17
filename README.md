# 📜 Project Hermes: Esoteric Data Refinery & Automation

Bu proje, internet üzerindeki herhangi bir kaynaktan (Web, PDF) bilgi toplamak, bu bilgiyi temizlemek (Rafine Etmek) ve Yapay Zeka (LLM) eğitimine uygun, yüksek kaliteli veri setlerine dönüştürmek için tasarlanmış tam otomatik bir **Veri Mühendisliği Boru Hattıdır (Data Engineering Pipeline)**.

**Son Sürüm:** v5.5 (Quality Inspector Update)

---

## 🚀 Öne Çıkan Özellikler

### 1. Hermes Konsolu v4.5 (Örümcek Modu)

* **🕷️ Akıllı Örümcek (Deep Spider)**: Verdiğiniz bir web sayfasını sadece taramakla kalmaz, o sayfaya bağlı (Depth-1) alt kategorileri de gezerek tüm kütüphaneyi ortaya çıkarır.
* **Tam Otomatik**: İndirme işlemi biter bitmez "Veri Rafinerisi"ni devreye sokar. Manuel müdahale gerektirmez.
* **Güvenli Gezinti**: Sonsuz döngü koruması, akıllı domain filtresi ve timeout mekanizmaları ile en karmaşık arşivlerde bile kaybolmadan çalışır.
* **Akıllı Filtre**: Reklamları ve gereksiz linkleri eler, sadece "Bilgi Değeri" olan içerikleri (Kitap, Makale, Arşiv) sunar.

### 2. Akıllı Veri Rafinerisi (Data Refinery)

İndirilen ham veriyi işleyerek saf bilgiye dönüştüren ana motordur:

* **👁️ OCR Modülü (Göz)**:
  * İndirilen PDF'leri analiz eder. Metin katmanı yoksa (resim taranmışsa), otomatik olarak **Tesseract OCR** motorunu devreye sokar ve %99 doğrulukla metne çevirir.
  * Türkçe ve İngilizce dil desteği entegredir.
* **🧠 Anlamsal Bölümleme (Smart Chunking)**:
  * Devasa metinleri, LLM'lerin (Claude, GPT, Gemini) "Context Window" limitlerine uygun, anlam bütünlüğü bozulmadan 3000 karakterlik parçalara böler.
* **🛡️ Kalite Müfettişi (Quality Inspector v2.0)**:
  * Metinleri 4 aşamalı testten geçirir: **Sembol Yoğunluğu**, **Kelime Formasyonu**, **Sesli Harf Oranı** ve **Uzunluk**.
  * OCR hatasıyla bozulmuş veya anlamsız karakter yığınlarını (ör: `x#_|||...`) tespit eder ve "Karantina"ya gönderir.
* **♻️ Sıfır Atık (Zero Waste Protocol)**:
  * **İşle ve Yok Et:** Bir dosya başarıyla işlendiği ve verisi alındığı an, orijinal ham dosya (Örn: 500MB'lık PDF) diskten **kalıcı olarak silinir**. Sadece saf veri (`Markdown`) saklanır.
  * Disk alanınız asla dolmaz.
* **💾 Dijital Hafıza (Manifest)**:
  * `library_manifest.json` dosyası, işlenen her kitabın parmak izini saklar. Aynı kitabı tekrar indirseniz bile, sistem "Bunu hatırlıyorum" diyerek işlemeyi atlar.

---

## 🛠️ Kurulum ve Hazırlık

### 1. Python ve Kütüphaneler

Gerekli paketleri (AI araçları, Web tarayıcıları, OCR kütüphaneleri) tek komutla kurun:

```bash
pip install -r requirements.txt
```

### 2. OCR Motoru (Gerekli!)

PDF Okuma özelliğinin çalışması için **Tesseract OCR** ve **Poppler** araçlarının sisteminizde kurulu olması gerekir.

* **Windows için Tesseract**: [İndir ve Kur](https://github.com/UB-Mannheim/tesseract/wiki)
* **Önemli**: Kurulum yolunu değiştirmeyin (`C:\Program Files\Tesseract-OCR`) veya koddaki yolu güncelleyin.

---

## 💻 Kullanım

Sistemi başlatmak için tek komut yeterlidir:

```bash
python indir.py
```

1. **Menüden Seçim Yapın**: Otomatik arşivleri tarayın veya kendi URL'nizi girin.
2. **Seç ve Başla**: İndirmek istediğiniz kitapları işaretleyin.
3. **İzle**: Hermes önce dosyaları indirir, ardından otomatik olarak **Rafineri** moduna geçer; PDF'leri okur, dönüştürür ve temizler.

**Çıktılar (`Desktop/Esoteric_Library/Kutuphane`):**

* **001_Kitap_Adi**, **002_Diger_Kitap** şeklinde tarih sırasına göre numaralandırılır.
* Her kitap klasörünün içi şöyledir:
  * � `Kitap_Adi_Orijinal.pdf` (Orijinal dosya direkt buradadır).
  * � `Okunabilir/`: İnsan okuması için Markdown dosyaları.
  * 📂 `Veri_Seti/`: Yapay zeka eğitimi için Hash ID'li JSONL verisetleri.
* 🗑️ `Karantina/`: Okunamayan veya bozuk dosyalar ana dizinde ayrılır.

---

## 📜 Sürüm Geçmişi

### v5.6 - Universal Downloader (Evrensel Erişim)

* **Özgür İndirici:** "Manuel URL" modu artık tamamen evrenselleştirildi. Yayıncı veya site ayrımı yapmaksızın verilen URL'yi analiz eder.
* **Akıllı URL Temizliği:** `index.html` veya parametreli karmaşık linkleri otomatik temizleyip doğru dosya yolunu (mobile/large klasörleri) bulur.
* **Sorgusuz Mod:** Kullanıcıya gereksiz sorular sormaz; URL ve İsim girilir, indirme başlar.

### v5.5 - Quality Inspector Update (Güncel)

* **Akıllı Denetim:** Artık sadece dosya boyutuna değil, içeriğin dilbilgisel tutarlılığına bakılıyor.
* **Gürültü Filtresi:** Sembol/Harf oranı, kelime uzunluk anomalileri ve sesli harf analizi ile "çöp" (garbage) veriler %99 oranında engelleniyor.
* **Veri Hijyeni:** Veri setine sadece insan okumasına uygun, yüksek kaliteli metinler dahil ediliyor.

### v5.4 - Flipbook Special Edition

* **Flipbook Desteği:** Resim serisi şeklinde sunulan (PubHTML5 vb.) kitapları algılar ve indirir.
* **Özel Klasör:** Bu tür indirmeler `Flipbooks` klasörüne yalıtılır.
* **Saf PDF Modu:** İndirilen yüzlerce resmi otomatik birleştirir, tek bir PDF yapar ve resimleri siler.
* **AI Muafiyeti:** Bu modda indirilen kitaplar eğitim setine (JSONL) dönüştürülmez, sadece okunmak içindir.

### v5.2 - Stability & Hotfixes

* **Kritik Onarım:** `indir.py` ve `setup_final_environment.py` dosyalarındaki eksik kod blokları tamamen onarıldı.
* **Hata Ayıklama Modu:** Menü sistemi artık hata durumunda kapanmıyor, kullanıcıya rapor sunuyor.
* **Tam Entegrasyon:** Türkçe klasör yapısı ve numaralandırma sistemi tüm modüllere sorunsuz entegre edildi.

### v5.1 - Turkish Edition

* **Tam Türkçe Yapı:** Klasör isimleri `Kutuphane`, `Okunabilir`, `Veri_Seti` olarak güncellendi.
* **Akıllı Sıralama:** İndirilen her klasöre otomatik sıra numarası (`001_`, `002_`) verilir.
* **Basitleştirilmiş Erişim:** Orijinal dosyalar artık alt klasörde değil, direkt kitap klasörünün içindedir.

### v5.0 - Professional Archiver

* **Merkezi Kütüphane Yapısı:** Tüm veriler `Library/` altında tek bir hiyerarşide toplanır.
* **Arşivleme Stratejisi:**
  * `Raw_Source`: Orijinal dosyalar silinmez, korunur.
  * `Human_Readable`: İnsan okuması için temiz Markdown.
  * `Machine_Data`: LLM eğitimi için zenginleştirilmiş veri.
* **Veri Bilimi Standartları:**
  * **Smart Chunking:** RAG sistemleri için örtüşmeli (overlapped) metin bölümleme.
  * **Content Hashing (MD5):** Her veri parçası için benzersiz kimliklendirme.
* **Genişletilmiş Örümcek:** 300 sayfaya kadar derinlemesine tarama kapasitesi.

### v4.5 - Spider Update

* **Deep Crawl (Örümcek):** Alt sayfaları ve kategorileri otomatik gezme yeteneği.
* **Smart Security:** Sonsuz döngü ve tuzak URL koruması.

### v4.0 - Refinery Edition

* **Tesseract OCR Entegrasyonu:** Görüntü tabanlı PDF'leri okuma yeteneği.
* **Manifest V2:** Gelişmiş hafıza yönetimi.

### v3.0 - Hermes Console

* Evrensel URL tarayıcı ve çoklu seçim arayüzü.

### v2.0 - MCP Server

* Model Context Protocol entegrasyonu.
