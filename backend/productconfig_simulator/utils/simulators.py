# backend/productconfig_simulator/utils/simulators.py
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.utils import timezone
from django.db import transaction

from productconfig.models import (
    Brand, ProductGroup, Category, ProductModel, 
    Question, Option, DependentRule, ConditionalOption
)

from .simulator_helpers import SimulationJobHelper
from .variant_helpers import SimulatedVariantHelper
from .error_helpers import SimulationErrorHelper

logger = logging.getLogger(__name__)

class Simulator:
    """
    Simulasyon islemlerini yuruten temel sinif.
    """
    def __init__(self, simulation_job):
        self.simulation = simulation_job
        self.simulation_helper = SimulationJobHelper()
        self.variant_helper = SimulatedVariantHelper()
        self.error_helper = SimulationErrorHelper()
        self.processed_models = 0
        self.total_variants = 0
        self.total_errors = 0
    
    def run(self):
        """
        Simulasyonu calistirir.
        """
        try:
            # Simulasyon baslangicini kaydet
            self.simulation.start()
            logger.info(f"Simulasyon baslatildi: ID={self.simulation.id}, Adi={self.simulation.name}")
            
            # urun modellerini getir
            product_models = self.simulation_helper.get_product_models_for_simulation(
                level=self.simulation.level,
                brand=self.simulation.brand,
                product_group=self.simulation.product_group,
                category=self.simulation.category,
                product_model=self.simulation.product_model
            )
            
            # urun modeli yoksa hata
            if not product_models.exists():
                self.simulation.fail("Belirlenen kriterlere uygun urun modeli bulunamadi.")
                logger.warning(f"Simulasyon basarisiz: urun modeli bulunamadi - ID={self.simulation.id}")
                return
            
            # Toplam model sayisini guncelle
            self.simulation.total_models = product_models.count()
            self.simulation.save()
            
            # Her model icin simulasyon islemi
            for product_model in product_models:
                try:
                    # urun modeli verilerini kontrol et
                    data_quality = self.simulation_helper.check_model_data_quality(product_model)
                    
                    # Veri kalitesi sorunlari varsa hatalari kaydet
                    if not data_quality['is_valid']:
                        self._record_data_quality_errors(product_model, data_quality)
                        
                    # Varyantlari olustur
                    self._process_product_model(product_model)
                    
                    # islenen model sayisini guncelle
                    self.processed_models += 1
                    self._update_progress()
                    
                except Exception as e:
                    # Hata kaydi
                    from ..models.simulation_error import SimulationError
                    SimulationError.objects.create(
                        simulation=self.simulation,
                        error_type='processing_error',
                        severity='error',
                        message=f"Model isleme hatasi: {str(e)}",
                        product_model=product_model,
                        details={'error': str(e)}
                    )
                    self.total_errors += 1
                    self._update_progress()
                    logger.error(f"urun modeli isleme hatasi - ID={product_model.id}: {str(e)}")
            
            # Simulasyonu tamamla
            self.simulation.complete()
            logger.info(f"Simulasyon tamamlandi: ID={self.simulation.id}, Toplam varyant={self.total_variants}, Toplam hata={self.total_errors}")
            
        except Exception as e:
            # Genel hata
            self.simulation.fail(str(e))
            logger.error(f"Simulasyon calistirma hatasi - ID={self.simulation.id}: {str(e)}")
    
    def _process_product_model(self, product_model):
        # Varyantları oluşturmadan önce "Proje Nedir" sorusuna varsayılan cevap hazırla
        initial_question = Question.objects.filter(
            applicable_product_models=product_model,
            is_active=True
        ).order_by('order').first()
        
        initial_answers = {}
        if initial_question and initial_question.name == "Proje Nedir":
            initial_answers[str(initial_question.id)] = {
                "question_id": initial_question.id,
                "answer_text": f"Simülasyon Projesi - {product_model.name}"
            }
        
        # Varyantları oluştur
        variants = self.variant_helper.generate_variants_for_model(
            product_model=product_model,
            max_variants=self.simulation.max_variants_per_model,
            include_dependent_rules=self.simulation.include_dependent_rules,
            include_conditional_options=self.simulation.include_conditional_options,
            include_price_multipliers=self.simulation.include_price_multipliers,
            initial_answers=initial_answers  # Önceden hazırlanmış cevapları ekle
        )
            
        # Varyantlari veritabanina kaydet
        total_saved = 0
        if variants:
            total_saved = self._save_variants(variants)
        
        # istatistikleri guncelle
        self.total_variants += total_saved
        
        logger.info(f"urun modeli islendi: ID={product_model.id}, Ad={product_model.name}, Varyant sayisi={total_saved}")
    
    def _save_variants(self, variants):
        """
        Olusturulan varyantlari veritabanina kaydeder.
        
        Args:
            variants: Olusturulan varyant listesi
            
        Returns:
            int: Kaydedilen varyant sayisi
        """
        # Bos liste kontrolu
        if not variants:
            return 0
        
        try:
            # islem sayisini sinirla
            batch_size = 500
            variant_count = len(variants)
            total_saved = 0
            
            # Gruplar halinde isle
            for i in range(0, variant_count, batch_size):
                batch = variants[i:i+batch_size]
                
                with transaction.atomic():
                    from ..services.simulated_variant_service import SimulatedVariantService
                    variant_service = SimulatedVariantService()
                    
                    # Her gruptaki varyantlari topluca olustur
                    # ilk parametre urun modeli iceren ilk varyantin product_model degerini alir
                    saved_count = variant_service.bulk_create_variants(
                        simulation=self.simulation,
                        product_model=batch[0]['product_model'],
                        variant_data_list=batch
                    )
                    
                    total_saved += saved_count
                
                # ilerlemeyi guncelle
                self._update_progress()
            
            return total_saved
            
        except Exception as e:
            logger.error(f"Toplu varyant olusturma hatasi: {str(e)}")
            return 0
    
    def _record_data_quality_errors(self, product_model, data_quality):
        """
        Veri kalitesi sorunlarini hata kayitlari olarak ekler.
        
        Args:
            product_model: urun modeli
            data_quality: Veri kalitesi kontrolunun sonuclari
        """
        # Secenegi olmayan sorular icin hata kayitlari
        for missing_option in data_quality.get('missing_options', []):
            from ..models.simulation_error import SimulationError
            try:
                question = Question.objects.get(id=missing_option['question_id'])
                
                SimulationError.objects.create(
                    simulation=self.simulation,
                    error_type='missing_options',
                    severity='error',
                    message=f"Soru '{question.name}' icin secenek bulunamadi",
                    product_model=product_model,
                    question=question,
                    details=missing_option
                )
                
                self.total_errors += 1
                
            except Question.DoesNotExist:
                logger.warning(f"Soru bulunamadi - ID={missing_option['question_id']}")
        
        # Bagimli kural sorunlari icin hata kayitlari
        for rule_issue in data_quality.get('dependent_rule_issues', []):
            from ..models.simulation_error import SimulationError
            
            SimulationError.objects.create(
                simulation=self.simulation,
                error_type='dependent_rule_error',
                severity='warning',
                message=f"Bagimli kural sorunu: {rule_issue['rule_name']}",
                product_model=product_model,
                details=rule_issue
            )
            
            self.total_errors += 1
    
    def _update_progress(self):
        """
        Simulasyon ilerleme durumunu gunceller.
        """
        self.simulation.update_progress(
            processed_models=self.processed_models,
            total_variants=self.total_variants,
            total_errors=self.total_errors
        )


