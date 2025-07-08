# backend/shipweekplanner/admin.py
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models.models import ShipmentOrder
from .resources import ShipmentOrderResource
from django.utils.html import format_html
from django.urls import reverse

class ShipmentOrderAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = ShipmentOrderResource  # Import-export kaynağı

    list_display = (
        'order_number', 
        'customer_name', 
        'order_date', 
        'planned_date_mirror', 
        'get_latest_planned_date',  
        'planned_date_real',  
        'planned_date_week',  
        'shipment_date', 
        'sales_person', 
        'order_status',  
        'shipment_details_summary',  # Kısa sevk detayları
        'view_notes_link',  # Notları görüntüle linki
        'selected_color'
    )
    list_filter = ('order_date', 'shipment_date', 'sales_person', 'order_status')
    search_fields = ('order_number', 'customer_name', 'sales_person')
    date_hierarchy = 'order_date'
    ordering = ['-order_date']

    def shipment_details_summary(self, obj):
        """
        Sevk detaylarını kısaltılmış bir özet olarak gösterir.
        """
        if obj.shipment_details:
            return (obj.shipment_details[:50] + '...') if len(obj.shipment_details) > 50 else obj.shipment_details
        return 'No details'
    shipment_details_summary.short_description = 'Shipment Details'

    def view_notes_link(self, obj):
        """
        Notlar için admin panelinde bir bağlantı oluşturur.
        """
        if obj.shipment_notes:
            url = reverse('admin:shipweekplanner_shipmentorder_change', args=[obj.id])
            return format_html('<a href="{}">View Notes</a>', url)
        return 'No notes'
    view_notes_link.short_description = 'Notes'

    def get_latest_planned_date(self, obj):
        if obj.planned_dates:
            return obj.planned_dates[-1]
        return "No planned date"
    get_latest_planned_date.short_description = 'Latest Planned Date'

    fields = (
        'order_number', 
        'customer_name', 
        'order_date', 
        'sales_person', 
        'order_status',  
        'planned_date_mirror',     
        'planned_dates',  
        'planned_date_real',  
        'planned_date_week',  
        'shipment_date', 
        'shipment_details', 
        'shipment_notes',
        'selected_color'
    )

admin.site.register(ShipmentOrder, ShipmentOrderAdmin)
