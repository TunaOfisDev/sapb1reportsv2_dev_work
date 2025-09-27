# backend/salesorder/api/filter_views.py
from django.db.models import Q, Sum, F, ExpressionWrapper, FloatField
from django.db.models.functions import Coalesce
from rest_framework.views import APIView
from rest_framework.response import Response
from ..models.models import SalesOrder
from django.utils.dateparse import parse_date
from datetime import datetime, timedelta
from django.db.models.functions import Coalesce
from django.db.models.functions import ExtractYear, ExtractMonth


class DynamicFilterView(APIView):
    def get(self, request, *args, **kwargs):
        queryset = SalesOrder.objects.all()
        current_time = datetime.now()

        # Diğer filtreler için Q nesnelerini kullanarak sorgu oluştur
        q_objects = Q()

        # Zaman filtresi
        time_filter = request.query_params.get('time_filter', None)
        if time_filter:
            if time_filter == 'daily':
                start_time = current_time - timedelta(days=1)
            elif time_filter == 'weekly':
                start_time = current_time - timedelta(weeks=1)
            elif time_filter == 'monthly':
                start_time = current_time - timedelta(days=30)
            elif time_filter == 'quarterly':
                start_time = current_time - timedelta(days=90)
            elif time_filter == 'yearly':
                start_time = current_time - timedelta(days=365)
            queryset = queryset.filter(belge_tarihi__gte=start_time)

        # Manuel tarih aralığı filtresi
        start_date = request.query_params.get('startdate')
        end_date = request.query_params.get('enddate')
        if start_date and end_date:
            start_date_parsed = parse_date(start_date)
            end_date_parsed = parse_date(end_date)
            q_objects &= Q(belge_tarihi__range=[start_date_parsed, end_date_parsed])

        # Diğer filtreler
        for filter_key in ['satici', 'doviz', 'satis_tipi', 'belge_tur', 'musteri_kod', 'musteri_ad']:
            filter_value = request.query_params.get(filter_key)
            if filter_value:
                q_objects &= Q(**{filter_key: filter_value})

        filtered_queryset = queryset.filter(q_objects)

        kur_with_default = ExpressionWrapper(Coalesce(F('kur'), 1), output_field=FloatField())
        aggregates = filtered_queryset.values('musteri_kod', 'musteri_ad').annotate(
            BrutTutarDPB=Sum(F('brut_tutar_dpb'), output_field=FloatField()),
            IskTutarDPB=Sum(F('isk_tutar_dpb'), output_field=FloatField()),
            NetTutarDPB=Sum(F('net_tutar_dpb'), output_field=FloatField()),
            KdvTutarDPB=Sum(F('kdv_tutar_dpb'), output_field=FloatField()),
            KdvliNetTutarDPB=Sum(F('kdvli_net_tutar_dpb'), output_field=FloatField()),
            BrutTutarYPB=Sum(F('brut_tutar_ypb') * kur_with_default, output_field=FloatField()),
            IskTutarYPB=Sum(F('isk_tutar_ypb') * kur_with_default, output_field=FloatField()),
            NetTutarYPB=Sum(F('net_tutar_ypb') * kur_with_default, output_field=FloatField()),
            KdvTutarYPB=Sum(F('kdv_tutar_ypb') * kur_with_default, output_field=FloatField()),
            KdvliNetTutarYPB=Sum(F('kdvli_net_tutar_ypb') * kur_with_default, output_field=FloatField()),
        ).order_by('-NetTutarYPB')

        return Response(list(aggregates))


class SalesReportView(APIView):
    def get(self, request, *args, **kwargs):
        # Filtreleme parametrelerini al
        year_filter = request.query_params.get('year')
        month_filter = request.query_params.get('month')
        satici_filter = request.query_params.get('satici')
        musteri_filter = request.query_params.get('musteri')
        belge_tur_filter = request.query_params.get('belge_tur')

        # Sorgu nesnesini oluştur
        q_objects = Q()
        if year_filter:
            q_objects &= Q(belge_tarihi__year=year_filter)
        if month_filter:
            q_objects &= Q(belge_tarihi__month=month_filter)
        if satici_filter:
            q_objects &= Q(satici=satici_filter)
        if musteri_filter:
            q_objects &= Q(musteri_kod=musteri_filter)
        if belge_tur_filter:
            q_objects &= Q(belge_tur=belge_tur_filter)

        # QuerySet'i filtrele
        queryset = SalesOrder.objects.filter(q_objects)

        # Yıl ve aya göre gruplandırma yaparak özet bilgileri hesapla
        aggregates = queryset.annotate(
            year=ExtractYear('belge_tarihi'),
            month=ExtractMonth('belge_tarihi')
        ).values('year', 'month', 'satici', 'musteri_kod', 'musteri_ad').annotate(
            TotalNetTutarYPB=Sum(F('net_tutar_ypb'), output_field=FloatField())
        ).order_by('-TotalNetTutarYPB')

        return Response(list(aggregates))

