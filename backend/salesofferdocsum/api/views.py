# backend/salesofferdocsum/api/views.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from ..serializers import SalesOfferDetailSerializer
from ..models.salesofferdetail import SalesOfferDetail
from ..models.docsum import DocumentSummary
from ..utilities.data_fetcher import fetch_hana_db_data
from django.core.cache import cache
from loguru import logger
from django.conf import settings

API_NAME = 'salesofferdocsum'

class SalesOfferDetailListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        cache_key = f'{API_NAME}_sales_offer_details'
        cached_data = cache.get(cache_key)
        if not cached_data:
            details = SalesOfferDetail.objects.all()
            serializer = SalesOfferDetailSerializer(details, many=True)
            cache.set(cache_key, serializer.data, timeout=180)  # 3 dakika cache süresi
            return Response(serializer.data)
        return Response(cached_data)

class FetchHanaDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        token = request.headers.get('Authorization').split(' ')[1] if request.headers.get('Authorization') else None
        if not token:
            return Response({"error": "Token sağlanmadı."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            last_update_key = f'{API_NAME}_last_hana_update'
            last_update = cache.get(last_update_key) or timezone.now() - timedelta(days=30)
            data = fetch_hana_db_data(token, last_update=last_update)

            if not data:
                return Response({"error": "Veri alınamadı veya boş."}, status=status.HTTP_204_NO_CONTENT)

            updated_doc_numbers = set()

            with transaction.atomic():
                for item in data:
                    detail, created = SalesOfferDetail.objects.update_or_create(
                        uniq_detail_no=item['UniqDetailNo'],
                        defaults={
                            'belge_no': item['BelgeNo'],
                            'satici': item['Satici'],
                            'belge_tarih': item['BelgeTarih'],
                            'teslim_tarih': item['TeslimTarih'],
                            'belge_onay': item['BelgeOnay'],
                            'belge_durum': item['BelgeStatus'],
                            'iptal_edilen': item['IptalEdilen'],
                            'elle_kapatilan': item['ElleKapatilan'],
                            'siparise_aktarilan': item['SipariseAktarilan'],
                            'belge_aciklamasi': item['BelgeAciklamasi'],
                            'sevk_adres': item['SevkAdres'],
                            'musteri_kod': item['MusteriKod'],
                            'musteri_ad': item['MusteriAd'],
                            'satis_tipi': item['SatisTipi'],
                            'kalem_grup': item['KalemGrup'],
                            'satir_durum': item['SatirStatus'],
                            'satir_no': item['SatirNo'],
                            'kalem_kod': item['KalemKod'],
                            'kalem_tanimi': item['KalemTanimi'],
                            'birim': item['Birim'],
                            'siparis_miktari': item.get('SipMiktar', 0),
                            'liste_fiyat_dpb': item.get('ListeFiyatDPB', 0),
                            'detay_kur': item.get('DetayKur', 1),
                            'detay_doviz': item['DetayDoviz'],
                            'iskonto_oran': item.get('IskontoOran', 0),
                            'net_fiyat_dpb': item.get('NetFiyatDPB', 0),
                            'net_tutar_ypb': item.get('NetTutarYPB', 0),
                            'net_tutar_spb': item.get('NetTutarSPB', 0),
                            'brut_tutar_spb': item.get('BrutTutarSPB', 0),
                        }
                    )
                    updated_doc_numbers.add(item['BelgeNo'])

                for belge_no in updated_doc_numbers:
                    details = SalesOfferDetail.objects.filter(belge_no=belge_no)
                    summary = details.aggregate(
                        net_tutar_ypb=Sum('net_tutar_ypb'),
                        net_tutar_spb=Sum('net_tutar_spb'),
                        brut_tutar_spb=Sum('brut_tutar_spb')
                    )
                    
                    DocumentSummary.objects.update_or_create(
                        belge_no=belge_no,
                        defaults={
                            'satici': details.first().satici,
                            'satis_tipi': details.first().satis_tipi,
                            'belge_tarih': details.first().belge_tarih,
                            'teslim_tarih': details.first().teslim_tarih,
                            'belge_onay': details.first().belge_onay,
                            'belge_durum': details.first().belge_durum,
                            'iptal_edilen': details.first().iptal_edilen,
                            'elle_kapatilan': details.first().elle_kapatilan,
                            'siparise_aktarilan': details.first().siparise_aktarilan,
                            'belge_aciklamasi': details.first().belge_aciklamasi,
                            'musteri_kod': details.first().musteri_kod,
                            'musteri_ad': details.first().musteri_ad,
                            'sevk_adres': details.first().sevk_adres,
                            'net_tutar_ypb': summary['net_tutar_ypb'] or 0,
                            'net_tutar_spb': summary['net_tutar_spb'] or 0,
                            'brut_tutar_spb': summary['brut_tutar_spb'] or 0,
                        }
                    )

            cache.set(last_update_key, timezone.now())
            self.clear_cache_for_updated_documents(updated_doc_numbers)

            return Response({
                "message": "HANA DB verileri başarıyla güncellendi ve özetler oluşturuldu.",
                "updated_documents": len(updated_doc_numbers)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"HANA verileri çekerken ve özet hesaplaması yapılırken hata oluştu: {e}")
            return Response({
                "error": "Veri güncelleme işlemi sırasında bir hata oluştu.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def clear_cache_for_updated_documents(self, updated_belge_nos):
        cache.delete(f'{API_NAME}_sales_offer_details')
        cache.delete(f'{API_NAME}_document_summaries')

        for belge_no in updated_belge_nos:
            cache.delete(f'{API_NAME}_sales_offer_detail_{belge_no}')
            cache.delete(f'{API_NAME}_document_summary_{belge_no}')

        if len(updated_belge_nos) > settings.CACHE_CLEAR_THRESHOLD:
            cache.delete_pattern(f'{API_NAME}_*')
        
        logger.info(f"{API_NAME}: {len(updated_belge_nos)} belge için önbellek temizlendi.")