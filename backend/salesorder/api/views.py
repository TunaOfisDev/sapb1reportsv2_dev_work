# backend/salesorder/api/views.py

from ..models.models import SalesOrder
from ..serializers import SalesOrderSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.core.cache import cache
from django.conf import settings
from django.http import HttpResponse
from tablib import Dataset
from import_export.formats.base_formats import XLSX
from ..utilities.data_fetcher import fetch_hana_db_data

class SalesOrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        # 'sales_orders_list' için bir cache anahtarı oluşturuluyor
        cache_key = 'sales_orders_list'
        # CACHE_TTL değerini settings.py dosyasından alıyoruz
        cache_time = settings.CACHE_TTL

        try:
            # Cache'ten 'sales_orders_list' verisini almayı dene
            sales_orders = cache.get(cache_key)
            if not sales_orders:
                # Eğer cache boş ise, veritabanından tüm satış siparişlerini çek
                sales_orders = SalesOrder.objects.all()
                # Verileri serialize et
                serializer = SalesOrderSerializer(sales_orders, many=True)
                # Verileri cache'e ekle
                cache.set(cache_key, serializer.data, cache_time)
                # Serialize edilmiş verileri response olarak dön
                return Response(serializer.data)
            else:
                # Cache'te veri varsa, bu verileri dön
                return Response(sales_orders)
        except Exception as e:
            # Herhangi bir hata oluşursa, hatayı logla ve 500 hata kodu ile dön
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FetchHanaDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Token'ı header'dan al
        token = request.headers.get('Authorization').split(' ')[1]

        # SAP HANA veritabanından veri çek
        hana_data = fetch_hana_db_data(token)
        print("HANA Data:", hana_data)  # Bu satırı ekleyin

        if hana_data:
            saved_objects = []
            errors = []
            for data in hana_data:  # 'data' anahtarını kaldırdık
                # Veri setinden gelen alanları modeldeki alan adlarıyla eşleştir
                mapped_data = {
                'satici': data.get('Satici'),
                'belge_tur': data.get('BelgeTur'),
                'onay1_status': data.get('Onay1Status'),
                'onay2_status': data.get('Onay2Status'),
                'belge_tarihi': data.get('BelgeTarihi'),
                'teslim_tarihi': data.get('TeslimTarihi'),
                'belge_status': data.get('BelgeStatus'),
                'musteri_kod': data.get('MusteriKod'),
                'musteri_ad': data.get('MusteriAd'),
                'belge_giris_no': data.get('BelgeGirisNo'),
                'sip_no': data.get('SipNo'),
                'satis_tipi': data.get('SatisTipi'),
                'belge_aciklamasi': data.get('BelgeAciklamasi'),
                'sevk_adresi': data.get('SevkAdresi'),
                'unique_master_no': data.get('UniqueMasterNo'),
                'kalem_grup_kod': data.get('KalemGrupKod'),
                'kalem_grup': data.get('KalemGrup'),
                'eski_bilesen_kod': data.get('EskiBilesenKod'),
                'musteri_sip_no': data.get('MusteriSipNo'),
                'musteri_sip_tarih': data.get('MusteriSipTarih'),
                'assmann_comm_no': data.get('AssmannCommNo'),
                'assmann_pos_no': data.get('AssmannPosNo'),
                'assmann_item_no': data.get('AssmannItemNo'),
                'renk_kod': data.get('RenkKod'),
                'uretim_aciklamasi': data.get('UretimAciklamasi'),
                'satir_status': data.get('SatirStatus'),
                'satir_no': data.get('SatirNo'),
                'depo_kod': data.get('DepoKod'),
                'kalem_kod': data.get('KalemKod'),
                'kalem_tanimi': data.get('KalemTanimi'),
                'birim': data.get('Birim'),
                'sip_miktar': data.get('SipMiktar'),
                'sevk_miktar': data.get('SevkMiktar'),
                'kalan_miktar': data.get('KalanMiktar'),
                'liste_fiyat_dpb': data.get('ListeFiyatDPB'),
                'iskonto_oran': data.get('IskontoOran'),
                'net_fiyat_dpb': data.get('NetFiyatDPB'),
                'brut_tutar_dpb': data.get('BrutTutarDPB'),
                'net_tutar_dpb': data.get('NetTutarDPB'),
                'isk_tutar_dpb': data.get('IskTutarDPB'),
                'kdv_tutar_dpb': data.get('KdvTutarDPB'),
                'kdvli_net_tutar_dpb': data.get('KdvliNetTutarDPB'),
                'kur': data.get('Kur'),
                'doviz': data.get('Doviz'),
                'liste_fiyat_ypb': data.get('ListeFiyatYPB'),
                'brut_tutar_ypb': data.get('BrutTutarYPB'),
                'isk_tutar_ypb': data.get('IskTutarYPB'),
                'net_tutar_ypb': data.get('NetTutarYPB'),
                'kdv_oran': data.get('KdvOran'),
                'kdv_tutar_ypb': data.get('KdvTutarYPB'),
                'kdvli_net_tutar_ypb': data.get('KdvliNetTutarYPB'),
            }


                serializer = SalesOrderSerializer(data=mapped_data)
                if serializer.is_valid():
                    saved_obj = serializer.save()
                    saved_objects.append(saved_obj)
                else:
                    errors.append(serializer.errors)
            
            if saved_objects:
                return Response({'message': f'{len(saved_objects)} sales orders successfully fetched and saved.', 'errors': errors}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'No data saved', 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Failed to fetch data from HANA DB'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

 


def export_sales_orders_xlsx(request):
    # Tüm satış siparişlerini al
    queryset = SalesOrder.objects.all()
    # Verileri Dataset'e dönüştürün
    dataset = Dataset()
    dataset.load_data(queryset)

    # XLSX formatında çıktı alın
    response = HttpResponse(dataset.export(format=XLSX), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="sales_orders.xlsx"'

    return response
