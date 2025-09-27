# backend/productconfig_simulator/utils/error_helpers.py
import json
import logging
from collections import defaultdict
from django.db.models import Count, Q
from django.utils import timezone

logger = logging.getLogger(__name__)

class SimulationErrorHelper:
    """
    SimulationError modeli için yardımcı fonksiyonlar içeren sınıf.
    """
    
    def group_errors_by_type(self, errors):
        """
        Hataları türlerine göre gruplar.
        
        Args:
            errors: Hata queryset'i
            
        Returns:
            dict: Türlerine göre gruplanmış hatalar
        """
        grouped_errors = defaultdict(list)
        
        for error in errors:
            grouped_errors[error.error_type].append(error)
            
        return dict(grouped_errors)
    
    def group_errors_by_product_model(self, errors):
        """
        Hataları ürün modellerine göre gruplar.
        
        Args:
            errors: Hata queryset'i
            
        Returns:
            dict: Ürün modellerine göre gruplanmış hatalar
        """
        grouped_errors = defaultdict(list)
        
        for error in errors:
            if error.product_model:
                key = f"{error.product_model.id}-{error.product_model.name}"
            else:
                key = "no_product_model"
                
            grouped_errors[key].append(error)
            
        return dict(grouped_errors)
    
    def generate_error_report(self, errors):
        """
        Hatalar için kapsamlı bir rapor oluşturur.
        
        Args:
            errors: Hata queryset'i
            
        Returns:
            dict: Hata raporu
        """
        total_errors = errors.count()
        
        if total_errors == 0:
            return {
                'total_count': 0,
                'report_time': timezone.now().isoformat(),
                'summary': "Hiç hata bulunamadı.",
                'by_type': {},
                'by_severity': {},
                'by_product_model': {},
                'details': []
            }
            
        # Türlere göre dağılım
        by_type = errors.values('error_type') \
                       .annotate(count=Count('id')) \
                       .order_by('error_type')
                       
        # Önem derecelerine göre dağılım
        by_severity = errors.values('severity') \
                           .annotate(count=Count('id')) \
                           .order_by('severity')
                          
        # Ürün modellerine göre dağılım
        by_model = errors.values('product_model__id', 'product_model__name') \
                         .annotate(count=Count('id')) \
                         .order_by('-count')
                         
        # Genel hata özeti
        summary = f"{total_errors} adet hata bulundu. "
        
        # En yaygın hata tipini bul
        if by_type:
            most_common_type = max(by_type, key=lambda x: x['count'])
            summary += f"En yaygın hata tipi: {most_common_type['error_type']} ({most_common_type['count']} adet). "
            
        # En yaygın önem derecesini bul
        if by_severity:
            most_common_severity = max(by_severity, key=lambda x: x['count'])
            summary += f"En yaygın önem derecesi: {most_common_severity['severity']} ({most_common_severity['count']} adet). "
            
        # Tüm hataların detayları
        details = []
        for error in errors:
            details.append({
                'id': error.id,
                'error_type': error.error_type,
                'severity': error.severity,
                'message': error.message,
                'product_model': {
                    'id': error.product_model.id,
                    'name': error.product_model.name
                } if error.product_model else None,
                'question': {
                    'id': error.question.id,
                    'name': error.question.name
                } if error.question else None,
                'option': {
                    'id': error.option.id,
                    'name': error.option.name
                } if error.option else None,
                'details': error.details,
                'resolved': error.resolution_status,
                'created_at': error.created_at.isoformat() if error.created_at else None
            })
            
        return {
            'total_count': total_errors,
            'report_time': timezone.now().isoformat(),
            'summary': summary,
            'by_type': {item['error_type']: item['count'] for item in by_type},
            'by_severity': {item['severity']: item['count'] for item in by_severity},
            'by_product_model': [
                {
                    'id': item['product_model__id'],
                    'name': item['product_model__name'] or 'Bilinmeyen Model',
                    'count': item['count']
                } for item in by_model if item['product_model__id'] is not None
            ],
            'details': details
        }
    
    def generate_error_fix_suggestions(self, error):
        """
        Bir hata için çözüm önerileri üretir.
        
        Args:
            error: Hata nesnesi
            
        Returns:
            list: Çözüm önerileri listesi
        """
        suggestions = []
        
        # Hata tipine göre öneriler
        if error.error_type == 'missing_options':
            suggestions.append("Bu soru için uygun seçenek(ler) ekleyin.")
            suggestions.append("Sorunun 'question_option_relations' kayıtlarını kontrol edin.")
            suggestions.append("Seçeneklerin 'applicable_product_models' alanlarında ürün modelinin seçili olduğunu doğrulayın.")
            
        elif error.error_type == 'dependent_rule_error':
            suggestions.append("Bağımlı kural tanımını kontrol edin ve düzeltin.")
            suggestions.append("Tetikleyici seçeneğin ürün modeli için uygun olduğunu doğrulayın.")
            suggestions.append("Bağımlı soruların ürün modeli için uygun olduğunu doğrulayın.")
            
        elif error.error_type == 'conditional_option_error':
            suggestions.append("Koşullu seçenek tanımını kontrol edin ve düzeltin.")
            suggestions.append("Tetikleyici seçeneklerin ürün modeli için uygun olduğunu doğrulayın.")
            suggestions.append("Hedef sorunun ürün modeli için uygun olduğunu doğrulayın.")
            
        elif error.error_type == 'price_multiplier_error':
            suggestions.append("Fiyat çarpan kuralını kontrol edin ve düzeltin.")
            suggestions.append("Hedef seçeneğin fiyat verilerini kontrol edin.")
            
        elif error.error_type == 'data_inconsistency':
            suggestions.append("Veri tutarsızlığı için ilgili modellerin ilişkilerini kontrol edin.")
            
        else:  # processing_error ve diğerleri
            suggestions.append("Hatanın detaylarını inceleyerek işlem sürecini kontrol edin.")
            
        # Genel öneriler
        suggestions.append("Veri tutarlılığını kontrol edin.")
        
        return suggestions
    
    def format_error_for_display(self, error):
        """
        Hatayı görüntülemek için formatlar.
        
        Args:
            error: Hata nesnesi
            
        Returns:
            dict: Görüntüleme için formatlanmış hata
        """
        result = {
            'id': error.id,
            'error_type': error.error_type,
            'error_type_display': error.get_error_type_display(),
            'severity': error.severity,
            'severity_display': error.get_severity_display(),
            'message': error.message,
            'details': error.details,
            'resolution_status': error.resolution_status,
            'created_at': error.created_at.isoformat() if error.created_at else None,
            'simulation_id': error.simulation.id,
            'related_objects': {}
        }
        
        # İlgili objeleri ekle
        if error.product_model:
            result['related_objects']['product_model'] = {
                'id': error.product_model.id,
                'name': error.product_model.name,
                'link': f"/admin/productconfig/productmodel/{error.product_model.id}/change/"
            }
            
        if error.question:
            result['related_objects']['question'] = {
                'id': error.question.id,
                'name': error.question.name,
                'link': f"/admin/productconfig/question/{error.question.id}/change/"
            }
            
        if error.option:
            result['related_objects']['option'] = {
                'id': error.option.id,
                'name': error.option.name,
                'link': f"/admin/productconfig/option/{error.option.id}/change/"
            }
            
        # Çözüm bilgilerini ekle
        if error.resolution_status:
            result['resolution'] = {
                'resolved_by': error.resolved_by.username if error.resolved_by else None,
                'resolved_at': error.resolved_at.isoformat() if error.resolved_at else None,
                'resolution_notes': error.resolution_notes
            }
            
        # Çözüm önerilerini ekle
        result['fix_suggestions'] = self.generate_error_fix_suggestions(error)
        
        return result