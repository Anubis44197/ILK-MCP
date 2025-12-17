#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST: Menu.py Simulation - Option 2 (Manual URL Download)
Verilen URL'i indir ve PDF oluştur
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

# Import main functions from indir.py
from indir import download_worker_full

async def test_menu_option_2():
    """Simulate menu option 2 - Manual URL input"""
    
    print("\n" + "="*80)
    print("🧪 TEST: MENU OPTION 2 - MANUAL URL DOWNLOAD")
    print("="*80)
    
    # Simulate user input
    url = "https://www.ataekitap.com/kitaplar/7-sinif-ben-korkmam-fen-bilimleri-soru-bankasi"
    title = "Ata E-Kitap - Fen Bilimleri Soru Bankası"
    
    print(f"\n📎 URL: {url}")
    print(f"📘 Başlık: {title}")
    
    # Call the main download function
    items = [{"title": title, "url": url, "type": "EBOOK"}]
    
    try:
        await download_worker_full(
            items=items,
            folder_name_raw=title,
            is_flipbook=True,
            flipbook_url=url
        )
        print("\n✅ TEST BAŞARILI")
        return True
    except Exception as e:
        print(f"\n❌ TEST BAŞARISIZ: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_menu_option_2())
    sys.exit(0 if result else 1)
