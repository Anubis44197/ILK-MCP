import asyncio
import httpx
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

async def check_page():
    url = "https://www.ataekitap.com/kitaplar/7-sinif-ben-korkmam-fen-bilimleri-soru-bankasi"
    
    async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}, verify=False, timeout=60) as client:
        resp = await client.get(url)
        
        # Save raw HTML for inspection
        with open("ataekitap_raw.html", "w", encoding="utf-8") as f:
            f.write(resp.text)
        
        print(f"✅ Saved raw HTML to ataekitap_raw.html ({len(resp.text)} bytes)")
        
        # Look for specific patterns
        if "fliphtml" in resp.text.lower():
            print("✅ Found FlipHTML5 reference")
        
        if "issuu" in resp.text.lower():
            print("✅ Found ISSUU reference")
        
        if "view." in resp.text.lower():
            print("✅ Found view. reference")
        
        if "files/mobile" in resp.text.lower():
            print("✅ Found files/mobile pattern")
        
        if '"url"' in resp.text or "'url'" in resp.text:
            print("✅ Found 'url' in page")
        
        # Look for book ID or similar
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Check all divs with data attributes
        print("\n📍 Elements with data-* attributes:")
        all_elements = soup.find_all(True)  # All elements
        for elem in all_elements:
            attrs = elem.attrs
            if any(k.startswith("data-") for k in attrs.keys()):
                data_attrs = {k: v for k, v in attrs.items() if k.startswith("data-")}
                print(f"   <{elem.name}> {data_attrs}")
        
        # Look for JSON in script tags
        print("\n📋 Script content (first 500 chars of each):")
        scripts = soup.find_all("script")
        for i, script in enumerate(scripts, 1):
            if script.string:
                content = script.string.strip()[:500]
                if content:
                    print(f"\n   Script {i}:")
                    print(f"   {content}")

asyncio.run(check_page())
