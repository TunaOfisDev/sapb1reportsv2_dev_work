# backend/filesharehub_v2/utils/rules.py
"""Ortak kural yardımcıları

* Dosya boyutu limitleri (genel & görsel)
* Gizli / sistem dosyalarını filtreleme
* Path traversal güvenlik kontrolü
* Chunk bazlı okuma yardımcısı
"""

import os
from pathlib import Path
from typing import Iterable
from django.core.exceptions import PermissionDenied

# ---- Boyut Sınırları -------------------------------------------------------

MIN_FILE_SIZE = 0.0001 * 1024 * 1024  # 0.0001 MB ≈ 100 B
MAX_FILE_SIZE = 50 * 1024 * 1024      # 50 MB (her tür dosya için üst sınır)

# Görsel (thumbnail üretilecek) özel eşiği – sunucuyu yormamak için
MAX_IMAGE_SIZE = 25 * 1024 * 1024     # 25 MB


# ---- Gizli dosya / uzantılar ---------------------------------------------

HIDDEN_FILES: list[str] = [
    ".DS_Store", "Thumbs.db", ".lnk", ".Trash-1000", ".ini", ".tmp", ".bak",
]


# ---- Boyut Kontrolleri -----------------------------------------------------

def is_valid_file_size(file_path: str | Path) -> bool:
    """Genel dosya boyut kontrolü (0.0001 MB – 50 MB)."""
    size = Path(file_path).stat().st_size
    return MIN_FILE_SIZE <= size <= MAX_FILE_SIZE


def is_valid_image_size(size: int) -> bool:
    """Üretilmesi istenen görseller için 25 MB sınırı."""
    return size <= MAX_IMAGE_SIZE


# ---- Gizli Dosya Kontrolü --------------------------------------------------

def should_hide_file(file_name: str, hidden: Iterable[str] | None = None) -> bool:
    """Belirtilen dosya adına göre sistem/gizli olup olmadığını döner (case‑insensitive)."""
    hidden = hidden or HIDDEN_FILES
    name_lower = file_name.lower()
    return any(name_lower.endswith(h.lower()) if h.startswith(".") else name_lower == h.lower() for h in hidden)


# ---- Path Güvenliği --------------------------------------------------------

def is_safe_path(base_path: str | Path, requested_path: str | Path) -> None:
    """``requested_path`` alt klasör mü? Aksi halde ``PermissionDenied`` fırlatır."""
    base_path = Path(base_path).resolve()
    requested_path = Path(requested_path).resolve()
    if not str(requested_path).startswith(str(base_path)):
        raise PermissionDenied("Invalid path: outside permitted base directory")


# ---- Chunk Bazlı Okuma -----------------------------------------------------

def file_iterator(file_path: str | Path, chunk_size: int = 8192):
    """Büyük dosyaları belleğe almadan stream etmek için generator."""
    with open(file_path, "rb") as fp:
        while True:
            chunk = fp.read(chunk_size)
            if not chunk:
                break
            yield chunk
