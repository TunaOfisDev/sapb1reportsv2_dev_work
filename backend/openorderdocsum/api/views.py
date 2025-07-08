# backend/openorderdocsum/api/views.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.db.models import Sum
from ..serializers import OpenOrderDetailSerializer
from ..models.openorderdeail import OpenOrderDetail
from ..models.docsum import DocumentSummary
from ..utilities.data_fetcher import fetch_hana_db_data
from django.core.cache import cache
from loguru import logger

class OpenOrderDetailListView(APIView):
    """
    OpenOrderDetail modelinin tüm kayıtlarını listeler.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        cached_data = cache.get('open_order_details')
        if not cached_data:
            details = OpenOrderDetail.objects.all()
            serializer = OpenOrderDetailSerializer(details, many=True)
            cache.set('open_order_details', serializer.data, timeout=10)  # 30 saniye cache süresi
            return Response(serializer.data)
        return Response(cached_data)


class FetchHanaDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        token = request.headers.get('Authorization').split(' ')[1] if request.headers.get('Authorization') else None
        if not token:
            return Response({"error": "Token sağlanmadı."}, status=status.HTTP_401_UNAUTHORIZED)

        data = fetch_hana_db_data(token)
        if not data:
            return Response({"error": "Veri alınamadı veya boş."}, status=status.HTTP_204_NO_CONTENT)

        try:
            with transaction.atomic():
                # Mevcut tüm OpenOrderDetail kayıtlarını sil
                OpenOrderDetail.objects.all().delete()

                # Yeni verileri oluştur
                for item in data:
                    OpenOrderDetail.objects.create(
                        uniq_detail_no=item['UniqDetailNo'],
                        belge_no=item['BelgeNo'],
                        satici=item['Satici'],
                        belge_tarih=item['BelgeTarih'],
                        teslim_tarih=item['TeslimTarih'],
                        belge_onay=item['BelgeOnay'],
                        belge_durum=item['BelgeStatus'],
                        sevk_adres=item['SevkAdres'],
                        musteri_kod=item['MusteriKod'],
                        musteri_ad=item['MusteriAd'],
                        satis_tipi=item['SatisTipi'],
                        kalem_grup=item['KalemGrup'],
                        satir_durum=item['SatirStatus'],
                        kalem_kod=item['KalemKod'],
                        kalem_tanimi=item['KalemTanimi'],
                        birim=item['Birim'],
                        siparis_miktari=item.get('SipMiktar', 0),
                        sevk_miktari=item.get('SevkMiktar', 0),
                        kalan_miktar=item.get('KalanMiktar', 0),
                        liste_fiyat_dpb=item.get('ListeFiyatDPB', 0),
                        detay_kur=item.get('DetayKur', 1),
                        detay_doviz=item['DetayDoviz'],
                        iskonto_oran=item.get('IskontoOran', 0),
                        net_fiyat_dpb=item.get('NetFiyatDPB', 0),
                        net_tutar_ypb=item.get('NetTutarYPB', 0),
                        acik_net_tutar_ypb=item.get('AcikNetTutarYPB', 0),
                        acik_net_tutar_spb=item.get('AcikNetTutarSPB', 0),
                        girsberger_net_tutar_ypb=item.get('GirsbergerNetTutarYPB', 0),
                        mamul_net_tutar_ypb=item.get('MamulNetTutarYPB', 0),
                        ticari_net_tutar_ypb=item.get('TicariNetTutarYPB', 0),
                        nakliye_net_tutar_ypb=item.get('NakliyeNetTutarYPB', 0),
                        montaj_net_tutar_ypb=item.get('MontajNetTutarYPB', 0)
                  )

                 # Veri güncellendikten sonra özetleri hesapla
                all_details = OpenOrderDetail.objects.values(
                    'belge_no', 'satici', 'belge_tarih', 'teslim_tarih', 'belge_onay', 
                    'belge_durum', 'musteri_kod', 'musteri_ad', 'sevk_adres', 'satis_tipi'
                ).annotate(
                    net_tutar_ypb=Sum('net_tutar_ypb'),
                    acik_net_tutar_ypb=Sum('acik_net_tutar_ypb'),
                    acik_net_tutar_spb=Sum('acik_net_tutar_spb'),
                    girsberger_net_tutar_ypb=Sum('girsberger_net_tutar_ypb'),
                    mamul_net_tutar_ypb=Sum('mamul_net_tutar_ypb'),
                    ticari_net_tutar_ypb=Sum('ticari_net_tutar_ypb'),
                    nakliye_net_tutar_ypb=Sum('nakliye_net_tutar_ypb'),
                    montaj_net_tutar_ypb=Sum('montaj_net_tutar_ypb')
                )

                # Mevcut özet kayıtlarını temizle
                DocumentSummary.objects.all().delete()

                # Hesaplanan özet bilgileri DocumentSummary modeline kaydet
                for detail in all_details:
                    DocumentSummary.objects.create(
                        belge_no=detail['belge_no'],
                        satici=detail.get('satici', ''),  # 'satici' anahtarı yoksa boş string döner
                        satis_tipi=detail.get('satis_tipi', ''), 
                        belge_tarih=detail.get('belge_tarih'),  # Doğru formatta tarih beklenir, kontrol edilmeli
                        teslim_tarih=detail.get('teslim_tarih'),  # Doğru formatta tarih beklenir, kontrol edilmeli
                        belge_onay=detail.get('belge_onay', ''),
                        belge_durum=detail.get('belge_durum', ''),
                        musteri_kod=detail.get('musteri_kod', ''),
                        musteri_ad=detail.get('musteri_ad', ''),
                        sevk_adres=detail.get('sevk_adres', ''),  # Eğer 'sevk_adres' anahtarı yoksa boş string döner
                        net_tutar_ypb=detail.get('net_tutar_ypb', 0.0),
                        acik_net_tutar_ypb=detail.get('acik_net_tutar_ypb', 0.0),
                        acik_net_tutar_spb=detail.get('acik_net_tutar_spb', 0.0),
                        girsberger_net_tutar_ypb=detail.get('girsberger_net_tutar_ypb', 0.0),
                        mamul_net_tutar_ypb=detail.get('mamul_net_tutar_ypb', 0.0),
                        ticari_net_tutar_ypb=detail.get('ticari_net_tutar_ypb', 0.0),
                        nakliye_net_tutar_ypb=detail.get('nakliye_net_tutar_ypb', 0.0),
                        montaj_net_tutar_ypb=detail.get('montaj_net_tutar_ypb', 0.0)
                    )


                # Önbelleği temizle
                cache.delete('open_order_details')
                return Response({"message": "HANA DB verileri başarıyla güncellendi ve özetler oluşturuldu."}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"HANA verileri çekerken ve özet hesaplaması yapılırken hata oluştu: {e}")
            return Response({
                "error": "Veri güncelleme işlemi sırasında bir hata oluştu.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)