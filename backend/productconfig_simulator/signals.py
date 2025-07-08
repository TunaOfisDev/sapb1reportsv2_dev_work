# backend/productconfig_simulator/signals.py
import logging
from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from django.utils import timezone

from .models.simulation_job import SimulationJob
from .models.simulated_variant import SimulatedVariant
from .models.simulation_error import SimulationError
from .tasks import run_simulation_task

logger = logging.getLogger(__name__)

@receiver(post_save, sender=SimulationJob)
def handle_simulation_job_save(sender, instance, created, **kwargs):
    """
    SimulationJob nesnesinin kaydedilmesi sonrası yapılacak işlemler.
    
    - Yeni oluşturulan işler için otomatik olarak Celery görevi başlatılır.
    - Tamamlanan işler için özet bilgiler güncellenir.
    """
    # Yeni oluşturulan bir simülasyon için Celery görevi başlat
    if created and instance.status == SimulationJob.SimulationStatus.PENDING:
        logger.info(f"Yeni simülasyon oluşturuldu, otomatik başlatılıyor - ID: {instance.id}")
        
        # Celery görevi başlat
        task = run_simulation_task.delay(
            simulation_id=instance.id,
            parallel=True,  # Varsayılan olarak paralel işleme kullan
            max_workers=4   # Varsayılan işlemci sayısı
        )
        
        # Celery task id'sini kaydet
        instance.celery_task_id = task.id
        instance.save(update_fields=['celery_task_id'])
    
    # Simülasyon tamamlandığında özet bilgileri güncelle
    elif instance.status == SimulationJob.SimulationStatus.COMPLETED:
        # Simülasyon sonuç özetini oluştur
        if not instance.result_summary or isinstance(instance.result_summary, dict) and not instance.result_summary:
            logger.info(f"Tamamlanan simülasyon için sonuç özeti oluşturuluyor - ID: {instance.id}")
            
            # Variant ve error sayılarını güncelle
            variant_count = SimulatedVariant.objects.filter(simulation=instance).count()
            error_count = SimulationError.objects.filter(simulation=instance).count()
            
            # Bitiş zamanını güncelle
            instance.end_time = timezone.now()
            
            # Özet bilgiyi hazırla
            result_summary = {
                'total_variants': variant_count,
                'total_errors': error_count,
                'duration_seconds': (instance.end_time - instance.start_time).total_seconds() if instance.start_time else 0,
                'completion_time': instance.end_time.isoformat() if instance.end_time else None,
                'errors_by_type': {}
            }
            
            # Hata tipine göre istatistikler
            error_types = SimulationError.objects.filter(
                simulation=instance
            ).values_list('error_type').distinct()
            
            for error_type in error_types:
                error_type_name = error_type[0]
                count = SimulationError.objects.filter(
                    simulation=instance, 
                    error_type=error_type_name
                ).count()
                result_summary['errors_by_type'][error_type_name] = count
            
            # Özeti kaydet
            instance.result_summary = result_summary
            instance.save(update_fields=['result_summary', 'end_time'])


@receiver(post_save, sender=SimulatedVariant)
def handle_simulated_variant_save(sender, instance, created, **kwargs):
    """
    SimulatedVariant oluşturulduğunda simülasyon istatistiklerini günceller.
    """
    if created:
        # İstatistikleri güncelle (bulk işlemlerde performans için kısıtlanabilir)
        simulation = instance.simulation
        
        # Toplam varyant sayısını güncelle
        current_count = SimulatedVariant.objects.filter(simulation=simulation).count()
        
        # Her varyant eklendiğinde güncelleme yapmak performansı etkileyebilir
        # Bu nedenle daha az sıklıkta güncelleme yapmak için mod kullanabiliriz
        if current_count % 100 == 0:  # Her 100 varyanttan birinde güncelle
            simulation.total_variants = current_count
            simulation.save(update_fields=['total_variants'])


@receiver(post_save, sender=SimulationError)
def handle_simulation_error_save(sender, instance, created, **kwargs):
    """
    SimulationError oluşturulduğunda simülasyon istatistiklerini günceller.
    """
    if created:
        # Simülasyon hata sayısını güncelle
        simulation = instance.simulation
        
        # Toplam hata sayısını güncelle
        current_error_count = SimulationError.objects.filter(simulation=simulation).count()
        
        # Daha az sıklıkta güncelleme için
        if current_error_count % 10 == 0:  # Her 10 hatadan birinde güncelle
            simulation.total_errors = current_error_count
            simulation.save(update_fields=['total_errors'])


@receiver(pre_delete, sender=SimulationJob)
def handle_simulation_job_delete(sender, instance, **kwargs):
    """
    SimulationJob silinmeden önce yapılacak işlemler.
    
    - İlişkili varyantları ve hataları temizleme
    - Devam eden Celery görevlerini iptal etme
    """
    logger.info(f"Simülasyon siliniyor - ID: {instance.id}")
    
    # Devam eden görev varsa iptal et
    if instance.celery_task_id and instance.status == SimulationJob.SimulationStatus.RUNNING:
        try:
            # Güncel Celery sürümleri için doğru import
            from celery.result import AsyncResult
            
            # Görevi iptal et
            task_result = AsyncResult(instance.celery_task_id)
            task_result.revoke(terminate=True)
            
            logger.info(f"Devam eden simülasyon görevi iptal edildi - Task ID: {instance.celery_task_id}")
        except Exception as e:
            logger.error(f"Görev iptal edilirken hata oluştu: {str(e)}")
    
    # İlişkili kayıtların sayısını logla
    variant_count = SimulatedVariant.objects.filter(simulation=instance).count()
    error_count = SimulationError.objects.filter(simulation=instance).count()
    
    logger.info(f"Simülasyon ID {instance.id} ile birlikte {variant_count} varyant ve {error_count} hata kaydı silinecek")