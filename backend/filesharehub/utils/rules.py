# backend/filesharehub/utils/rules.py
import os
from django.core.exceptions import PermissionDenied

# Dosya boyutlarını kontrol eden kurallar
MIN_FILE_SIZE = 0.0001 * 1024 * 1024  # 0.0001MB in bytes
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB in bytes

# Gizlenecek dosya uzantıları ve isimleri
HIDDEN_FILES = ['.DS_Store', 'Thumbs.db', '.lnk', '.Trash-1000', '.ini']  # .ini uzantısı eklendi

def is_valid_file_size(file_path):
    """
    Dosyanın boyutunu kontrol eder. Belirtilen aralığa uygunsa True döner, değilse False.
    """
    file_size = os.path.getsize(file_path)
    return MIN_FILE_SIZE <= file_size <= MAX_FILE_SIZE

def file_iterator(file_path, chunk_size=8192):
    """
    Büyük dosyaların iteratif olarak okunmasını sağlar.
    """
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk

def is_safe_path(base_path, requested_path):
    """
    İstenen dosya yolunun base_path ile başlamasını kontrol eder.
    """
    normalized_requested_path = os.path.normpath(requested_path)
    if not normalized_requested_path.startswith(base_path):
        raise PermissionDenied("Invalid path")

def should_hide_file(file_name):
    """
    Belirtilen dosya adının veya klasörün gizlenmesi gerekip gerekmediğini kontrol eder.
    """
    return any(file_name.endswith(ext) or file_name == ext for ext in HIDDEN_FILES)

def list_directory_contents(directory_path):
    """
    Dizin içindeki dosyaları ve alt dizinleri listeler.
    """
    contents = {"directories": [], "files": []}
    for item_name in os.listdir(directory_path):
        full_path = os.path.join(directory_path, item_name)

        # Gizli dosya veya klasör kontrolü
        if should_hide_file(item_name):
            continue

        if os.path.isdir(full_path):
            contents["directories"].append({"name": item_name})
        elif os.path.isfile(full_path):
            file_size = os.path.getsize(full_path)
            if is_valid_file_size(full_path):
                contents["files"].append({"name": item_name, "size": file_size})
    return contents
