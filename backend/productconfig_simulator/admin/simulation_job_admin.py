# backend/productconfig_simulator/admin/simulation_job_admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.db.models import Count, Sum, Avg, Min, Max

from ..models.simulation_job import SimulationJob
from ..models.simulated_variant import SimulatedVariant
from ..models.simulation_error import SimulationError
from .filters import (
    SimulationLevelFilter,
    SimulationStatusFilter,
    HasErrorsFilter,
    DateRangeFilter
)

class SimulationJobAdmin(admin.ModelAdmin):
    """
    Simülasyon işlerini yönetmek için admin arayüzü
    """
    list_display = (
        'id', 'name', 'level_display', 'status_display', 'progress_bar',
        'total_variants', 'total_errors', 'start_time', 'end_time', 'duration_display'
    )
    list_filter = (
        SimulationLevelFilter,
        SimulationStatusFilter,
        HasErrorsFilter,
        DateRangeFilter,
        'is_active',
    )
    search_fields = ('name', 'description')
    
    # progress alanı SimulationJob modelinde var olduğundan emin ol
    readonly_fields = (
        'status', 'start_time', 'end_time', 'celery_task_id',
        'total_models', 'processed_models', 'total_variants', 'total_errors',
        'created_at', 'updated_at', 'stats_summary'
    )
    # 'progress' alanını kaldırdım çünkü modelde bulunamıyor
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('name', 'description', 'level', 'is_active')
        }),
        ('Hedef Seçimi', {
            'fields': ('brand', 'product_group', 'category', 'product_model'),
            'description': 'Simülasyon yapılacak hedef seçimi.'
        }),
        ('Yapılandırma', {
    'fields': ('max_variants_per_model',),
    'description': 'Simülasyon ayarları.'
}),

        ('Durum', {
            'fields': ('status', 'start_time', 'end_time', 'celery_task_id'),
            'description': 'Simülasyon durumu ve ilerleme bilgileri.'
        }),
        ('İstatistikler', {
            'fields': ('total_models', 'processed_models', 'total_variants', 'total_errors', 'stats_summary'),
            'description': 'Simülasyon sonuç istatistikleri.'
        }),
    )
    
    # kalan kodlar...
    actions = ['start_simulation', 'cancel_simulation', 'export_results']

    def level_display(self, obj):
        """Simülasyon seviyesini renkli göster"""
        level_colors = {
            SimulationJob.SimulationLevel.BRAND: 'purple',
            SimulationJob.SimulationLevel.PRODUCT_GROUP: 'blue',   # GROUP yerine PRODUCT_GROUP
            SimulationJob.SimulationLevel.CATEGORY: 'green',
            SimulationJob.SimulationLevel.PRODUCT_MODEL: 'orange',   # MODEL yerine PRODUCT_MODEL
        }
        color = level_colors.get(obj.level, 'gray')
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_level_display()
        )

    level_display.short_description = 'Seviye'

    def status_display(self, obj):
        """Simülasyon durumunu renkli göster"""
        status_colors = {
            SimulationJob.SimulationStatus.PENDING: 'gray',
            SimulationJob.SimulationStatus.RUNNING: 'blue',
            SimulationJob.SimulationStatus.COMPLETED: 'green',
            SimulationJob.SimulationStatus.FAILED: 'red',
            SimulationJob.SimulationStatus.CANCELLED: 'orange',
        }
        color = status_colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Durum'

    def progress_bar(self, obj):
        """İlerleme çubuğu göster"""
        progress = obj.progress_percentage  # integer değer
        if obj.status == SimulationJob.SimulationStatus.RUNNING:
            bar_color = "#007bff"  # mavi
        elif obj.status == SimulationJob.SimulationStatus.COMPLETED:
            bar_color = "#28a745"  # yeşil
            progress = 100
        else:
            bar_color = "#6c757d"  # gri

        # Üç placeholder ({}, {}, {}) için üç argüman veriyoruz: progress, bar_color, progress
        return format_html(
            '''
            <div style="width: 100px; background-color: #f8f9fa; border-radius: 5px;">
                <div style="width: {}%; background-color: {}; color: white; text-align: center; padding: 2px 0; border-radius: 5px;">
                    {}%
                </div>
            </div>
            ''',
            progress,     # <-- 1. placeholder (yüzde genişliği)
            bar_color,    # <-- 2. placeholder (rengi)
            progress      # <-- 3. placeholder (içerideki yüzde yazısı)
        )

    progress_bar.short_description = 'İlerleme'


    def duration_display(self, obj):
        """Simülasyon süresini göster"""
        if obj.start_time and obj.end_time:
            duration = obj.end_time - obj.start_time
            hours, remainder = divmod(duration.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            # Burada formatı düzeltiyoruz: (saat, dakika, saniye)
            return format_html('{}h {}m {}s', int(hours), int(minutes), int(seconds))
        return '-'

    duration_display.short_description = 'Süre'

    def stats_summary(self, obj):
        """İstatistik özeti göster"""
        if obj.status != SimulationJob.SimulationStatus.COMPLETED:
            return "Simülasyon tamamlanmadığı için istatistikler henüz mevcut değil."

        # Varyant istatistikleri
        variants = SimulatedVariant.objects.filter(simulation=obj)
        variant_count = variants.count()
        
        if variant_count == 0:
            return "Simülasyon tamamlandı, ancak hiç varyant oluşturulmadı."

        # Fiyat istatistikleri
        price_stats = variants.aggregate(
            avg_price=Avg('total_price'),
            min_price=Min('total_price'),
            max_price=Max('total_price')
        )

        # Hata istatistikleri
        errors = SimulationError.objects.filter(simulation=obj)
        error_count = errors.count()
        error_by_type = dict(errors.values_list('error_type').annotate(count=Count('id')))
        error_by_severity = dict(errors.values_list('severity').annotate(count=Count('id')))
        resolved_count = errors.filter(resolution_status=True).count()
        
        # İstatistik HTML'i oluştur
        html = """
        <style>
            .stats-card {
                background-color: #f8f9fa;
                border-radius: 5px;
                padding: 10px;
                margin-bottom: 10px;
            }
            .stats-header {
                font-weight: bold;
                border-bottom: 1px solid #dee2e6;
                padding-bottom: 5px;
                margin-bottom: 8px;
            }
            .stats-row {
                display: flex;
                justify-content: space-between;
                margin-bottom: 5px;
            }
            .stats-label {
                font-weight: bold;
                color: #495057;
            }
            .stats-value {
                color: #212529;
            }
        </style>
        
        <div class="stats-card">
            <div class="stats-header">Varyant İstatistikleri</div>
            <div class="stats-row">
                <span class="stats-label">Toplam Varyant:</span>
                <span class="stats-value">{}</span>
            </div>
            <div class="stats-row">
                <span class="stats-label">Ortalama Fiyat:</span>
                <span class="stats-value">{:.2f} TL</span>
            </div>
            <div class="stats-row">
                <span class="stats-label">Minimum Fiyat:</span>
                <span class="stats-value">{:.2f} TL</span>
            </div>
            <div class="stats-row">
                <span class="stats-label">Maksimum Fiyat:</span>
                <span class="stats-value">{:.2f} TL</span>
            </div>
        </div>
        
        <div class="stats-card">
            <div class="stats-header">Hata İstatistikleri</div>
            <div class="stats-row">
                <span class="stats-label">Toplam Hata:</span>
                <span class="stats-value">{}</span>
            </div>
            <div class="stats-row">
                <span class="stats-label">Çözülen Hatalar:</span>
                <span class="stats-value">{} ({}%)</span>
            </div>
        </div>
        """.format(
            variant_count,
            price_stats['avg_price'] or 0,
            price_stats['min_price'] or 0,
            price_stats['max_price'] or 0,
            error_count,
            resolved_count,
            int(resolved_count / error_count * 100) if error_count > 0 else 0
        )
        
        return format_html(html)
    stats_summary.short_description = 'İstatistik Özeti'
    
    def start_simulation(self, request, queryset):
        """Seçili simülasyonları başlat"""
        from ..tasks import run_simulation_task
        count = 0
        for sim in queryset:
            if sim.status in [SimulationJob.SimulationStatus.PENDING, SimulationJob.SimulationStatus.FAILED, SimulationJob.SimulationStatus.CANCELLED]:
                task = run_simulation_task.delay(simulation_id=sim.id)
                sim.celery_task_id = task.id
                sim.status = SimulationJob.SimulationStatus.RUNNING
                sim.save()
                count += 1
        self.message_user(request, f"{count} simülasyon başlatıldı.", messages.SUCCESS)
    start_simulation.short_description = "Seçili simülasyonları başlat"

    def cancel_simulation(self, request, queryset):
        """Seçili simülasyonları iptal et"""
        from celery.result import AsyncResult
        count = 0
        for sim in queryset:
            if sim.status == SimulationJob.SimulationStatus.RUNNING and sim.celery_task_id:
                task_result = AsyncResult(sim.celery_task_id)
                task_result.revoke(terminate=True)
                sim.status = SimulationJob.SimulationStatus.CANCELLED
                sim.save()
                count += 1
        self.message_user(request, f"{count} simülasyon iptal edildi.", messages.SUCCESS)
    cancel_simulation.short_description = "Seçili simülasyonları iptal et"

    def export_results(self, request, queryset):
        """Seçili simülasyon sonuçlarını dışa aktar"""
        if len(queryset) != 1:
            self.message_user(request, "Lütfen dışa aktarmak için sadece bir simülasyon seçin.", messages.ERROR)
            return
        
        sim = queryset.first()
        export_url = reverse('admin:export-simulation-results', args=[sim.id])
        return HttpResponseRedirect(export_url)
    export_results.short_description = "Sonuçları dışa aktar"