# backend/filesharehub_v2/management/commands/fix_thumbnails.py
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from filesharehub_v2.models.filerecord import FileRecord
from loguru import logger

class Command(BaseCommand):
    help = "Mevcut thumbnail dosyalarını tarar ve veritabanındaki eksik kayıtları düzeltir."

    def handle(self, *args, **options):
        thumbs_dir = os.path.join(settings.MEDIA_ROOT, "thumbs")

        if not os.path.exists(thumbs_dir):
            self.stderr.write(f"[X] thumbs klasörü yok: {thumbs_dir}")
            return

        total = 0
        fixed = 0
        skipped = 0
        missing = 0

        for fname in os.listdir(thumbs_dir):
            if not fname.endswith(".jpg"):
                continue
            try:
                file_id = int(os.path.splitext(fname)[0])
                total += 1
                rel_path = os.path.join("thumbs", fname)

                try:
                    file = FileRecord.objects.get(file_id=file_id)
                except FileRecord.DoesNotExist:
                    logger.warning(f"[fix_thumbnails] file_id={file_id} kaydı yok, atlandı.")
                    missing += 1
                    continue

                if file.thumbnail_path != rel_path:
                    file.thumbnail_path = rel_path
                    file.save(update_fields=["thumbnail_path"])
                    logger.success(f"[fix_thumbnails] Güncellendi: {file.name} → {rel_path}")
                    fixed += 1
                else:
                    skipped += 1

            except ValueError:
                logger.warning(f"[fix_thumbnails] Geçersiz dosya adı: {fname}")
                continue

        self.stdout.write(self.style.SUCCESS(f"\n✅ Tarama tamamlandı."))
        self.stdout.write(f"Toplam: {total}, Güncellenen: {fixed}, Zaten doğru: {skipped}, Eksik kayıt: {missing}")
