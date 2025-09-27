# backend/filesharehub/tasks.py
from celery import shared_task
import os
from django.utils import timezone

MAX_FILES_PER_TASK = 1000

@shared_task
def scan_directory_task(directory_path):
    from .models.models import Directory, FileRecord
    from django.db import transaction

    directory = Directory.get_or_create_directory(directory_path)
    file_records = []
    file_count = 0

    for root, dirs, filenames in os.walk(directory_path):
        for filename in filenames:
            if file_count >= MAX_FILES_PER_TASK:
                # Kalan dosyalar için yeni bir görev başlat
                scan_directory_task.delay(directory_path)
                break
            full_path = os.path.join(root, filename)
            relative_path = os.path.relpath(full_path, directory_path)
            file_size = os.path.getsize(full_path)
            last_modified = timezone.make_aware(timezone.datetime.fromtimestamp(os.path.getmtime(full_path)))

            file_records.append(FileRecord(
                directory=directory,
                filename=relative_path,
                file_path=full_path,
                size=file_size,
                last_modified=last_modified
            ))
            file_count += 1

        if file_count >= MAX_FILES_PER_TASK:
            break

    with transaction.atomic():
        FileRecord.objects.bulk_create(file_records, update_conflicts=True, update_fields=['file_path', 'size', 'last_modified'], unique_fields=['directory', 'filename'])

    directory.last_scanned = timezone.now()
    directory.save()

@shared_task(name="filesharehub.tasks.scan_and_save_files")
def scan_and_save_files():
    from .models.models import Directory
    from .tasks import scan_directory_task

    directories = Directory.objects.all()  # is_active filtresi kaldırıldı
    for directory in directories:
        scan_directory_task.delay(directory.path)