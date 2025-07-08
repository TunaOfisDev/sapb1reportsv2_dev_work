# backend/systemnotebook/management/commands/backfill_sha.py
from django.core.management.base import BaseCommand
from systemnotebook.models.system_note_model import SystemNote
import re

class Command(BaseCommand):
    help = "Başlıktan SHA yakalayıp commit_sha alanını doldurur."

    def handle(self, *args, **kwargs):
        pattern = re.compile(r"\b[0-9a-f]{7,40}\b")  # basit SHA regex
        qs = SystemNote.objects.filter(commit_sha__isnull=True, source="github")
        updated = 0
        for note in qs:
            m = pattern.search(note.content) or pattern.search(note.title)
            if m:
                note.commit_sha = m.group(0)
                note.save(update_fields=["commit_sha"])
                updated += 1
        self.stdout.write(self.style.SUCCESS(f"{updated} kayıt güncellendi."))
