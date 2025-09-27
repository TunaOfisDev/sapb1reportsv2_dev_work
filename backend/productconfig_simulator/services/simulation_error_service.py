# backend/productconfig_simulator/services/simulation_error_service.py
from django.db.models import Count, Q
from django.utils import timezone
import logging

from ..models.simulation_error import SimulationError
from ..utils.error_helpers import SimulationErrorHelper
from .base_service import BaseService

logger = logging.getLogger(__name__)

class SimulationErrorService(BaseService):
    """
    Simülasyon hatalarını yönetmek için servis sınıfı.
    """
    
    def __init__(self):
        super().__init__(SimulationError)
        self.helper = SimulationErrorHelper()
    
    def get_errors_by_simulation(self, simulation_id):
        """Belirli bir simülasyona ait tüm hataları döndürür"""
        return self.filter_by(simulation_id=simulation_id)
    
    def get_unresolved_errors(self):
        """Çözülmemiş tüm hataları döndürür"""
        return self.filter_by(resolution_status=False)
    
    def get_errors_by_type(self, error_type, simulation_id=None):
        """Belirli bir türdeki hataları döndürür"""
        filters = {'error_type': error_type}
        if simulation_id:
            filters['simulation_id'] = simulation_id
        return self.filter_by(**filters)
    
    def get_critical_errors(self, simulation_id=None):
        """Kritik hataları döndürür"""
        filters = {'severity': SimulationError.ErrorSeverity.CRITICAL}
        if simulation_id:
            filters['simulation_id'] = simulation_id
        return self.filter_by(**filters)
    
    def create_error(self, simulation, error_type, message, severity=SimulationError.ErrorSeverity.ERROR, 
                    product_model=None, question=None, option=None, details=None):
        """
        Yeni bir simülasyon hatası oluşturur.
        
        Args:
            simulation: Simülasyon işi
            error_type: Hata tipi
            message: Hata mesajı
            severity: Hata önem derecesi
            product_model: İlgili ürün modeli (opsiyonel)
            question: İlgili soru (opsiyonel)
            option: İlgili seçenek (opsiyonel)
            details: Hata detayları (opsiyonel)
            
        Returns:
            SimulationError: Oluşturulan hata
        """
        error = SimulationError(
            simulation=simulation,
            error_type=error_type,
            severity=severity,
            message=message,
            product_model=product_model,
            question=question,
            option=option,
            details=details or {}
        )
        error.save()
        
        # Simülasyondaki toplam hata sayısını güncelle
        simulation.total_errors = SimulationError.objects.filter(simulation=simulation).count()
        simulation.save(update_fields=['total_errors'])
        
        logger.info(f"Yeni simülasyon hatası kaydedildi: ID={error.id}, Tür={error_type}, Mesaj={message}")
        return error
    
    def resolve_error(self, error_id, user=None, notes=None):
        """
        Bir hatayı çözüldü olarak işaretler.
        
        Args:
            error_id: Hata ID'si
            user: Hatayı çözen kullanıcı
            notes: Çözüm notları
            
        Returns:
            SimulationError: Güncellenen hata
        """
        error = self.get_by_id(error_id)
        error.resolve(user=user, notes=notes)
        logger.info(f"Hata çözüldü olarak işaretlendi: ID={error_id}, Kullanıcı={user}")
        return error
    
    def bulk_resolve_errors(self, error_ids, user=None, notes=None):
        """
        Birden çok hatayı toplu olarak çözüldü olarak işaretler.
        
        Args:
            error_ids: Hata ID'leri listesi
            user: Hatayı çözen kullanıcı
            notes: Çözüm notları
            
        Returns:
            int: Çözülen hata sayısı
        """
        errors = self.filter_by(id__in=error_ids, resolution_status=False)
        resolved_count = 0
        
        for error in errors:
            error.resolution_status = True
            error.resolved_by = user
            error.resolved_at = timezone.now()
            if notes:
                error.resolution_notes = notes
            error.save()
            resolved_count += 1
        
        logger.info(f"{resolved_count} adet hata toplu olarak çözüldü olarak işaretlendi")
        return resolved_count
    
    def get_error_statistics(self, simulation_id=None):
        """
        Hata istatistiklerini hesaplar ve döndürür.
        
        Args:
            simulation_id: Simülasyon ID'si (None ise tüm hatalar için)
            
        Returns:
            dict: Hata istatistikleri
        """
        errors = self.get_all()
        if simulation_id:
            errors = errors.filter(simulation_id=simulation_id)
        
        # Hata türlerine göre sayılar
        by_type = errors.values('error_type') \
                       .annotate(count=Count('id')) \
                       .order_by('error_type')
        
        # Hata önem derecelerine göre sayılar
        by_severity = errors.values('severity') \
                           .annotate(count=Count('id')) \
                           .order_by('severity')
        
        # Çözüm durumuna göre sayılar
        resolution_stats = {
            'resolved': errors.filter(resolution_status=True).count(),
            'unresolved': errors.filter(resolution_status=False).count(),
        }
        
        return {
            'total_count': errors.count(),
            'by_type': {item['error_type']: item['count'] for item in by_type},
            'by_severity': {item['severity']: item['count'] for item in by_severity},
            'resolution_stats': resolution_stats
        }
    
    def generate_error_report(self, simulation_id):
        """
        Belirli bir simülasyon için kapsamlı hata raporu oluşturur.
        
        Args:
            simulation_id: Simülasyon ID'si
            
        Returns:
            dict: Hata raporu
        """
        return self.helper.generate_error_report(
            self.get_errors_by_simulation(simulation_id)
        )
    
    def search_errors(self, search_term, simulation_id=None):
        """
        Hatalar içinde arama yapar.
        
        Args:
            search_term: Arama terimi
            simulation_id: Simülasyon ID'si (opsiyonel)
            
        Returns:
            QuerySet: Arama sonuçları
        """
        if not search_term:
            return self.get_errors_by_simulation(simulation_id) if simulation_id else self.get_all()
        
        query = Q(message__icontains=search_term) | \
                Q(product_model__name__icontains=search_term) | \
                Q(question__name__icontains=search_term) | \
                Q(option__name__icontains=search_term)
        
        errors = self.filter_by(query)
        if simulation_id:
            errors = errors.filter(simulation_id=simulation_id)
            
        return errors