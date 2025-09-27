# backend/orderarchive/split_excel.py
import pandas as pd
import os

def split_excel_directory(input_dir, chunk_size=10000, output_dir="output_chunks"):
    """
    Bir dizindeki tüm Excel dosyalarını (xlsx) parçalar halinde böler.
    
    :param input_dir: Giriş dizini (Excel dosyalarının bulunduğu yer)
    :param chunk_size: Parça boyutu (satır sayısı)
    :param output_dir: Çıkış dizini (parçaların kaydedileceği yer)
    """
    # Çıkış dizinini oluştur
    os.makedirs(output_dir, exist_ok=True)

    # Dizindeki tüm .xlsx dosyalarını bul
    excel_files = [f for f in os.listdir(input_dir) if f.endswith('.xlsx')]

    if not excel_files:
        print("Dizinde hiç .xlsx dosyası bulunamadı.")
        return

    for file_index, file_name in enumerate(excel_files, start=1):
        file_path = os.path.join(input_dir, file_name)
        print(f"{file_index}/{len(excel_files)}: {file_name} işleniyor...")

        try:
            # Excel dosyasını yükle ve tarih formatını belirt
            data = pd.read_excel(file_path, dtype=str)  # Tüm verileri metin olarak oku

            # Tarih kolonlarını kontrol edip formatlarını düzelt
            date_columns = ["SipTarih", "TeslimTarih"]
            for col in date_columns:
                if col in data.columns:
                    data[col] = pd.to_datetime(data[col], errors="coerce").dt.strftime("%d.%m.%Y")

            # Dosyayı parçalara ayır
            for i, start_row in enumerate(range(0, len(data), chunk_size)):
                chunk = data.iloc[start_row:start_row + chunk_size]
                
                # Parça için dinamik dosya adı oluştur
                output_file = os.path.join(output_dir, f"{os.path.splitext(file_name)[0]}_chunk_{i + 1}.xlsx")
                chunk.to_excel(output_file, index=False, float_format="%.2f")
                print(f"{output_file} oluşturuldu.")

        except Exception as e:
            print(f"Hata oluştu: {file_name} - {e}")

# Kullanım
input_directory = "/home/user/uyum_siparis_arsiv/orderarchive_db"
output_directory = "/home/user/uyum_siparis_arsiv/orderarchive_chunks"
split_excel_directory(input_directory, chunk_size=10000, output_dir=output_directory)

