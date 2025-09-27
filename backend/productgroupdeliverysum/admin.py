# backend/productgroupdeliverysum/admin.py
from django.contrib import admin
from .models.delivery_summary import DeliverySummary

@admin.register(DeliverySummary)
class DeliverySummaryAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'yil', 'yil_ay', 'teslimat_tutar', 'teslimat_girsberger', 
        'teslimat_mamul', 'teslimat_ticari', 'teslimat_nakliye', 'teslimat_montaj',
        'created_at', 'updated_at'
    )
    list_filter = ('yil', 'yil_ay')  # Yıl ve ay bazında filtreleme
    search_fields = ('yil_ay', 'teslimat_tutar')  # Yıl-Ay ve teslimat tutarına göre arama

    ordering = ('-yil', '-yil_ay')  # Yıl ve Ay'a göre sıralama