class ParallelSimulator(Simulator):
    """
    coklu islem ile simulasyon yapan sinif.
    """
    def __init__(self, simulation_job, max_workers=4):
        super().__init__(simulation_job)
        self.max_workers = max_workers
    
    def run(self):
        """
        Simulasyonu paralel calistirir.
        """
        try:
            # Simulasyon baslangicini kaydet
            self.simulation.start()
            logger.info(f"Paralel simulasyon baslatildi: ID={self.simulation.id}, Adi={self.simulation.name}, calisan sayisi={self.max_workers}")
            
            # urun modellerini getir
            product_models = self.simulation_helper.get_product_models_for_simulation(
                level=self.simulation.level,
                brand=self.simulation.brand,
                product_group=self.simulation.product_group,
                category=self.simulation.category,
                product_model=self.simulation.product_model
            )
            
            # urun modeli yoksa hata
            if not product_models.exists():
                self.simulation.fail("Belirlenen kriterlere uygun urun modeli bulunamadi.")
                logger.warning(f"Simulasyon basarisiz: urun modeli bulunamadi - ID={self.simulation.id}")
                return
            
            # Toplam model sayisini guncelle
            self.simulation.total_models = product_models.count()
            self.simulation.save()
            
            # islemcileri hazirla
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Her model icin is planla
                future_to_model = {
                    executor.submit(self._process_model_task, model): model 
                    for model in product_models
                }
                
                # islemler tamamlandikca sonuclari isle
                for future in as_completed(future_to_model):
                    model = future_to_model[future]
                    try:
                        # islem sonucunu al
                        variants_count, errors_count = future.result()
                        
                        # istatistikleri guncelle
                        self.processed_models += 1
                        self.total_variants += variants_count
                        self.total_errors += errors_count
                        
                        # ilerlemeyi guncelle
                        self._update_progress()
                        
                        logger.info(f"Model islendi: ID={model.id}, Varyant sayisi={variants_count}, Hata sayisi={errors_count}")
                    except Exception as e:
                        logger.error(f"Model isleme hatasi - ID={model.id}: {str(e)}")
                        self.total_errors += 1
                        self._update_progress()
            
            # Simulasyonu tamamla
            self.simulation.complete()
            logger.info(f"Paralel simulasyon tamamlandi: ID={self.simulation.id}, Toplam varyant={self.total_variants}, Toplam hata={self.total_errors}")
            
        except Exception as e:
            # Genel hata
            self.simulation.fail(str(e))
            logger.error(f"Paralel simulasyon calistirma hatasi - ID={self.simulation.id}: {str(e)}")
    
    def _process_model_task(self, product_model):
        """
        Bir islemci (thread) icin model isleme gorevi.
        
        Args:
            product_model: islenecek urun modeli
            
        Returns:
            tuple: (Olusturulan varyant sayisi, Olusturulan hata sayisi)
        """
        variants_count = 0
        errors_count = 0
        
        try:
            # urun modeli verilerini kontrol et
            data_quality = self.simulation_helper.check_model_data_quality(product_model)
            
            # Veri kalitesi sorunlari varsa hatalari kaydet
            if not data_quality['is_valid']:
                errors = self._record_data_quality_errors_parallel(product_model, data_quality)
                errors_count += len(errors)
            
            # Varyantlari olustur
            variants = self.variant_helper.generate_variants_for_model(
                product_model=product_model,
                max_variants=self.simulation.max_variants_per_model,
                include_dependent_rules=self.simulation.include_dependent_rules,
                include_conditional_options=self.simulation.include_conditional_options,
                include_price_multipliers=self.simulation.include_price_multipliers
            )
            
            # Varyantlari veritabanina kaydet
            if variants:
                # Veritabani islemleri icin atomic transaction kullan
                with transaction.atomic():
                    from ..services.simulated_variant_service import SimulatedVariantService
                    variant_service = SimulatedVariantService()
                    
                    saved_count = variant_service.bulk_create_variants(
                        simulation=self.simulation,
                        product_model=product_model,
                        variant_data_list=variants
                    )
                    
                    variants_count += saved_count
            
            return variants_count, errors_count
            
        except Exception as e:
            # Hata kaydi
            logger.error(f"Paralel model isleme hatasi - ID={product_model.id}: {str(e)}")
            # Exception sebebiyle islem durmaz
            return variants_count, errors_count + 1
    
    def _record_data_quality_errors_parallel(self, product_model, data_quality):
        """
        Veri kalitesi sorunlarini paralel olarak hata kayitlari olarak ekler.
        
        Args:
            product_model: urun modeli
            data_quality: Veri kalitesi kontrolunun sonuclari
            
        Returns:
            list: Olusturulan hata kayitlari
        """
        from ..models.simulation_error import SimulationError
        errors = []
        
        # Secenegi olmayan sorular icin hata kayitlari
        for missing_option in data_quality.get('missing_options', []):
            try:
                question = Question.objects.get(id=missing_option['question_id'])
                
                error = SimulationError.objects.create(
                    simulation=self.simulation,
                    error_type='missing_options',
                    severity='error',
                    message=f"Soru '{question.name}' icin secenek bulunamadi",
                    product_model=product_model,
                    question=question,
                    details=missing_option
                )
                
                errors.append(error)
                
            except Question.DoesNotExist:
                logger.warning(f"Soru bulunamadi - ID={missing_option['question_id']}")
        
        # Bagimli kural sorunlari icin hata kayitlari
        for rule_issue in data_quality.get('dependent_rule_issues', []):
            error = SimulationError.objects.create(
                simulation=self.simulation,
                error_type='dependent_rule_error',
                severity='warning',
                message=f"Bagimli kural sorunu: {rule_issue['rule_name']}",
                product_model=product_model,
                details=rule_issue
            )
            
            errors.append(error)
            
        return errors


