# backend/productconfigv2/utils/text_helpers.py (YENİ DOSYA)

def normalize_for_search(text: str) -> str:
    """
    Bir metni, veritabanında arama yapmaya uygun hale getirir.
    Tüm harfleri küçültür ve Türkçe karakterleri ASCII karşılıklarına çevirir.
    Örnek: "Büyük IŞIK, küçük ışık" -> "buyuk isik, kucuk isik"
    """
    if not text:
        return ""
    
    text = text.lower()
    
    turkish_map = {
        ord('ı'): 'i',
        ord('i'): 'i', # ikisini de 'i' yap
        ord('ş'): 's',
        ord('ğ'): 'g',
        ord('ü'): 'u',
        ord('ö'): 'o',
        ord('ç'): 'c',
    }
    
    return text.translate(turkish_map)