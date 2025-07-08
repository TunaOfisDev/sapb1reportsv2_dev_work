# backend/heliosforgev2/utils/file_ops.py

import os
import uuid
from pathlib import Path

def ensure_dir_exists(path: str) -> None:
    """
    Belirtilen klasör yoksa oluştur.
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def save_text_to_file(content: str, output_path: str) -> None:
    """
    Verilen metni UTF-8 olarak dosyaya yazar.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)


def generate_unique_filename(extension: str = ".json", prefix: str = "") -> str:
    """
    Benzersiz bir dosya adı üret. Örn: chunk_ab12ef34.json
    """
    uid = uuid.uuid4().hex[:8]
    return f"{prefix}{uid}{extension}"


def build_storage_path(base_dir: str, filename: str) -> str:
    """
    Belirtilen klasöre dosya adını ekleyerek tam path üretir.
    """
    return os.path.join(base_dir, filename)


