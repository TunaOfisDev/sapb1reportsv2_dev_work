# backend/salesorderdetail/api/views.py
from django.core.cache import cache
from django.conf import settings
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models.models import SalesOrderDetail, SalesOrderMaster
from ..serializers import SalesOrderDetailSerializer, SalesOrderMasterSerializer
from ..utilities.data_fetcher import fetch_hana_db_data


class SalesOrderMasterView(generics.ListCreateAPIView):
    queryset = SalesOrderMaster.objects.all()
    serializer_class = SalesOrderMasterSerializer
    permission_classes = [IsAuthenticated]

class SalesOrderDetailView(generics.ListCreateAPIView):
    queryset = SalesOrderDetail.objects.all()
    serializer_class = SalesOrderDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        master_belge_giris_no = self.request.query_params.get('master_belge_giris_no')
        if master_belge_giris_no:
            queryset = queryset.filter(master__master_belge_giris_no=master_belge_giris_no)
        return queryset



class FetchHanaSalesOrderDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        token = request.headers.get('Authorization').split(' ')[1]
        sales_order_data = fetch_hana_db_data(token)

        if not sales_order_data:
            return Response({
                'error': 'Failed to fetch data from HANA DB or no new data found.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        saved_masters = []
        saved_details = []
        errors = []

        for data in sales_order_data:
            master_instance, created = SalesOrderMaster.objects.get_or_create(
                master_belge_giris_no=data.get('MasterBelgeGirisNo'),
                defaults={
                'master_unique_id': data.get('master_unique_id'),
                'master_belge_giris_no': data.get('MasterBelgeGirisNo'),
                'sip_no': data.get('SipNo'),
                'satis_tipi': data.get('SatisTipi'),
                'satici': data.get('Satici'),
                'belge_tur': data.get('BelgeTur'),
                'onay1_status': data.get('Onay1Status'),
                'onay2_status': data.get('Onay2Status'),
                'belge_tarihi': data.get('BelgeTarihi'),
                'teslim_tarihi': data.get('TeslimTarihi'),
                'belge_onay': data.get('BelgeOnay'),
                'belge_status': data.get('BelgeStatus'),
                'belge_kur': data.get('BelgeKur'),
                'belge_doviz': data.get('BelgeDoviz'),
                'musteri_kod': data.get('MusteriKod'),
                'musteri_ad': data.get('MusteriAd')

                }
            )
            if created:
                saved_masters.append(master_instance)

            detail_data = {
                    'master': master_instance.pk,
                    'detay_unique_id': data.get('detay_unique_id'),
                    'detay_belge_giris_no': data.get('DetayBelgeGirisNo'),
                    'kalem_grup': data.get('KalemGrup'),
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
                    'detay_kur': data.get('DetayKur'),
                    'detay_doviz': data.get('DetayDoviz'),
                    'iskonto_oran': data.get('IskontoOran'),
                    'net_fiyat_dpb': data.get('NetFiyatDPB'),
                    'brut_tutar_dpb': data.get('BrutTutarDPB'),
                    'net_tutar_dpb': data.get('NetTutarDPB'),
                    'isk_tutar_dpb': data.get('IskTutarDPB'),
                    'kdv_tutar_dpb': data.get('KdvTutarDPB'),
                    'kdvli_net_tutar_dpb': data.get('KdvliNetTutarDPB'),
                    'liste_fiyat_ypb': data.get('ListeFiyatYPB'),
                    'brut_tutar_ypb': data.get('BrutTutarYPB'),
                    'isk_tutar_ypb': data.get('IskTutarYPB'),
                    'net_tutar_ypb': data.get('NetTutarYPB'),
                    'kdv_oran': data.get('KdvOran'),
                    'kdv_tutar_ypb': data.get('KdvTutarYPB'),
                    'kdvli_net_tutar_ypb': data.get('KdvliNetTutarYPB'),

            }
            detail_serializer = SalesOrderDetailSerializer(data=detail_data)
            if detail_serializer.is_valid():
                detail_instance = detail_serializer.save()
                saved_details.append(detail_instance)
            else:
                errors.append(detail_serializer.errors)

        if saved_masters or saved_details:
            return Response({
                'message': f'{len(saved_masters)} master(s) and {len(saved_details)} detail(s) were successfully fetched and saved.',
                'masters_saved_count': len(saved_masters),
                'details_saved_count': len(saved_details),
                'errors': errors
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Data fetching was successful but no new data was saved.',
                'errors': errors
            }, status=status.HTTP_400_BAD_REQUEST)