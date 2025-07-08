# backend/filesharehub_v2/utils/samba_path.py
import os
import hashlib
from urllib.parse import unquote
from django.core.exceptions import SuspiciousFileOperation


def secure_join(base_dir: str, user_path: str) -> str:
    """
    Kullanıcıdan gelen path'i güvenli şekilde base_dir ile birleştirir.
    Path traversal saldırılarını ve base dışı erişimi engeller.
    """
    if not user_path.strip():
        return os.path.abspath(base_dir)

    # URL decode → trim slashes
    cleaned_path = unquote(user_path).strip("/")

    combined_path = os.path.normpath(os.path.join(base_dir, cleaned_path))

    abs_base = os.path.abspath(base_dir)
    abs_target = os.path.abspath(combined_path)

    if not abs_target.startswith(abs_base):
        raise SuspiciousFileOperation("Yetkisiz dizin erişimi tespit edildi.")

    return abs_target


def compute_file_id(rel_path: str) -> int:
    """
    Göreli path'ten SHA1 hash'e dayalı sabit `file_id` üretir.
    Bu fonksiyon, tüm backend boyunca kullanılmalıdır.
    """
    return int(hashlib.sha1(rel_path.encode()).hexdigest(), 16) % (10**9)
