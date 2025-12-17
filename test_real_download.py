import asyncio
import os
import httpx
from urllib.parse import urljoin, urlparse

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

async def test_download():
    base_url = "https://view.gunayekitap.com/book/39"
    target_dir = "./test_download"
    os.makedirs(target_dir, exist_ok=True)
    
    if not base_url.endswith('/'): 
        base_url += '/'
    
    patterns = ["files/mobile/", "files/large/", "mobile/", "files/shot/", "pages/", "", "files/page/"]
    
    async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}, verify=False, timeout=60, follow_redirects=True) as client:
        # Pattern detection
        valid_pattern = None
        for pat in patterns:
            test_url = urljoin(base_url, f"{pat}1.jpg")
            print(f"Pattern test: {test_url[:80]}...", end=" -> ")
            try:
                r = await client.get(test_url)
                print(f"Status {r.status_code}")
                if r.status_code == 200:
                    print(f"✅ FOUND: {pat}")
                    valid_pattern = pat
                    # Test content
                    print(f"   File size: {len(r.content)} bytes")
                    if r.content[:10]:
                        print(f"   First bytes: {r.content[:10]}")
                    break
            except Exception as e:
                print(f"ERROR: {str(e)[:40]}")
        
        if not valid_pattern:
            print("❌ NO PATTERN FOUND")
            return
        
        print(f"\n→ Starting download with pattern: {valid_pattern}")
        
        # Download first 3 pages for testing
        found_images = []
        for page_num in range(1, 4):
            img_url = urljoin(base_url, f"{valid_pattern}{page_num}.jpg")
            print(f"   Page {page_num}: {img_url[:70]}... ", end="")
            try:
                resp = await client.get(img_url)
                print(f"Status {resp.status_code}, Size: {len(resp.content)} bytes", end="")
                
                if resp.status_code == 200:
                    fname = f"{page_num:04d}.jpg"
                    fpath = os.path.join(target_dir, fname)
                    with open(fpath, "wb") as f:
                        f.write(resp.content)
                    found_images.append(fpath)
                    print(" ✅ SAVED")
                else:
                    print(f" ❌ Failed")
            except Exception as e:
                print(f"❌ ERROR: {str(e)[:50]}")
        
        print(f"\n📊 Summary: Downloaded {len(found_images)} images")
        
        # Check file headers
        for fpath in found_images:
            if os.path.exists(fpath):
                with open(fpath, 'rb') as f:
                    header = f.read(10)
                    if header.startswith(b'\xff\xd8'):
                        print(f"   {os.path.basename(fpath)}: ✅ JPEG (magic bytes OK)")
                    else:
                        print(f"   {os.path.basename(fpath)}: ❌ NOT JPEG ({header[:20]})")

asyncio.run(test_download())
