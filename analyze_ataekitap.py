import asyncio
import httpx
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

async def analyze_site():
    url = "https://www.ataekitap.com/kitaplar/7-sinif-ben-korkmam-fen-bilimleri-soru-bankasi"
    
    print(f"🔍 Analyzing: {url}\n")
    
    async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}, verify=False, timeout=60, follow_redirects=True) as client:
        # 1. Get main page
        print("1️⃣  Fetching main page...")
        try:
            resp = await client.get(url)
            print(f"   Status: {resp.status_code}")
            print(f"   Content-Type: {resp.headers.get('content-type', 'N/A')}")
            print(f"   Size: {len(resp.content)} bytes")
            
            soup = BeautifulSoup(resp.content, "html.parser")
            
            # Look for common patterns
            print("\n2️⃣  Looking for iframes (embed)...")
            iframes = soup.find_all("iframe")
            for i, iframe in enumerate(iframes[:3], 1):
                src = iframe.get("src", "N/A")
                print(f"   [{i}] {src[:100]}")
            
            print("\n3️⃣  Looking for image tags...")
            images = soup.find_all("img")
            print(f"   Found {len(images)} img tags")
            for img in images[:5]:
                src = img.get("src", "N/A")
                alt = img.get("alt", "")
                if "kitap" in alt.lower() or "book" in alt.lower() or "sayfa" in src.lower():
                    print(f"   - {alt}: {src[:80]}")
            
            print("\n4️⃣  Looking for script tags with data...")
            scripts = soup.find_all("script")
            print(f"   Found {len(scripts)} script tags")
            
            for script in scripts:
                if script.string:
                    content = script.string[:200]
                    if "json" in content.lower() or "image" in content.lower() or "url" in content.lower():
                        print(f"   - {content[:150]}...")
            
            print("\n5️⃣  Looking for data attributes...")
            data_elements = soup.find_all(attrs={"data-url": True})
            for elem in data_elements[:3]:
                print(f"   - {elem.get('data-url', 'N/A')[:100]}")
            
            # Look for flipbook URLs
            print("\n6️⃣  Looking for common flipbook patterns...")
            flipbook_patterns = [
                "flipbook", "pages", "book", "viewer", "mobile/1",
                "view.", "issuu", "gumroad", "fliphtml5"
            ]
            
            for pattern in flipbook_patterns:
                if pattern.lower() in resp.text.lower():
                    print(f"   ✅ Found keyword: '{pattern}'")
            
            # Extract URLs from page
            print("\n7️⃣  Extracting URLs...")
            links = soup.find_all("a", href=True)
            important_links = []
            for link in links:
                href = link.get("href", "")
                text = link.get_text(strip=True)[:50]
                if any(kw in href.lower() for kw in ["kitap", "pdf", "view", "book", "page"]):
                    important_links.append((text, href))
            
            print(f"   Found {len(important_links)} potentially useful links:")
            for text, href in important_links[:10]:
                full_url = urljoin(url, href)
                print(f"   - {text}: {full_url[:100]}")
            
            # Check for PDF download
            print("\n8️⃣  Checking for direct downloads...")
            pdfs = [link for link in links if link.get("href", "").lower().endswith(".pdf")]
            for pdf in pdfs[:3]:
                href = pdf.get("href", "")
                full_url = urljoin(url, href)
                print(f"   📄 {full_url}")
            
            # Check meta tags for Open Graph / structured data
            print("\n9️⃣  Meta tags...")
            metas = soup.find_all("meta")
            for meta in metas:
                name = meta.get("name", meta.get("property", ""))
                content = meta.get("content", "")
                if any(kw in name.lower() for kw in ["image", "description", "url"]):
                    print(f"   {name}: {content[:80]}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "="*80)
    print("📋 SUMMARY")
    print("="*80)

asyncio.run(analyze_site())
