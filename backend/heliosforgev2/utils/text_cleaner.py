# backend/heliosforgev2/utils/text_cleaner.py

import re
import unicodedata

def clean_text(text: str) -> str:
    """
    Temel metin temizleme:
    - Unicode normalize
    - Satır sonu ve fazla boşlukları temizler
    - Garip PDF karakterlerini düzeltir
    """
    if not text:
        return ""

    # Unicode normalize (örn: latin-1 -> NFC)
    text = unicodedata.normalize("NFKC", text)

    # Boşlukları sadeleştir
    text = re.sub(r'\s+', ' ', text)

    # Ön/son boşluk temizle
    return text.strip()


def is_meaningful(text: str, min_length: int = 5) -> bool:
    """
    Chunk'a dahil edilecek kadar anlamlı mı?
    - Sadece noktalama içeriyorsa false
    - Minimum uzunluk kontrolü
    """
    if not text or len(text.strip()) < min_length:
        return False
    if re.fullmatch(r"[.,;:\-–!?() ]*", text):
        return False
    return True


def remove_duplicate_spaces(text: str) -> str:
    """
    Art arda gelen boşlukları tek boşlukla değiştirir
    """
    return re.sub(r'\s{2,}', ' ', text)


def normalize_quotes(text: str) -> str:
    """
    Akıllı tırnakları (typographic quotes) düz tırnağa çevir
    """
    return text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
