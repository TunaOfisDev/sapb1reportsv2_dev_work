# backend/filesharehub_v2/utils/fs_scanner.py
"""Dizin tarayıcı – FileRecord senkronizasyonu

* Gizli dosyaları atlar
* 0.0001–50 MB aralığındaki dosyalara bakar
* Görsel uzantıları (.jpg/.png/…) tanır, **25 MB üzeri görselleri thumbnail’e sokmaz**
* `thumbnail_path` alanını kesinlikle silmez; sadece ilk yaratıldığında boş set edilir
"""

from __future__ import annotations

import mimetypes
import os
from datetime import datetime
from urllib.parse import unquote

from django.conf import settings
from django.core.exceptions import PermissionDenied

from filesharehub_v2.models.filerecord import FileRecord
from filesharehub_v2.tasks.generate_thumbnail import generate_thumbnail
from filesharehub_v2.utils import rules
from filesharehub_v2.utils.rules import is_safe_path, should_hide_file

from django.utils.timezone import make_aware

from django.utils.timezone import is_naive, make_aware
import logging

logger = logging.getLogger("filesharehubv2")

# Görsel kabul ettiğimiz uzantılar (TIFF hariç)
IMAGE_EXTS: set[str] = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}


# ---------------------------------------------------------------------------
# Yardımcılar
# ---------------------------------------------------------------------------



def _update_record_if_needed(record: FileRecord, **fields) -> None:
    """Yalnızca değişen alanları DB'ye kaydeder. Naive datetime'ı aware yapar. Sadece hata loglar."""
    dirty = False
    updates = {}

    for field, value in fields.items():
        # Yalnızca `modified` için timezone uyumsuzluğu kontrolü
        if field == "modified" and value and is_naive(value):
            try:
                value = make_aware(value)
            except Exception as e:
                logger.error(f"[TZError] file_id={record.file_id} – modified alanı aware yapılamadı: {e}")
                continue

        if getattr(record, field) != value:
            setattr(record, field, value)
            updates[field] = value
            dirty = True

    if dirty:
        try:
            record.save(update_fields=list(updates.keys()))
        except Exception as e:
            logger.error(f"[UpdateError] file_id={record.file_id} – güncelleme başarısız: {e}")



# ---------------------------------------------------------------------------
# Ana fonksiyon: list_directory
# ---------------------------------------------------------------------------

def list_directory(abs_path: str, rel_path: str = "") -> dict:
    """`abs_path` altındaki içerikleri okur, FileRecord ile senkronize eder."""

    files: list[dict] = []
    directories: list[dict] = []

    # Güvenlik – path traversal önlemi
    try:
        is_safe_path(settings.NETWORK_FOLDER_PATH, abs_path)
    except PermissionDenied as exc:
        print(f"[FSScannerError] Güvenlik hatası: {exc}")
        return {"directories": [], "files": []}

    try:
        with os.scandir(abs_path) as it:
            for entry in it:
                if should_hide_file(entry.name):
                    continue

                rel_item_path = os.path.join(rel_path, entry.name).replace("\\", "/")
                rel_item_path = unquote(rel_item_path)  # %20 → boşluk
                abs_item_path = os.path.join(abs_path, entry.name)
                file_id = FileRecord.compute_id(rel_item_path)

                item = {
                    "file_id": file_id,
                    "name": entry.name,
                    "path": rel_path,
                    "full_path": rel_item_path,
                    "is_dir": entry.is_dir(),
                    "modified": datetime.fromtimestamp(entry.stat().st_mtime).isoformat(),
                    "ext": "",
                    "size": None,
                    "is_image": False,
                    "thumbnail_path": "",
                }

                try:
                    # -------------------------------------------------------
                    # Klasör
                    # -------------------------------------------------------
                    if entry.is_dir():
                        FileRecord.objects.update_or_create(
                            file_id=file_id,
                            defaults={
                                "name": entry.name,
                                "path": rel_path,
                                "is_dir": True,
                                "modified": make_aware(datetime.fromtimestamp(entry.stat().st_mtime)),
                                "ext": "",
                                "size": None,
                                "is_image": False,
                            },
                        )
                        directories.append(item)
                        continue

                    # -------------------------------------------------------
                    # Dosya
                    # -------------------------------------------------------
                    if not rules.is_valid_file_size(abs_item_path):
                        continue  # çok küçük / çok büyük → listeye alma

                    item["size"] = entry.stat().st_size
                    item["ext"] = os.path.splitext(entry.name)[1][1:].lower()
                    mime_type, _ = mimetypes.guess_type(entry.name)
                    is_img_ext = "." + item["ext"] in IMAGE_EXTS
                    item["is_image"] = bool(mime_type and mime_type.startswith("image/")) or is_img_ext

                    # Büyük görseli thumbnail'e sokma
                    if item["is_image"] and not rules.is_valid_image_size(item["size"]):
                        item["is_image"] = False  # sadece dosya olarak listelensin

                    # Kaydı oluştur / güncelle
                    record, created = FileRecord.objects.get_or_create(
                        file_id=file_id,
                        defaults={
                            "name": entry.name,
                            "path": rel_path,
                            "is_dir": False,
                            "modified": make_aware(datetime.fromtimestamp(entry.stat().st_mtime)),
                            "ext": item["ext"],
                            "size": item["size"],
                            "is_image": item["is_image"],
                            "thumbnail_path": "" if item["is_image"] else None,
                        },
                    )

                    if not created:
                        _update_record_if_needed(
                            record,
                            name=entry.name,
                            path=rel_path,
                            modified=make_aware(datetime.fromtimestamp(entry.stat().st_mtime)),
                            ext=item["ext"],
                            size=item["size"],
                            is_image=item["is_image"],
                        )

                    # Thumbnail kuyruğu
                    if item["is_image"] and not record.thumbnail_path:
                        generate_thumbnail.delay(file_id)

                    item["thumbnail_path"] = record.thumbnail_path
                    files.append(item)

                except Exception as exc:
                    print(f"[FSScannerError] {entry.name} işlenirken hata: {exc}")
                    continue

    except Exception as exc:
        print(f"[FSScannerError] Genel hata: {exc}")
        return {"directories": [], "files": []}

    return {
        "directories": sorted(directories, key=lambda x: x["name"].lower()),
        "files": sorted(files, key=lambda x: x["name"].lower()),
    }


# ---------------------------------------------------------------------------
# Dış API – Celery task'lerinden çağrılır
# ---------------------------------------------------------------------------

def sync_directory(abs_path: str):
    """Tüm alt dizini tek sefer taramak için yardımcı fonksiyon."""
    rel_path = os.path.relpath(abs_path, settings.NETWORK_FOLDER_PATH).replace("\\", "/")
    list_directory(abs_path, rel_path)
