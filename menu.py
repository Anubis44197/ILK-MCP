
import asyncio
import os
import sys
import subprocess

# REnkler
C_HEADER = "\033[95m"
C_BLUE = "\033[94m"
C_GREEN = "\033[92m"
C_RESET = "\033[0m"

SCRATCH_DIR = r"c:\Users\90535\.gemini\antigravity\scratch"
PYTHON_EXE = sys.executable

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def main_menu():
    while True:
        clear()
        print(f"{C_HEADER}========================================")
        print(f"      HERMES PROJECT - ANA KUMANDA")
        print(f"========================================{C_RESET}")
        print("1. İndirme Konsolu (Hermes v4.0)")
        print("2. Veri İşleme & Yapay Zeka Hazırlığı (Human/Machine)")
        print("3. Masaüstü Arşivini Düzenle/Onar (Temizlik)")
        print("4. Çıkış")
        
        choice = input(f"\n{C_BLUE}Seçiminiz: {C_RESET}")
        
        script = ""
        if choice == '1':
            script = "indir.py"
        elif choice == '2':
            script = "setup_final_environment.py"
        elif choice == '3':
            script = "arsiv_temizleyici.py"
        elif choice == '4':
            sys.exit()
        else:
            continue
            
        full_path = os.path.join(SCRATCH_DIR, script)
        if os.path.exists(full_path):
            try:
                print(f"\n🚀 Başlatılıyor: {script} ...")
                print("-" * 40)
                # subprocess call
                subprocess.run([PYTHON_EXE, full_path], check=False)
                print("-" * 40)
                input("\nMenüye dönmek için Enter'a basın...")
            except Exception as e:
                print(f"Hata: {e}")
                input("Enter...")
        else:
            print(f"Dosya bulunamadı: {full_path}")
            input("Enter...")

if __name__ == "__main__":
    main_menu()
