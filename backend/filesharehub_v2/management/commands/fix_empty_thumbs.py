# backend/filesharehub_v2/management/commands/fix_empty_thumbs.py
from django.core.management.base import BaseCommand
from filesharehub_v2.models.filerecord import FileRecord
from pathlib import Path
from django.conf import settings

class Command(BaseCommand):
    help = "thumbnail_path='' olup fiziksel dosyası bulunan kayıtları onarır"

    def handle(self, *args, **kwargs):
        qs = FileRecord.objects.filter(is_image=True, thumbnail_path="")
        repaired = 0
        for rec in qs:
            thumb = Path(settings.MEDIA_ROOT) / "thumbs" / f"{rec.file_id}.jpg"
            if thumb.exists():
                rec.thumbnail_path = thumb.relative_to(settings.MEDIA_ROOT).as_posix()
                rec.save(update_fields=["thumbnail_path"])
                repaired += 1
        self.stdout.write(self.style.SUCCESS(f"✔  {repaired} kayıt onarıldı"))
