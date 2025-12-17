import asyncio
import os
import httpx
from urllib.parse import urljoin
from PIL import Image
from io import BytesIO

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

async def test_full_download():
    # The working ebook URL
    ebook_url = "https://www.ataekitap.com/e-books/2023-2024/Ortaokul/7-sinif/7_Sinif_Ben_Korkmam_Fen_Bilimleri_Soru_Bankasi/index.html"
    
    target_dir = "./test_ataekitap_download"
    os.makedirs(target_dir, exist_ok=True)
    
    print(f"📥 Downloading from: {ebook_url}\n")
    
    async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}, verify=False, timeout=60, follow_redirects=True) as client:
        pattern = "files/mobile/"
        
        print("📖 Downloading pages...")
        found_images = []
        
        for page_num in range(1, 21):  # Try first 20 pages
            img_url = urljoin(ebook_url, f"{pattern}{page_num}.jpg")
            
            try:
                resp = await client.get(img_url, timeout=10)
                
                if resp.status_code == 200:
                    # Verify it's a valid JPEG
                    if resp.content.startswith(b'\xff\xd8'):
                        fname = f"{page_num:04d}.jpg"
                        fpath = os.path.join(target_dir, fname)
                        with open(fpath, "wb") as f:
                            f.write(resp.content)
                        found_images.append(fpath)
                        print(f"   ✅ Page {page_num}: {len(resp.content)} bytes - SAVED")
                    else:
                        print(f"   ❌ Page {page_num}: {resp.status_code} - NOT JPEG")
                        break
                else:
                    print(f"   ❌ Page {page_num}: Status {resp.status_code}")
                    if page_num > 5:  # If we have at least 5 pages, consider it success
                        break
                    
            except Exception as e:
                print(f"   ❌ Page {page_num}: Error - {str(e)[:40]}")
                break
        
        print(f"\n✅ Downloaded {len(found_images)} valid pages")
        
        if len(found_images) > 0:
            # Try to create a small PDF
            print(f"\n📚 Creating PDF from {len(found_images)} pages...")
            try:
                images = []
                for fpath in found_images[:5]:  # Use first 5 pages
                    img = Image.open(fpath)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    images.append(img)
                
                pdf_path = os.path.join(target_dir, "preview.pdf")
                images[0].save(pdf_path, "PDF", save_all=True, append_images=images[1:])
                print(f"   ✅ PDF created: {pdf_path}")
                
                # Check file size
                size = os.path.getsize(pdf_path)
                print(f"   📄 PDF size: {size} bytes")
                
            except Exception as e:
                print(f"   ❌ PDF creation error: {e}")
        
        print(f"\n✅ Test complete! Images saved to {target_dir}")

asyncio.run(test_full_download())
