import asyncio
import httpx
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

async def test_ebook_url():
    # Found from data-ebook-path
    ebook_path = "/e-books/2023-2024/Ortaokul/7-sinif/7_Sinif_Ben_Korkmam_Fen_Bilimleri_Soru_Bankasi/index.html"
    base_url = "https://www.ataekitap.com"
    ebook_url = urljoin(base_url, ebook_path)
    
    print(f"📚 E-Book URL: {ebook_url}\n")
    
    async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}, verify=False, timeout=60, follow_redirects=True) as client:
        # Get the ebook page
        print("1️⃣  Fetching ebook index page...")
        resp = await client.get(ebook_url)
        print(f"   Status: {resp.status_code}")
        print(f"   Size: {len(resp.content)} bytes")
        
        if resp.status_code == 200:
            # Look for patterns in the HTML
            if "flipbook" in resp.text.lower():
                print("   ✅ Found 'flipbook' in page")
            
            if "files/mobile" in resp.text.lower():
                print("   ✅ Found 'files/mobile' pattern")
                
            if "pages/" in resp.text.lower():
                print("   ✅ Found 'pages/' pattern")
            
            # Try to find image patterns
            patterns = ["files/mobile/", "files/large/", "mobile/", "files/shot/", "pages/", "files/page/"]
            
            print("\n2️⃣  Testing image patterns...")
            for pat in patterns:
                test_url = urljoin(ebook_url, f"{pat}1.jpg")
                try:
                    r = await client.get(test_url, timeout=5)
                    if r.status_code == 200:
                        # Check if it's actually an image
                        if r.content.startswith(b'\xff\xd8'):
                            print(f"   ✅ {pat} - Status {r.status_code} - VALID JPEG!")
                        else:
                            print(f"   ⚠️  {pat} - Status {r.status_code} - NOT JPEG ({r.content[:20]})")
                    else:
                        print(f"   ❌ {pat} - Status {r.status_code}")
                except Exception as e:
                    print(f"   ❌ {pat} - Error: {str(e)[:50]}")
            
            # Save HTML for inspection
            print("\n3️⃣  Saving HTML for inspection...")
            with open("ataekitap_ebook.html", "w", encoding="utf-8") as f:
                f.write(resp.text)
            print("   ✅ Saved to ataekitap_ebook.html")
            
            # Look for script data
            soup = BeautifulSoup(resp.text, "html.parser")
            scripts = soup.find_all("script")
            
            print(f"\n4️⃣  Found {len(scripts)} script tags, checking for JSON...")
            for i, script in enumerate(scripts):
                if script.string:
                    content = script.string.strip()
                    # Look for specific patterns
                    if "pageCount" in content or "totalPages" in content or "images" in content:
                        print(f"   📝 Script {i} has page/image data")
                        print(f"      {content[:200]}...")

asyncio.run(test_ebook_url())
