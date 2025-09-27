# backend/filesharehub_v2/utils/fs_scanner.py (Temiz Versiyon)

from __future__ import annotations
import mimetypes
import os
from datetime import datetime
from urllib.parse import unquote
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.utils.timezone import is_naive, make_aware
from filesharehub_v2.models.filerecord import FileRecord
from filesharehub_v2.tasks.generate_thumbnail import generate_thumbnail
from filesharehub_v2.utils import rules
from filesharehub_v2.utils.rules import is_safe_path, should_hide_file

IMAGE_EXTS: set[str] = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}

def _update_record_if_needed(record: FileRecord, **fields) -> None:
    dirty = False
    updates = {}
    for field, value in fields.items():
        if field == "modified" and value and is_naive(value):
            try: value = make_aware(value)
            except Exception: continue
        if getattr(record, field) != value:
            setattr(record, field, value)
            updates[field] = value
            dirty = True
    if dirty:
        try: record.save(update_fields=list(updates.keys()))
        except Exception as e: print(f"[FSScanner-UpdateError] file_id={record.file_id} – güncelleme başarısız: {e}")

def list_directory(abs_path: str, rel_path: str = "") -> dict:
    files: list[dict] = []
    directories: list[dict] = []
    try: is_safe_path(settings.NETWORK_FOLDER_PATH, abs_path)
    except PermissionDenied as exc:
        print(f"[FSScanner-SecurityError] Güvenlik hatası: {exc}")
        return {"directories": [], "files": []}
    try:
        with os.scandir(abs_path) as it:
            for entry in it:
                if should_hide_file(entry.name): continue
                try:
                    rel_item_path = os.path.join(rel_path, entry.name).replace("\\", "/")
                    rel_item_path = unquote(rel_item_path)
                    abs_item_path = os.path.join(abs_path, entry.name) # Bu satır hatayı düzeltmek için önemli
                    file_id = FileRecord.compute_id(rel_item_path)
                    entry_stat = entry.stat()
                    modified_dt = make_aware(datetime.fromtimestamp(entry_stat.st_mtime))
                    
                    if entry.is_dir():
                        FileRecord.objects.update_or_create(file_id=file_id, defaults={"name": entry.name, "path": rel_path, "is_dir": True, "modified": modified_dt})
                        directories.append({"name": entry.name})
                        continue

                    # HATA BURADAYDI: Fonksiyona sayı yerine dosya yolu gönderiyoruz.
                    if not rules.is_valid_file_size(abs_item_path):
                        continue

                    ext = os.path.splitext(entry.name)[1][1:].lower()
                    mime_type, _ = mimetypes.guess_type(entry.name)
                    is_img = bool(mime_type and mime_type.startswith("image/")) or f".{ext}" in IMAGE_EXTS
                    if is_img and not rules.is_valid_image_size(entry_stat.st_size): is_img = False
                    
                    record, created = FileRecord.objects.get_or_create(file_id=file_id, defaults={"name": entry.name, "path": rel_path, "is_dir": False, "modified": modified_dt, "ext": ext, "size": entry_stat.st_size, "is_image": is_img, "thumbnail_path": "" if is_img else None})
                    if not created: _update_record_if_needed(record, name=entry.name, path=rel_path, modified=modified_dt, ext=ext, size=entry_stat.st_size, is_image=is_img)
                    if is_img and not record.thumbnail_path: generate_thumbnail.delay(file_id)
                    
                    files.append({"name": entry.name})
                except Exception as exc: print(f"[FSScanner-ItemError] {entry.name} işlenirken hata: {exc}")
    except Exception as exc:
        print(f"[FSScanner-GeneralError] 'os.scandir' hatası: {exc}")
        return {"directories": [], "files": []}
    return {"directories": directories, "files": files}

def sync_directory(abs_path: str):
    rel_path = os.path.relpath(abs_path, settings.NETWORK_FOLDER_PATH).replace("\\", "/")
    if rel_path == ".": rel_path = ""
    list_directory(abs_path, rel_path)