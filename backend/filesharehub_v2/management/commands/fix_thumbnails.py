# backend/filesharehub_v2/management/commands/fix_thumbnails.py
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from filesharehub_v2.models.filerecord import FileRecord

class Command(BaseCommand):
    help = "Mevcut thumbnail dosyalarını tarar ve veritabanındaki eksik kayıtları düzeltir. Loglama yapmaz."

    def handle(self, *args, **options):
        thumbs_dir = os.path.join(settings.MEDIA_ROOT, "thumbs")

        if not os.path.exists(thumbs_dir):
            self.stderr.write(self.style.ERROR(f"[X] thumbs klasörü bulunamadı: {thumbs_dir}"))
            return

        self.stdout.write("Thumbnail düzeltme işlemi başlatıldı...")
        
        total = 0
        fixed = 0
        skipped = 0
        missing_db_record = 0
        invalid_name = 0

        for fname in os.listdir(thumbs_dir):
            if not fname.endswith(".jpg"):
                continue
            
            total += 1
            try:
                file_id = int(os.path.splitext(fname)[0])
                rel_path = os.path.join("thumbs", fname)

                try:
                    file_record = FileRecord.objects.get(file_id=file_id)
                    
                    if file_record.thumbnail_path != rel_path:
                        file_record.thumbnail_path = rel_path
                        file_record.save(update_fields=["thumbnail_path"])
                        fixed += 1
                    else:
                        skipped += 1

                except FileRecord.DoesNotExist:
                    # Log yerine konsola bilgi mesajı yaz
                    # self.stdout.write(f"   - DB kaydı yok, atlandı: {fname}")
                    missing_db_record += 1
                    continue

            except ValueError:
                # Log yerine konsola uyarı mesajı yaz
                # self.stdout.write(self.style.WARNING(f"   - Geçersiz dosya adı, atlandı: {fname}"))
                invalid_name += 1
                continue

        self.stdout.write(self.style.SUCCESS(f"\n✅ Tarama tamamlandı."))
        summary = (
            f"Toplam .jpg dosyası: {total}\n"
            f"Güncellenen DB kaydı: {fixed}\n"
            f"Zaten doğru olan: {skipped}\n"
            f"DB kaydı bulunamayan: {missing_db_record}\n"
            f"Geçersiz isme sahip: {invalid_name}"
        )
        self.stdout.write(summary)