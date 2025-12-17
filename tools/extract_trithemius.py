from mcp.server.fastmcp import FastMCP
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import asyncio
import os

# Standalone script, not using FastMCP server directly but using its logic
async def fetch_html(url: str):
    print(f"Fetching {url}")
    async with httpx.AsyncClient(verify=False, follow_redirects=True) as client:
        response = await client.get(url, timeout=30.0)
        if response.encoding is None or response.encoding == 'ISO-8859-1':
            response.encoding = 'utf-8' 
        return response.text

async def convert_url_to_md(url, output_filename):
    print(f"Processing {url} -> {output_filename}")
    html = await fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")

    # Image processing
    image_count = 0
    for img in soup.find_all("img"):
        if img is None: continue
        try:
            src = img.get("src")
        except AttributeError: continue
        if not src: continue
        
        img_h = img.get("height")
        if "pixel" in src or "line" in src or (img_h and img_h == "1"):
            img.decompose() 
            continue

        full_img_url = urljoin(url, src)
        alt_text = img.get("alt", f"Image-{image_count}")
        markdown_image = f"\n\n![{alt_text}]({full_img_url})\n\n"
        img.replace_with(markdown_image)
        image_count += 1

    # Cleanup
    for script in soup(["script", "style", "head", "input", "form", "nav"]):
        script.decompose()

    # Text extraction
    text = soup.get_text(separator="\n")
    cleaned_lines = [line.strip() for line in text.splitlines() if line.strip()]
    final_content = "\n".join(cleaned_lines)

    header = f"# Source: {url}\n\n"
    
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(header + final_content)
    
    print(f"Saved {output_filename} ({len(final_content)} chars)")

async def main():
    tasks = [
        ("https://www.esotericarchives.com/tritheim/stegano.htm", "steganographia_book1.md"),
        ("https://www.esotericarchives.com/tritheim/steg4.htm", "steganographia_book2.md"),
        ("https://www.esotericarchives.com/tritheim/stegano3.htm", "steganographia_book3.md")
    ]
    
    for url, filename in tasks:
        await convert_url_to_md(url, filename)

if __name__ == "__main__":
    asyncio.run(main())