class SimulatorFactory:
    """
    Simulator nesneleri olusturmak icin fabrika sinifi.
    """
    @staticmethod
    def create_simulator(simulation_job, parallel=False, max_workers=4):
        """
        Uygun simulator nesnesini olusturur.
        
        Args:
            simulation_job: Simulasyon isi
            parallel: Paralel isleme modu
            max_workers: Paralel islemede maksimum islemci sayisi
            
        Returns:
            Simulator: Olusturulan simulator
        """
        if parallel:
            return ParallelSimulator(simulation_job, max_workers)
        else:
            return Simulator(simulation_job)


def run_simulation(simulation_id, parallel=False, max_workers=4):
    """
    Belirli bir simulasyonu calistirmak icin kolaylik fonksiyonu.
    
    Args:
        simulation_id: Simulasyon ID'si
        parallel: Paralel isleme modu
        max_workers: Paralel islemede maksimum islemci sayisi
        
    Returns:
        bool: Basari durumu
    """
    from ..models.simulation_job import SimulationJob
    
    try:
        # Simulasyon isini getir
        simulation = SimulationJob.objects.get(id=simulation_id)
        
        # Simulator olustur
        simulator = SimulatorFactory.create_simulator(
            simulation_job=simulation,
            parallel=parallel,
            max_workers=max_workers
        )
        
        # Simulasyonu calistir
        simulator.run()
        
        return True
        
    except SimulationJob.DoesNotExist:
        logger.error(f"Simulasyon bulunamadi - ID={simulation_id}")
        return False
    except Exception as e:
        logger.error(f"Simulasyon calistirma hatasi - ID={simulation_id}: {str(e)}")
        return False