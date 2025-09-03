# backend/customersales/services/customersales_services.py

from typing import Dict, Any, List, Optional
from ..utils import data_fetcher

# -----------------------------------------------------------------------------
# Servis Katmanı (Business Logic Layer)
#
# Bu modül, `customersales` uygulamasının iş mantığını içerir. API view'lerinden
# gelen istekleri alır, `data_fetcher` gibi yardımcı modülleri kullanarak
# gerekli verileri toplar, veriler üzerinde ek işlemler (dönüşüm, birleştirme,
# hesaplama vb.) yapar ve sonucu view katmanına döndürür.
#
# Bu katman, view'lerin temiz kalmasını ve sadece HTTP istek/yanıt
# döngüsüyle ilgilenmesini sağlar.
# -----------------------------------------------------------------------------


def get_report_data_service(token: str, filters: Optional[Dict[str, Any]] = None) -> Optional[List[Dict[str, Any]]]:
    """
    "Müşteri Bazlı Satış Özeti" raporunun ana verilerini getiren servis fonksiyonu.

    Args:
        token (str): Kullanıcı kimlik doğrulaması için JWT.
        filters (dict, optional): Veriyi süzmek için kullanılacak filtreler.

    Returns:
        list[dict] or None: Rapor verisi başarıyla alınırsa bir liste,
                            aksi takdirde None döner.
    """
    print("Servis katmanı: Rapor verisi getiriliyor...")

    # 1. Adım: Veri getirme katmanından ham veriyi al.
    report_data = data_fetcher.fetch_report_data(token, filters)

    # 2. Adım: İş mantığı ve veri dönüşümü (Gerekirse)
    # Bu bölümde, veritabanından gelen ham veri üzerinde ek işlemler yapılabilir.
    # Örnek: Belirli alanlara göre ek hesaplamalar yapmak, veriyi farklı bir
    # kaynaktan gelen veriyle birleştirmek veya formatlamak.
    # Şu anki ihtiyaç için doğrudan geçiş yapıyoruz.
    if report_data is None:
        print("Servis katmanı: Veri alınamadı.")
        return None

    # Örnek bir dönüşüm/zenginleştirme:
    # for row in report_data:
    #     row['YillikOrtalama'] = row['ToplamNetSPB_EUR'] / 12

    print(f"Servis katmanı: {len(report_data)} satır veri başarıyla işlendi.")
    return report_data


def get_filter_options_service(token: str) -> Optional[Dict[str, List[str]]]:
    """
    Raporun dinamik filtreleri için kullanılabilir seçenekleri getiren servis.

    Args:
        token (str): Kullanıcı kimlik doğrulaması için JWT.

    Returns:
        dict or None: Filtre seçenekleri başarıyla alınırsa bir sözlük,
                      aksi takdirde None döner.
    """
    print("Servis katmanı: Filtre seçenekleri getiriliyor...")
    
    # Veri getirme katmanından filtre seçeneklerini al.
    filter_options = data_fetcher.fetch_filter_options(token)

    # Gerekirse burada filtre seçenekleri üzerinde değişiklik yapılabilir.
    # Örnek: 'Tanımsız' seçeneğini listenin sonuna taşımak.
    if filter_options and 'saticilar' in filter_options:
        if 'Tanımsız' in filter_options['saticilar']:
            filter_options['saticilar'].remove('Tanımsız')
            filter_options['saticilar'].append('Tanımsız')

    return filter_options


def get_report_summary_service(token: str) -> Optional[Dict[str, Any]]:
    """
    Raporun statik genel özet (grand total) verilerini getiren servis.

    Args:
        token (str): Kullanıcı kimlik doğrulaması için JWT.

    Returns:
        dict or None: Özet verisi başarıyla alınırsa bir sözlük,
                      aksi takdirde None döner.
    """
    print("Servis katmanı: Rapor özeti getiriliyor...")
    
    # Veri getirme katmanından özet verisini al.
    summary_data = data_fetcher.fetch_report_summary(token)
    
    # Gerekirse burada özet verileri üzerinde ek hesaplamalar yapılabilir.
    # Örnek: Yılın biten kısmına göre satış hedefi karşılama oranı hesaplamak.
    
    return summary_data