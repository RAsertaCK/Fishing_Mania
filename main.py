# main.py
import pygame
import sys
import os 
import traceback # <--- TAMBAHKAN IMPORT INI

try:
    # Mengubah direktori kerja ke direktori tempat skrip ini berada
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir: 
        os.chdir(script_dir)
        print(f"Direktori kerja diubah ke: {script_dir}")
    else:
        print("PERINGATAN: Tidak bisa mendapatkan direktori skrip. Path relatif mungkin bermasalah.")
except NameError: 
    print("Tidak bisa mengubah direktori kerja (mungkin dijalankan secara interaktif).")
except FileNotFoundError:
    print(f"PERINGATAN: Direktori skrip '{script_dir if 'script_dir' in locals() else ''}' tidak ditemukan. Path relatif mungkin bermasalah.")

try:
    from config import Config 
    from game import Game
except ImportError as e:
    print(f"ERROR Impor Awal: {e}")
    print("Pastikan semua file .py (config.py, game.py, dll.) ada di direktori yang sama dengan main.py.")
    sys.exit()


def main():
    print("Menjalankan main() dari __main__...")
    
    try:
        pygame.init()
        print("Pygame berhasil diinisialisasi.")
    except pygame.error as e:
        print(f"ERROR saat pygame.init(): {e}")
        sys.exit()

    try:
        if pygame.mixer.get_init() is None: 
            pygame.mixer.init() 
            if pygame.mixer.get_init():
                print("Pygame mixer berhasil diinisialisasi.")
            else:
                print("PERINGATAN: Pygame mixer GAGAL diinisialisasi.")
        else:
            print("Pygame mixer sudah terinisialisasi sebelumnya.")
    except pygame.error as e:
         print(f"ERROR saat pygame.mixer.init(): {e}")

    try:
        if not hasattr(Config, 'SCREEN_WIDTH') or not hasattr(Config, 'SCREEN_HEIGHT'):
            print("ERROR: Config tidak memiliki atribut SCREEN_WIDTH atau SCREEN_HEIGHT.")
            print("Menggunakan nilai default 1280x720.")
            screen_width, screen_height = 1280, 720
        else:
            screen_width, screen_height = Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT

        screen_surface = pygame.display.set_mode((screen_width, screen_height)) # Ganti nama variabel agar tidak bentrok
        pygame.display.set_caption("Fishing Mania (TES Ver.)") 
        print("Layar game berhasil dibuat.")
    except AttributeError as e: 
        print(f"ERROR: Pastikan Config memiliki SCREEN_WIDTH dan SCREEN_HEIGHT. Detail: {e}")
        pygame.quit()
        sys.exit()
    except pygame.error as e: 
        print(f"ERROR saat membuat layar (pygame error): {e}")
        pygame.quit()
        sys.exit()
    except Exception as e: 
        print(f"ERROR tidak diketahui saat membuat layar: {e}")
        pygame.quit()
        sys.exit()

    game_instance = None 
    try:
        game_instance = Game(screen_surface) # Gunakan variabel screen_surface yang baru
        print("Instance Game berhasil dibuat. Menjalankan game...")
        game_instance.run()
    except Exception as e:
        print("--- ERROR FATAL saat menjalankan Game instance: ---")
        print(f"Detail Error: {e}")
        traceback.print_exc() 
    finally:
        print("Keluar dari fungsi main().")
        if game_instance and hasattr(game_instance, 'running') and game_instance.running:
            game_instance.running = False 
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()