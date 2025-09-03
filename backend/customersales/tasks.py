# backend/customersales/tasks.py

from celery import shared_task
from django.db import transaction
from django.contrib.auth import get_user_model

# Gerekli fonksiyonları ve modelleri içe aktarıyoruz
from .utils.data_fetcher import fetch_raw_sales_data_from_hana
from .models import CustomerSalesRawData
from sapreports.jwt_utils import get_token_for_user # Sistemsel token almak için bir yol (varsayımsal)

import logging

logger = logging.getLogger(__name__)

def get_system_auth_token():
    """
    Arka plan görevleri için geçerli bir JWT token alır.
    Bu, 'sistem kullanıcısı' gibi özel bir kullanıcı üzerinden yapılmalıdır.
    """
    # NOT: Bu fonksiyonu kendi projenizdeki bir sistem kullanıcısına göre
    # uyarlamanız gerekmektedir. Örnek olarak 'system_user@tunacelik.com.tr'
    # kullanılmıştır.
    try:
        User = get_user_model()
        system_user = User.objects.get(email='system_user@tunacelik.com.tr')
        token = get_token_for_user(system_user)
        return token.get('access')
    except User.DoesNotExist:
        logger.error("Sistem kullanıcısı bulunamadı! Veri çekme görevi token alamadı.")
        return None


@shared_task(name="customersales.refresh_hana_data")
def refresh_sales_data_from_hana():
    """
    HANA veritabanından ham satış verilerini çeker ve yerel PostgreSQL
    veritabanındaki CustomerSalesRawData tablosunu günceller.
    Bu görev, Celery Beat tarafından periyodik olarak çalıştırılmalıdır.
    """
    logger.info("Müşteri Satış verilerini HANA'dan yenileme görevi başladı.")

    # 1. Adım: Arka plan görevi için bir token al.
    auth_token = get_system_auth_token()
    if not auth_token:
        return "Görev token alamadığı için durduruldu."

    # 2. Adım: HANA'dan tüm ham veriyi çek.
    raw_data = fetch_raw_sales_data_from_hana(auth_token)

    if raw_data is None:
        logger.error("HANA'dan veri çekilemedi. Görev sonlandırılıyor.")
        return "HANA'dan veri çekme başarısız."

    logger.info(f"{len(raw_data)} adet kayıt HANA'dan başarıyla çekildi.")

    # 3. Adım: Veriyi PostgreSQL'e kaydet.
    try:
        # Veritabanı işlemlerini bir transaction içinde yaparak bütünlüğü sağlıyoruz.
        with transaction.atomic():
            # 3a. Eski veriyi tamamen temizle.
            logger.info("PostgreSQL'deki eski veriler siliniyor...")
            CustomerSalesRawData.objects.all().delete()

            # 3b. Gelen yeni veriyi modele uygun hale getir ve toplu olarak ekle.
            # bulk_create, tek tek .create() yapmaktan kat kat daha hızlıdır.
            logger.info("Yeni veriler PostgreSQL'e toplu olarak ekleniyor...")
            
            # API'den gelen anahtarları modeldeki alan adlarıyla eşleştiriyoruz (büyük/küçük harf)
            # Eğer data_fetcher'dan gelen key'ler model ile aynı ise bu adıma gerek yok.
            # Örnek: {'Satici': '...'} -> {'satici': '...'}
            objects_to_create = [
                CustomerSalesRawData(
                    satici=row.get('Satici', ''),
                    satis_tipi=row.get('SatisTipi', ''),
                    cari_grup=row.get('CariGrup', ''),
                    musteri_kodu=row.get('MusteriKodu', ''),
                    musteri_adi=row.get('MusteriAdi', ''),
                    toplam_net_spb_eur=row.get('ToplamNetSPB_EUR', 0),
                    ocak=row.get('Ocak', 0),
                    subat=row.get('Şubat', 0),
                    mart=row.get('Mart', 0),
                    nisan=row.get('Nisan', 0),
                    mayis=row.get('Mayıs', 0),
                    haziran=row.get('Haziran', 0),
                    temmuz=row.get('Temmuz', 0),
                    agustos=row.get('Ağustos', 0),
                    eylul=row.get('Eylül', 0),
                    ekim=row.get('Ekim', 0),
                    kasim=row.get('Kasım', 0),
                    aralik=row.get('Aralık', 0)
                ) for row in raw_data
            ]
            CustomerSalesRawData.objects.bulk_create(objects_to_create, batch_size=1000)

        logger.info(f"{len(objects_to_create)} adet yeni kayıt PostgreSQL'e başarıyla eklendi.")
        return f"Görev başarıyla tamamlandı. {len(objects_to_create)} kayıt işlendi."

    except Exception as e:
        logger.error(f"PostgreSQL'e veri yazılırken bir hata oluştu: {e}")
        return f"Veritabanı hatası: {e}"