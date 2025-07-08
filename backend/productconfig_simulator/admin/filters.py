# backend/productconfig_simulator/admin/filters.py
from django.contrib.admin import SimpleListFilter
from django.db.models import Q, Count
from ..models.simulation_job import SimulationJob
from ..models.simulation_error import SimulationError


class SimulationLevelFilter(SimpleListFilter):
    """
    Simülasyon seviyesine göre filtreleme yapan admin filtresi.
    """
    title = 'Simülasyon Seviyesi'
    parameter_name = 'level'

    def lookups(self, request, model_admin):
        return SimulationJob.SimulationLevel.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(level=self.value())
        return queryset


class SimulationStatusFilter(SimpleListFilter):
    """
    Simülasyon durumuna göre filtreleme yapan admin filtresi.
    """
    title = 'Durum'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return SimulationJob.SimulationStatus.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


class HasErrorsFilter(SimpleListFilter):
    """
    Hata içeren simülasyonları filtreleme yapan admin filtresi.
    """
    title = 'Hata Durumu'
    parameter_name = 'has_errors'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Hata İçeren'),
            ('no', 'Hatasız'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            # Hata içeren simülasyonları getir
            return queryset.annotate(error_count=Count('simulation_errors')).filter(error_count__gt=0)
        if self.value() == 'no':
            # Hata içermeyen simülasyonları getir
            return queryset.annotate(error_count=Count('simulation_errors')).filter(error_count=0)
        return queryset


class ErrorTypeFilter(SimpleListFilter):
    """
    Hata türüne göre filtreleme yapan admin filtresi.
    """
    title = 'Hata Türü'
    parameter_name = 'error_type'

    def lookups(self, request, model_admin):
        return SimulationError.ErrorType.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(error_type=self.value())
        return queryset


class ErrorSeverityFilter(SimpleListFilter):
    """
    Hata önem derecesine göre filtreleme yapan admin filtresi.
    """
    title = 'Önem Derecesi'
    parameter_name = 'severity'

    def lookups(self, request, model_admin):
        return SimulationError.ErrorSeverity.choices


    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(severity=self.value())
        return queryset


class ResolutionStatusFilter(SimpleListFilter):
    """
    Çözüm durumuna göre filtreleme yapan admin filtresi.
    """
    title = 'Çözüm Durumu'
    parameter_name = 'resolution_status'

    def lookups(self, request, model_admin):
        return (
            ('resolved', 'Çözülmüş'),
            ('unresolved', 'Çözülmemiş'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'resolved':
            return queryset.filter(resolution_status=True)
        if self.value() == 'unresolved':
            return queryset.filter(resolution_status=False)
        return queryset


class ModelRelatedFilter(SimpleListFilter):
    """
    Ürün modeli ilişkisine göre filtreleme yapan admin filtresi.
    """
    title = 'Ürün Modeli Durumu'
    parameter_name = 'has_product_model'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Ürün Modeli Mevcut'),
            ('no', 'Ürün Modeli Yok'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(product_model__isnull=False)
        if self.value() == 'no':
            return queryset.filter(product_model__isnull=True)
        return queryset


class QuestionRelatedFilter(SimpleListFilter):
    """
    Soru ilişkisine göre filtreleme yapan admin filtresi.
    """
    title = 'Soru Durumu'
    parameter_name = 'has_question'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Soru Mevcut'),
            ('no', 'Soru Yok'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(question__isnull=False)
        if self.value() == 'no':
            return queryset.filter(question__isnull=True)
        return queryset


class DateRangeFilter(SimpleListFilter):
    """
    Tarih aralığına göre filtreleme yapan admin filtresi.
    """
    title = 'Tarih Aralığı'
    parameter_name = 'date_range'

    def lookups(self, request, model_admin):
        return (
            ('today', 'Bugün'),
            ('yesterday', 'Dün'),
            ('this_week', 'Bu Hafta'),
            ('last_week', 'Geçen Hafta'),
            ('this_month', 'Bu Ay'),
            ('last_month', 'Geçen Ay'),
        )

    def queryset(self, request, queryset):
        from datetime import datetime, timedelta
        from django.utils import timezone

        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

        if self.value() == 'today':
            return queryset.filter(created_at__gte=today)
        if self.value() == 'yesterday':
            yesterday = today - timedelta(days=1)
            return queryset.filter(created_at__gte=yesterday, created_at__lt=today)
        if self.value() == 'this_week':
            start_of_week = today - timedelta(days=today.weekday())
            return queryset.filter(created_at__gte=start_of_week)
        if self.value() == 'last_week':
            start_of_this_week = today - timedelta(days=today.weekday())
            start_of_last_week = start_of_this_week - timedelta(days=7)
            return queryset.filter(created_at__gte=start_of_last_week, created_at__lt=start_of_this_week)
        if self.value() == 'this_month':
            start_of_month = today.replace(day=1)
            return queryset.filter(created_at__gte=start_of_month)
        if self.value() == 'last_month':
            start_of_this_month = today.replace(day=1)
            last_day_of_prev_month = start_of_this_month - timedelta(days=1)
            start_of_last_month = last_day_of_prev_month.replace(day=1)
            return queryset.filter(created_at__gte=start_of_last_month, created_at__lt=start_of_this_month)
        return queryset