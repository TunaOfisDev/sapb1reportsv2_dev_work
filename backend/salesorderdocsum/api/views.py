# backend/salesorderdocsum/api/views.py

from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from ..serializers import SalesOrderDetailSerializer
from ..models.salesorderdetail import SalesOrderDetail
from ..models.docsum import DocumentSummary
from ..utilities.data_fetcher import fetch_hana_db_data
from django.core.cache import cache
from loguru import logger

API_NAME = 'salesorderdocsum'


class SalesOrderDetailListView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get(self, request, *args, **kwargs):
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        belge_no = request.query_params.get('belge_no')
        musteri_kod = request.query_params.get('musteri_kod')
        
        # Recent verileri de serialize edilmeli
        recent_details = SalesOrderDetail.objects.filter(belge_tarih__gte=thirty_days_ago)
        if belge_no:
            recent_details = recent_details.filter(belge_no__icontains=belge_no)
        if musteri_kod:
            recent_details = recent_details.filter(musteri_kod__icontains=musteri_kod)
        
        # Recent verileri serialize ediyoruz
        recent_serializer = SalesOrderDetailSerializer(recent_details, many=True)
        recent_data = recent_serializer.data
        
        cache_key = f'{API_NAME}_old_sales_order_details'
        cached_old_data = cache.get(cache_key)
        if not cached_old_data:
            old_details = SalesOrderDetail.objects.filter(belge_tarih__lt=thirty_days_ago)
            serializer = SalesOrderDetailSerializer(old_details, many=True)
            cached_old_data = serializer.data
            cache.set(cache_key, cached_old_data, timeout=None)
        
        if belge_no or musteri_kod:
            cached_old_data = [
                item for item in cached_old_data
                if (not belge_no or belge_no in item['belge_no']) and
                (not musteri_kod or musteri_kod in item['musteri_kod'])
            ]
        
        # Artık tüm veriler aynı formatta (serialize edilmiş dict'ler)
        all_details = recent_data + cached_old_data
        all_details.sort(key=lambda x: x['belge_tarih'], reverse=True)
        
        paginator = self.pagination_class()
        paginated_details = paginator.paginate_queryset(all_details, request)
        
        return paginator.get_paginated_response(paginated_details)

class FetchHanaDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        token = request.headers.get('Authorization', '').split(' ')[-1]
        if not token:
            return Response({"error": "Token sağlanmadı."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            with transaction.atomic():
                
                
                # HANA DB'den tüm verileri çek
                data = fetch_hana_db_data(token)
                if not data:
                    logger.error("HANA DB'den veri alınamadı")
                    return Response({"error": "Veri alınamadı veya boş."}, status=status.HTTP_204_NO_CONTENT)
                
                
                
                # Mevcut tüm verileri sil
               
                SalesOrderDetail.objects.all().delete()
                DocumentSummary.objects.all().delete()
                
                
                # Yeni kayıtları toplu ekle
                new_records = []
                belge_nos = set()
                
               
                for item in data:
                    new_record = SalesOrderDetail(
                        uniq_detail_no=item['UniqDetailNo'],
                        belge_no=item['BelgeNo'],
                        satici=item['Satici'],
                        belge_tarih=item['BelgeTarih'],
                        teslim_tarih=item['TeslimTarih'],
                        belge_onay=item['BelgeOnay'],
                        belge_durum=item['BelgeStatus'],
                        belge_aciklamasi=item['BelgeAciklamasi'],
                        sevk_adres=item['SevkAdres'],
                        musteri_kod=item['MusteriKod'],
                        musteri_ad=item['MusteriAd'],
                        satis_tipi=item['SatisTipi'],
                        kalem_grup=item['KalemGrup'],
                        satir_durum=item['SatirStatus'],
                        satir_no=item['SatirNo'],
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
                        net_tutar_spb=item.get('NetTutarSPB', 0),
                        acik_net_tutar_ypb=item.get('AcikNetTutarYPB', 0),
                        acik_net_tutar_spb=item.get('AcikNetTutarSPB', 0),
                        brut_tutar_spb=item.get('BrutTutarSPB', 0),
                    )
                    new_records.append(new_record)
                    belge_nos.add(item['BelgeNo'])
                    
                    # Her 1000 kayıtta bir toplu ekleme yap (bellek optimizasyonu için)
                    if len(new_records) >= 1000:
                        
                        SalesOrderDetail.objects.bulk_create(new_records)
                        new_records = []
                
                # Kalan kayıtları ekle
                if new_records:
                    
                    SalesOrderDetail.objects.bulk_create(new_records)
                
                
                
                # Özet bilgileri hesapla ve oluştur
                
                self._create_document_summaries(belge_nos)
                
                # Önbelleği temizle
              
                cache.clear()
                
                
                
                return Response({
                    "message": "Tüm veriler sıfırlandı ve yeniden yüklendi.",
                    "records_count": len(data),
                    "unique_documents": len(belge_nos)
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            logger.error(f"Veri sıfırlama ve yükleme işlemi sırasında hata: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _create_document_summaries(self, belge_nos):
        """Belge numaralarına göre özetleri hesaplar ve kaydeder"""
        # Belge numaralarına göre gruplandırılmış özet veriler
        summaries = SalesOrderDetail.objects.filter(belge_no__in=belge_nos).values(
            'belge_no', 'satici', 'belge_tarih', 'teslim_tarih', 'belge_onay', 
            'belge_durum', 'belge_aciklamasi', 'musteri_kod', 'musteri_ad', 
            'sevk_adres', 'satis_tipi'
        ).annotate(
            net_tutar_ypb=Sum('net_tutar_ypb'),
            net_tutar_spb=Sum('net_tutar_spb'),
            acik_net_tutar_ypb=Sum('acik_net_tutar_ypb'),
            acik_net_tutar_spb=Sum('acik_net_tutar_spb'),
            brut_tutar_spb=Sum('brut_tutar_spb'),
        )
        
        # Belgeleri toplu olarak oluştur
        summary_objects = []
        for summary in summaries:
            summary_obj = DocumentSummary(
                belge_no=summary['belge_no'],
                satici=summary['satici'],
                belge_tarih=summary['belge_tarih'],
                teslim_tarih=summary['teslim_tarih'],
                belge_onay=summary['belge_onay'],
                belge_durum=summary['belge_durum'],
                belge_aciklamasi=summary['belge_aciklamasi'],
                musteri_kod=summary['musteri_kod'],
                musteri_ad=summary['musteri_ad'],
                sevk_adres=summary['sevk_adres'],
                satis_tipi=summary['satis_tipi'],
                net_tutar_ypb=summary['net_tutar_ypb'],
                net_tutar_spb=summary['net_tutar_spb'],
                acik_net_tutar_ypb=summary['acik_net_tutar_ypb'],
                acik_net_tutar_spb=summary['acik_net_tutar_spb'],
                brut_tutar_spb=summary['brut_tutar_spb'],
            )
            summary_objects.append(summary_obj)
            
            # Her 1000 özet için toplu ekleme yap
            if len(summary_objects) >= 1000:
                DocumentSummary.objects.bulk_create(summary_objects)
                summary_objects = []
        
        # Kalan özetleri ekle
        if summary_objects:
            DocumentSummary.objects.bulk_create(summary_objects)
        
        