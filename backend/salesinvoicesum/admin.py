# backend/salesinvoicesum/admin.py
from django.contrib import admin
from import_export.admin import ExportMixin
from .models.sales_invoice_sum_model import SalesInvoiceSum

class SalesInvoiceSumAdmin(ExportMixin, admin.ModelAdmin):
    list_display = [
        'representative', 'customer_group', 'customer_code', 'customer_name',
        'debt_balance', 'advance_balance', 'today_total', 'yesterday_total',
        'two_days_ago_total', 'three_days_ago_total', 'four_days_ago_total',
        'weekly_total', 'monthly_total', 'last_month_total', 'yearly_total',
        'open_orders_total', 'open_shipments_total', 'invoice_count', 'created_at', 'updated_at'
    ]
    search_fields = ['customer_code', 'customer_name', 'representative']
    list_filter = ['representative', 'customer_group']
    ordering = ['-created_at']

admin.site.register(SalesInvoiceSum, SalesInvoiceSumAdmin)
