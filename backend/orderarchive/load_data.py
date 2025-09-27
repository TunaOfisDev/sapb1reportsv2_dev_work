# backend/orderarchive/load_data.py
import django
import os
import sys
import subprocess
from glob import glob
from datetime import datetime
import traceback

# Proje yolunu modül yollarına ekle
sys.path.append('/var/www/sapb1reportsv2/backend')

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sapreports.settings')

# Log dosyası ve chunk dizini tanımları
LOG_FILE = "/home/user/uyum_siparis_arsiv/logs/load_data.log"
CHUNKS_DIR = "/home/user/uyum_siparis_arsiv/orderarchive_chunks/"

def setup_logging():
    """
    Log dosyasını hazırla ve yetkileri geçici olarak devret.
    """
    print("Loglama başlatılıyor...")
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        subprocess.run(["sudo", "touch", LOG_FILE], check=True)
        subprocess.run(["sudo", "chown", "user:user", LOG_FILE], check=True)
        print("Loglama tamamlandı.")
    except Exception as e:
        print(f"Log dosyasını hazırlarken hata oluştu: {e}")
        sys.exit(1)

def log_message(message):
    """
    Mesajı log dosyasına ve konsola yaz.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"
    print(formatted_message)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(formatted_message + "\n")
    except PermissionError:
        print("Log dosyasına yazılamadı. Yetki sorunlarını kontrol edin.")

def import_chunks():
    """
    Chunk dosyalarını sırayla içeri aktarır.
    """
    from orderarchive.utils.import_large_file import import_large_file

    # Chunk dosyalarını listele ve sıralama işlemi uygula
    chunk_files = sorted(
        glob(os.path.join(CHUNKS_DIR, "*.xlsx")),
        key=lambda x: (
            os.path.basename(x).split('_')[0],  # Dosya ön eki sıralama (ör. 01, 02)
            int(os.path.basename(x).split('_')[-1].split('.')[0].replace("chunk", ""))  # Chunk numarasına göre sıralama
        )
    )
    log_message(f"Bulunan chunk dosyaları: {chunk_files}")

    if not chunk_files:
        log_message("Hata: Chunk dosyaları bulunamadı.")
        return

    for chunk_file in chunk_files:
        try:
            log_message(f"Yükleme işlemi başlatılıyor: {chunk_file}")
            import_large_file(chunk_file, chunk_size=10000)
            log_message(f"{chunk_file} başarıyla yüklendi.")
        except Exception as e:
            log_message(f"Hata oluştu: {chunk_file} -> {e}")
            traceback.print_exc()


def main():
    """
    Ana işlem fonksiyonu.
    """
    try:
        setup_logging()
        log_message("Sistem başlatıldı ve yetkiler devredildi.")

        # Django ortamını başlat
        django.setup()
        log_message("Django ortamı başarıyla başlatıldı.")

        # Chunk dosyalarını içeri aktar
        import_chunks()
        log_message("Tüm yükleme işlemleri başarıyla tamamlandı.")
    except Exception as e:
        print(f"Beklenmeyen bir hata oluştu: {e}")
        traceback.print_exc()
    finally:
        # Yetkileri geri ver
        subprocess.run(["sudo", "chown", "-R", "www-data:www-data", "/var/www/sapb1reportsv2/backend/logs"], check=True)
        log_message("Yetkiler geri verildi.")

if __name__ == "__main__":
    main()

