# backend/productconfig_simulator/tasks.py
from celery import shared_task
import logging
from django.conf import settings
from .utils.simulators import run_simulation
from django.utils import timezone

logger = logging.getLogger(__name__)

@shared_task(bind=True, name='run_simulation_task')
def run_simulation_task(self, simulation_id, parallel=True, max_workers=4):
    """
    Simülasyon işlerini arka planda çalıştırmak için Celery görevi.
    
    Args:
        simulation_id: Simülasyon ID'si
        parallel: Paralel işleme modu
        max_workers: Paralel işlemede maksimum işlemci sayısı
        
    Returns:
        dict: Görev sonucu
    """
    task_id = self.request.id
    logger.info(f"Simülasyon görevi başlatıldı - Simulation ID: {simulation_id}, Task ID: {task_id}")
    
    # Simülasyon verilerini güncelle
    from .models.simulation_job import SimulationJob
    try:
        simulation = SimulationJob.objects.get(id=simulation_id)
        simulation.celery_task_id = task_id
        simulation.save(update_fields=['celery_task_id'])
    except SimulationJob.DoesNotExist:
        logger.error(f"Simülasyon bulunamadı - ID: {simulation_id}")
        return {
            'success': False,
            'simulation_id': simulation_id,
            'error': 'Simulation not found'
        }
    
    # Başlangıç zamanını kaydet
    start_time = timezone.now()
    
    # Simülasyonu çalıştır
    try:
        success = run_simulation(
            simulation_id=simulation_id,
            parallel=parallel,
            max_workers=max_workers
        )
        
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"Simülasyon görevi tamamlandı - Simulation ID: {simulation_id}, Duration: {duration} seconds")
        
        return {
            'success': success,
            'simulation_id': simulation_id,
            'duration': duration,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat()
        }
    except Exception as e:
        logger.error(f"Simülasyon görevi hatası - Simulation ID: {simulation_id}, Error: {str(e)}")
        
        # Simülasyonu başarısız olarak işaretle
        try:
            simulation = SimulationJob.objects.get(id=simulation_id)
            simulation.status = SimulationJob.SimulationStatus.FAILED
            simulation.end_time = timezone.now()
            simulation.save(update_fields=['status', 'end_time'])
        except Exception as update_error:
            logger.error(f"Simülasyon durumu güncellenirken hata oluştu: {str(update_error)}")
        
        return {
            'success': False,
            'simulation_id': simulation_id,
            'error': str(e),
            'start_time': start_time.isoformat(),
            'end_time': timezone.now().isoformat()
        }


@shared_task(name='cleanup_simulations')
def cleanup_simulations(days=30, status=None):
    """
    Eski simülasyonları temizlemek için Celery görevi.
    
    Args:
        days: X günden eski simülasyonları temizle
        status: Belirli bir durumda olanları temizle (opsiyonel)
        
    Returns:
        dict: Temizleme sonucu
    """
    from django.utils import timezone
    from datetime import timedelta
    from .models.simulation_job import SimulationJob
    
    cutoff_date = timezone.now() - timedelta(days=days)
    logger.info(f"Eski simülasyonlar temizleniyor - Cutoff date: {cutoff_date}")
    
    query = SimulationJob.objects.filter(created_at__lt=cutoff_date)
    if status:
        query = query.filter(status=status)
    
    # Silinecek simülasyonların ID'lerini logla
    simulation_ids = list(query.values_list('id', flat=True))
    logger.info(f"Silinecek simülasyon sayısı: {len(simulation_ids)}")
    
    # İlişkili varyantları ve hataları say
    from .models.simulated_variant import SimulatedVariant
    from .models.simulation_error import SimulationError
    
    variant_count = SimulatedVariant.objects.filter(simulation_id__in=simulation_ids).count()
    error_count = SimulationError.objects.filter(simulation_id__in=simulation_ids).count()
    
    logger.info(f"Silinecek ilişkili kayıt sayısı - Variants: {variant_count}, Errors: {error_count}")
    
    # Toplu silme işlemini gerçekleştir
    deleted_count = query.delete()[0]
    
    logger.info(f"Temizleme tamamlandı - Silinen simülasyon sayısı: {deleted_count}")
    
    return {
        'success': True,
        'cleaned_simulations': deleted_count,
        'cleaned_variants': variant_count,
        'cleaned_errors': error_count,
        'cutoff_date': cutoff_date.isoformat(),
        'status_filter': status
    }