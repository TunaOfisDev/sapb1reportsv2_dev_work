# backend/productconfig_simulator/services/simulation_job_service.py
from django.utils import timezone
from django.db.models import Q, Count, Sum
from ..models.simulation_job import SimulationJob
from ..utils.simulator_helpers import SimulationJobHelper
from .base_service import BaseService
import logging

logger = logging.getLogger(__name__)

class SimulationJobService(BaseService):
    """
    Simülasyon işlerini yönetmek için servis sınıfı.
    """
    
    def __init__(self):
        super().__init__(SimulationJob)
        self.helper = SimulationJobHelper()
    
    def create_simulation(self, data, user=None):
        """
        Yeni bir simülasyon işi oluşturur.
        
        Args:
            data (dict): Simülasyon verileri
            user: İşlemi gerçekleştiren kullanıcı
        
        Returns:
            SimulationJob: Oluşturulan simülasyon işi
        """
        level = data.get('level')
        
        # Simülasyon adını otomatik oluştur (eğer verilmemişse)
        if not data.get('name'):
            data['name'] = self._generate_simulation_name(data)
        
        # Kullanıcı bilgisini ekle
        if user:
            data['created_by'] = user
        
        # Toplam model sayısını belirle
        data['total_models'] = self.helper.calculate_total_models(
            level=level,
            brand=data.get('brand'),
            product_group=data.get('product_group'),
            category=data.get('category'),
            product_model=data.get('product_model')
        )
        
        # Simülasyon işini oluştur
        simulation = super().create(**data)
        logger.info(f"Yeni simülasyon oluşturuldu: ID={simulation.id}, Adı={simulation.name}")
        
        return simulation
    
    def get_running_simulations(self):
        """Çalışan tüm simülasyonları döndürür"""
        return self.filter_by(status=SimulationJob.SimulationStatus.RUNNING)
    
    def get_simulations_by_user(self, user):
        """Belirli bir kullanıcının simülasyonlarını döndürür"""
        return self.filter_by(created_by=user)
    
    def get_simulations_with_errors(self):
        """Hata içeren simülasyonları döndürür"""
        return self.filter_by().annotate(error_count=Count('errors')).filter(error_count__gt=0)
    
    def get_latest_completed_simulations(self, limit=10):
        """Tamamlanmış son simülasyonları döndürür"""
        return self.filter_by(status=SimulationJob.SimulationStatus.COMPLETED).order_by('-end_time')[:limit]
    
    def search_simulations(self, search_term):
        """Simülasyonlar içinde arama yapar"""
        if not search_term:
            return self.get_all()
            
        return self.filter_by(
            Q(name__icontains=search_term) |
            Q(description__icontains=search_term) |
            Q(brand__name__icontains=search_term) |
            Q(product_group__name__icontains=search_term) |
            Q(category__name__icontains=search_term) |
            Q(product_model__name__icontains=search_term)
        )
    
    def cancel_all_running_simulations(self):
        """Çalışan tüm simülasyonları iptal eder"""
        running_simulations = self.get_running_simulations()
        count = 0
        
        for simulation in running_simulations:
            simulation.cancel()
            count += 1
            
        return count
    
    def get_simulation_statistics(self):
        """Simülasyon istatistiklerini hesaplar ve döndürür"""
        all_simulations = self.get_all()
        
        return {
            'total_count': all_simulations.count(),
            'by_status': {
                'pending': all_simulations.filter(status=SimulationJob.SimulationStatus.PENDING).count(),
                'running': all_simulations.filter(status=SimulationJob.SimulationStatus.RUNNING).count(),
                'completed': all_simulations.filter(status=SimulationJob.SimulationStatus.COMPLETED).count(),
                'failed': all_simulations.filter(status=SimulationJob.SimulationStatus.FAILED).count(),
                'cancelled': all_simulations.filter(status=SimulationJob.SimulationStatus.CANCELLED).count(),
            },
            'by_level': {
                'brand': all_simulations.filter(level=SimulationJob.SimulationLevel.BRAND).count(),
                'product_group': all_simulations.filter(level=SimulationJob.SimulationLevel.PRODUCT_GROUP).count(),
                'category': all_simulations.filter(level=SimulationJob.SimulationLevel.CATEGORY).count(),
                'product_model': all_simulations.filter(level=SimulationJob.SimulationLevel.PRODUCT_MODEL).count(),
            },
            'total_variants': all_simulations.aggregate(Sum('total_variants'))['total_variants__sum'] or 0,
            'total_errors': all_simulations.aggregate(Sum('total_errors'))['total_errors__sum'] or 0,
        }
    
    def _generate_simulation_name(self, data):
        """Simülasyon verilerine göre otomatik isim oluşturur"""
        level = data.get('level')
        timestamp = timezone.now().strftime('%Y%m%d-%H%M%S')
        
        if level == SimulationJob.SimulationLevel.BRAND and data.get('brand'):
            return f"Marka-{data['brand'].name}-{timestamp}"
            
        elif level == SimulationJob.SimulationLevel.PRODUCT_GROUP and data.get('product_group'):
            return f"Grup-{data['product_group'].name}-{timestamp}"
            
        elif level == SimulationJob.SimulationLevel.CATEGORY and data.get('category'):
            return f"Kategori-{data['category'].name}-{timestamp}"
            
        elif level == SimulationJob.SimulationLevel.PRODUCT_MODEL and data.get('product_model'):
            return f"Model-{data['product_model'].name}-{timestamp}"
            
        return f"Simülasyon-{timestamp}"