# backend/customersales/api/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db import transaction
from django.db.models import Sum, Q, DecimalField
from decimal import Decimal
from django.utils import timezone
from django.db.models.functions import Coalesce # İyileştirme için eklendi
import logging # İyileştirme için eklendi

from ..models import CustomerSalesRawData
from ..api.serializers import CustomerSalesDataSerializer, CustomerSalesSummarySerializer
from ..utils.data_fetcher import fetch_raw_sales_data_from_hana

# Loglama için logger oluşturuluyor
logger = logging.getLogger(__name__)

def _safe_decimal(value):
    if value in (None, '', 'null', 'NULL'): return 0.0
    try: return float(value)
    except (ValueError, TypeError): return 0.0


class CustomerSalesDataView(APIView):
    """
    ✅ Raporlama için kullanılır.
    Filtrelenmiş veriyi, filtre seçeneklerini, özet toplamları ve
    son güncellenme zamanını PostgreSQL'den tek seferde getirir.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        base_queryset = CustomerSalesRawData.objects.all()
        # ... (filtreleme kodlarınız burada aynı kalıyor) ...
        filters = Q()
        if request.query_params.getlist('satici'):
            filters &= Q(satici__in=request.query_params.getlist('satici'))
        if request.query_params.getlist('satis_tipi'):
            filters &= Q(satis_tipi__in=request.query_params.getlist('satis_tipi'))
        if request.query_params.getlist('cari_grup'):
            filters &= Q(cari_grup__in=request.query_params.getlist('cari_grup'))
        
        filtered_queryset = base_queryset.filter(filters)

        # ... (summary_data ve filter_options kodlarınız burada aynı kalıyor) ...
        summary_data = filtered_queryset.aggregate(
            ToplamNetSPB_EUR=Coalesce(Sum('toplam_net_spb_eur'), Decimal('0.0'), output_field=DecimalField()),
            # ... diğer aylar
            Aralık=Coalesce(Sum('aralik'), Decimal('0.0'), output_field=DecimalField())
        )
        saticilar = sorted(base_queryset.values_list('satici', flat=True).distinct())
        satis_tipleri = sorted(base_queryset.values_list('satis_tipi', flat=True).distinct())
        cari_gruplar = sorted(base_queryset.values_list('cari_grup', flat=True).distinct())
        filter_options = {
            "saticilar": saticilar,
            "satisTipleri": satis_tipleri,
            "cariGruplar": cari_gruplar,
        }
        
        # YENİ EKLENEN BÖLÜM: SON GÜNCELLEME ZAMANINI ALMA
        last_update_str = "Veri henüz güncellenmemiş."
        # Tablodaki en yeni kaydı created_at alanına göre bul
        last_sync_record = base_queryset.order_by('-created_at').first()
        if last_sync_record:
            # Kaydın zaman damgasını projenin yerel saat dilimine (Europe/Istanbul) çevir
            local_time = timezone.localtime(last_sync_record.created_at)
            # İstenen formata çevir
            last_update_str = local_time.strftime("%d.%m.%Y %H:%M")
        
        data_serializer = CustomerSalesDataSerializer(filtered_queryset.order_by('-toplam_net_spb_eur')[:5000], many=True)
        summary_serializer = CustomerSalesSummarySerializer(summary_data)

        # YENİ EKLENEN BÖLÜM: 'lastUpdated' ALANINI YANITA EKLEME
        response_payload = {
            "lastUpdated": last_update_str,
            "data": data_serializer.data,
            "summary": summary_serializer.data,
            "filterOptions": filter_options
        }
        return Response(response_payload)

class FetchHanaDataView(APIView):
    """
    ✅ Veri senkronizasyonu için kullanılır.
    Kullanıcının "HANA Veri Çek" butonuna basmasıyla tetiklenir.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logger.info("HANA'dan veri çekme işlemi kullanıcı tarafından başlatıldı.")
        token = str(request.auth)
        
        raw_data = fetch_raw_sales_data_from_hana(token)
        if raw_data is None:
            logger.error("HANA'dan veri alınamadı. İşlem durduruldu.")
            return Response({"error": "HANA'dan veri alınamadı."}, status=status.HTTP_502_BAD_GATEWAY)

        logger.info(f"HANA'dan {len(raw_data)} kayıt çekildi. Veritabanına kaydediliyor...")

        objects_to_create = [
            CustomerSalesRawData(
                satici=row.get("Satici", ""), satis_tipi=row.get("SatisTipi", ""),
                cari_grup=row.get("CariGrup", ""), musteri_kodu=row.get("MusteriKodu", ""),
                musteri_adi=row.get("MusteriAdi", ""),
                toplam_net_spb_eur=_safe_decimal(row.get("ToplamNetSPB_EUR")),
                ocak=_safe_decimal(row.get("Ocak")), subat=_safe_decimal(row.get("Şubat")),
                mart=_safe_decimal(row.get("Mart")), nisan=_safe_decimal(row.get("Nisan")),
                mayis=_safe_decimal(row.get("Mayıs")), haziran=_safe_decimal(row.get("Haziran")),
                temmuz=_safe_decimal(row.get("Temmuz")), agustos=_safe_decimal(row.get("Ağustos")),
                eylul=_safe_decimal(row.get("Eylül")), ekim=_safe_decimal(row.get("Ekim")),
                kasim=_safe_decimal(row.get("Kasım")), aralik=_safe_decimal(row.get("Aralık"))
            ) for row in raw_data
        ]

        try:
            with transaction.atomic():
                CustomerSalesRawData.objects.all().delete()
                CustomerSalesRawData.objects.bulk_create(objects_to_create, batch_size=1000)

            logger.info(f"{len(objects_to_create)} kayıt başarıyla PostgreSQL'e aktarıldı.")
            return Response({"message": f"{len(objects_to_create)} kayıt başarıyla içe aktarıldı."}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"Veritabanına kaydederken hata oluştu: {str(e)}")
            return Response({"error": f"Veritabanına kaydederken hata oluştu: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)