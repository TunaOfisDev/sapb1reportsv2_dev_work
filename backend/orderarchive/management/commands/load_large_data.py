# backend/orderarchive/management/commands/load_large_data.py
import os
from django.core.management.base import BaseCommand
from ...utils.import_large_file import import_large_file


class Command(BaseCommand):
    help = "Büyük veri dosyasını parça parça yükler."

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help="Yüklenecek Excel dosyasının tam yolu")
        parser.add_argument('--chunk_size', type=int, default=10000, help="Parça boyutu")

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        chunk_size = kwargs['chunk_size']

        if not os.path.exists(file_path):
            self.stderr.write(f"Hata: {file_path} bulunamadı.")
            return

        self.stdout.write(f"Veri yükleniyor: {file_path}")
        import_large_file(file_path, chunk_size)
        self.stdout.write(f"Yükleme tamamlandı: {file_path}")
