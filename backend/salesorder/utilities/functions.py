# backend/salesorder/utilities/functions.py
from django.db.models import Sum, F, ExpressionWrapper, FloatField
from django.db.models.functions import Coalesce
from ..models.models import SalesOrder

def get_aggregated_values():
    """
    Belirli bir filtre/gruplama için SalesOrder kayıtlarının özet hesaplamalarını gerçekleştirir.
    Özet hesaplamalar şunları içerir: BrutTutarDPB, IskTutarDPB, NetTutarDPB, KdvTutarDPB, KdvliNetTutarDPB,
    BrutTutarYPB, IskTutarYPB, NetTutarYPB, KdvTutarYPB, KdvliNetTutarYPB.
    """
    # Kur değeri None veya 0 ise 1 kullan
    kur_with_default = ExpressionWrapper(Coalesce(F('kur'), 1), output_field=FloatField())
    
    # Satır bazında DPB ve YPB hesaplamaları
    aggregates = SalesOrder.objects.aggregate(
        BrutTutarDPB=Sum(F('brut_tutar_dpb'), output_field=FloatField()),
        IskTutarDPB=Sum(F('isk_tutar_dpb'), output_field=FloatField()),
        NetTutarDPB=Sum(F('net_tutar_dpb'), output_field=FloatField()),
        KdvTutarDPB=Sum(F('kdv_tutar_dpb'), output_field=FloatField()),
        KdvliNetTutarDPB=Sum(F('kdvli_net_tutar_dpb'), output_field=FloatField()),
        BrutTutarYPB=Sum(F('brut_tutar_ypb'), output_field=FloatField()),
        IskTutarYPB=Sum(F('isk_tutar_ypb'), output_field=FloatField()),
        NetTutarYPB=Sum(F('net_tutar_ypb'), output_field=FloatField()),
        KdvTutarYPB=Sum(F('kdv_tutar_ypb'), output_field=FloatField()),
        KdvliNetTutarYPB=Sum(F('kdvli_net_tutar_ypb'), output_field=FloatField()),
    )

    return aggregates



