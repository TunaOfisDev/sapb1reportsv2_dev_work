# backend/productconfig/dto/question_context.py
from django.db.models import QuerySet
from dataclasses import dataclass, field
from typing import Dict, Optional, Set
from ..models import Brand, ProductGroup, Category, ProductModel, Option, Question
import logging

logger = logging.getLogger(__name__)
# .env dosyasından ENABLE_LOGGING değişkenini kontrol et
import os
if not os.getenv('ENABLE_LOGGING', 'True').lower() == 'true':
    logger.setLevel(logging.CRITICAL)  # Loglamayı sadece CRITICAL seviyesine indir

class ChainFilter:
    def __init__(self):
        self.selected_brands = set()
        self.selected_groups = set()
        self.selected_categories = set()
        self.selected_product_models = set()

    def update_chain(self, brand_ids=None, group_ids=None, category_ids=None, product_model_ids=None):
        """
        Zinciri gunceller. Yeni gelen ID'leri mevcut ID'lerle kesistirir.
        """
        if brand_ids is not None:
            self.selected_brands &= set(brand_ids) if self.selected_brands else set(brand_ids)
        if group_ids is not None:
            self.selected_groups &= set(group_ids) if self.selected_groups else set(group_ids)
        if category_ids is not None:
            self.selected_categories &= set(category_ids) if self.selected_categories else set(category_ids)
        if product_model_ids is not None:
            self.selected_product_models &= set(product_model_ids) if self.selected_product_models else set(product_model_ids)

    def filter_options(self, options: QuerySet):
        """
        Verilen QuerySet'i zincirdeki ID'lere göre filtreler.
        """
        if self.selected_brands:
            options = options.filter(applicable_brands__id__in=self.selected_brands)
        if self.selected_groups:
            options = options.filter(applicable_groups__id__in=self.selected_groups)
        if self.selected_categories:
            options = options.filter(applicable_categories__id__in=self.selected_categories)
        if self.selected_product_models:
            options = options.filter(applicable_product_models__id__in=self.selected_product_models)
        
        return options

    def reset_chain(self):
        """
        Zinciri sifirlar.
        """
        self.selected_brands = set()
        self.selected_groups = set()
        self.selected_categories = set()
        self.selected_product_models = set()


@dataclass
class QuestionContext:
    applicable_brands: Set[int] = field(default_factory=set)
    applicable_groups: Set[int] = field(default_factory=set)
    applicable_categories: Set[int] = field(default_factory=set)
    applicable_product_models: Set[int] = field(default_factory=set)

    selected_brand: Optional[Brand] = None
    selected_group: Optional[ProductGroup] = None
    selected_category: Optional[Category] = None
    selected_model: Optional[ProductModel] = None

    selection_history: Dict = field(default_factory=dict)
    is_after_master_questions: bool = False

    chain_filter: ChainFilter = ChainFilter()

    def update_chain_from_option(self, option: Option) -> None:
        """
        Zinciri seçenege göre gunceller.
        """
        self.chain_filter.update_chain(
            brand_ids=list(option.applicable_brands.values_list('id', flat=True)) if option.applicable_brands.exists() else None,
            group_ids=list(option.applicable_groups.values_list('id', flat=True)) if option.applicable_groups.exists() else None,
            category_ids=list(option.applicable_categories.values_list('id', flat=True)) if option.applicable_categories.exists() else None,
            product_model_ids=list(option.applicable_product_models.values_list('id', flat=True)) if option.applicable_product_models.exists() else None,
        )

    def filter_options(self, options: QuerySet) -> QuerySet:
        """
        Zincirdeki degerlerle seçenekleri filtreler.
        """
        return self.chain_filter.filter_options(options)

    def deep_filter_options(self, option: Option) -> bool:
        """
        Seçenek için derin filtreleme yapar.
        Tum applicable_* alanlarinda kesisim kontrolu yapar.
        """
        try:
            # Brand kontrolu
            if self.applicable_brands and option.applicable_brands.exists():
                brand_ids = set(option.applicable_brands.values_list('id', flat=True))
                if not (self.applicable_brands & brand_ids):
                    logger.debug(f"Brand filtreleme basarisiz - Option: {option.id}")
                    return False

            # Group kontrolu
            if self.applicable_groups and option.applicable_groups.exists():
                group_ids = set(option.applicable_groups.values_list('id', flat=True))
                if not (self.applicable_groups & group_ids):
                    logger.debug(f"Group filtreleme basarisiz - Option: {option.id}")
                    return False

            # Category kontrolu
            if self.applicable_categories and option.applicable_categories.exists():
                category_ids = set(option.applicable_categories.values_list('id', flat=True))
                if not (self.applicable_categories & category_ids):
                    logger.debug(f"Category filtreleme basarisiz - Option: {option.id}")
                    return False

            # ProductModel kontrolu - Burayı düzeltiyoruz
            if self.is_after_master_questions and self.applicable_product_models:
                # Eğer master sorular tamamlandıysa ve ürün modeli filtremiz varsa
                if option.applicable_product_models.exists():
                    model_ids = set(option.applicable_product_models.values_list('id', flat=True))
                    if not (self.applicable_product_models & model_ids):
                        logger.debug(f"ProductModel filtreleme basarisiz - Option: {option.id}")
                        return False
                else:
                    # Eğer seçeneğin hiç ürün modeli bağlantısı yoksa
                    logger.debug(f"Option {option.id} herhangi bir ürün modeline bağlı değil")
                    return False

            logger.debug(f"Derin filtreleme basarili - Option: {option.id}")
            return True

        except Exception as e:
            logger.error(f"Derin filtreleme hatasi - Option {option.id}: {str(e)}")
            return False
        


    def update_from_option(self, option: Option, question_id: Optional[int] = None) -> None:
        """Seçenekten gelen degerlerle context'i gunceller."""
        try:
            # Derin filtreleme kontrolu
            if not self.deep_filter_options(option):
                logger.warning(f"Option {option.id} derin filtreleme kontrolunden geçemedi")
                return

            # Applicable alanlari guncelle
            if option.applicable_brands.exists():
                new_brand_ids = set(option.applicable_brands.values_list('id', flat=True))
                self._update_with_intersection("brands", new_brand_ids)

            if option.applicable_groups.exists():
                new_group_ids = set(option.applicable_groups.values_list('id', flat=True))
                self._update_with_intersection("groups", new_group_ids)

            if option.applicable_categories.exists():
                new_category_ids = set(option.applicable_categories.values_list('id', flat=True))
                self._update_with_intersection("categories", new_category_ids)

            if option.applicable_product_models.exists():
                new_model_ids = set(option.applicable_product_models.values_list('id', flat=True))
                self._update_with_intersection("product_models", new_model_ids)

            # Seçimi geçmise ekle
            if question_id:
                self._add_to_history(question_id, option)

            # Seçili degerleri guncelle
            self._update_selected_values(option)

            logger.debug(f"""
                Derin filtreleme sonrasi durum:
                Brands: {self.applicable_brands}
                Groups: {self.applicable_groups}
                Categories: {self.applicable_categories}
                Models: {self.applicable_product_models}
            """)

        except Exception as e:
            logger.error(f"Option guncelleme hatasi: {str(e)}")
            raise

    def _add_to_history(self, question_id: int, option: Option):
        self.selection_history[question_id] = {
            "option_id": option.id,
            "applicable_brands": list(option.applicable_brands.values_list('id', flat=True)) if option.applicable_brands.exists() else [],
            "applicable_groups": list(option.applicable_groups.values_list('id', flat=True)) if option.applicable_groups.exists() else [],
            "applicable_categories": list(option.applicable_categories.values_list('id', flat=True)) if option.applicable_categories.exists() else [],
            "applicable_product_models": list(option.applicable_product_models.values_list('id', flat=True)) if option.applicable_product_models.exists() else [],
        }
            

    def _update_selected_values(self, option: Option) -> None:
        """Seçili degerleri gunceller."""
        if option.applicable_brands.exists():
            self.selected_brand = option.applicable_brands.first()  # İlk markayi seç
        if option.applicable_groups.exists():
            self.selected_group = option.applicable_groups.first()  # İlk grubu seç
        if option.applicable_categories.exists():
            self.selected_category = option.applicable_categories.first()  # İlk kategoriyi seç
        if option.applicable_product_models.exists():
            self.selected_model = option.applicable_product_models.first()  # İlk modeli seç

        logger.debug(f"Seçilen degerler guncellendi: "
                    f"Brand: {self.selected_brand}, "
                    f"Group: {self.selected_group}, "
                    f"Category: {self.selected_category}, "
                    f"Model: {self.selected_model}")
 


    def update_from_variant_history(self, variant) -> None:
        """Variant geçmisinden context'i gunceller."""
        logger.debug(f"Variant geçmisi degerlendiriliyor - Variant ID: {variant.id}")

        # Baslangiç durumu
        self.applicable_brands.clear()
        self.applicable_groups.clear()
        self.applicable_categories.clear()
        self.applicable_product_models.clear()
        self.is_after_master_questions = False

        # Cevaplari kronolojik sirala ve isle
        sorted_answers = sorted(variant.text_answers.items(), key=lambda x: int(x[0]))
        last_master_question_answered = False

        for question_id_str, answer in sorted_answers:
            question_id = int(question_id_str)
            if 'answer_id' not in answer:
                continue

            try:
                option = Option.objects.get(id=answer['answer_id'])
                question = Question.objects.get(id=question_id)

                # Master soru kontrolu
                if question.category_type == 'master_question':
                    last_master_question_answered = True
                elif last_master_question_answered:
                    self.is_after_master_questions = True

                # **Burada applicable_* alanlarini guncelliyoruz**
                if 'applicable_brands' in answer:
                    self.applicable_brands = set(answer['applicable_brands'])
                if 'applicable_groups' in answer:
                    self.applicable_groups = set(answer['applicable_groups'])
                if 'applicable_categories' in answer:
                    self.applicable_categories = set(answer['applicable_categories'])
                if 'applicable_product_models' in answer:
                    self.applicable_product_models = set(answer['applicable_product_models'])

                # Context guncelle
                self.update_from_option(option, question_id)

            except (Option.DoesNotExist, Question.DoesNotExist) as e:
                logger.error(f"Veri getirme hatasi: {str(e)}")

    def validate_chain_consistency(self):
        """
        Markalar, gruplar, kategoriler ve modeller arasindaki zincirleme tutarliligi kontrol eder.
        """
        if not self.selected_brand or not self.selected_group or not self.selected_category:
            return False  # Her bir alanin seçili olmasi gerekiyor

        # Kategori zincirini kontrol et
        categories = Category.objects.filter(
            brand=self.selected_brand,
            product_group=self.selected_group,
            id=self.selected_category.id
        )
        if not categories.exists():
            logger.error("Marka, grup ve kategori eslesmesi tutarsiz.")
            return False

        # urun modeli zincirini kontrol et
        if self.applicable_product_models:
            models = ProductModel.objects.filter(
                id__in=self.applicable_product_models,
                category=self.selected_category
            )
            if not models.exists():
                logger.error("Kategori ve urun modeli eslesmesi tutarsiz.")
                return False

        return True

    def apply_applicable_filters(self, options: QuerySet[Option]) -> QuerySet[Option]:
        """
        Applicable alanlari kullanarak seçenekleri filtreler.
        """
        if self.applicable_brands:
            options = options.filter(applicable_brands__id__in=self.applicable_brands)
        if self.applicable_groups:
            options = options.filter(applicable_groups__id__in=self.applicable_groups)
        if self.applicable_categories:
            options = options.filter(applicable_categories__id__in=self.applicable_categories)
        if self.applicable_product_models:
            options = options.filter(applicable_product_models__id__in=self.applicable_product_models)

        options = self.apply_field_filter(options, 'brands', self.applicable_brands)
        options = self.apply_field_filter(options, 'groups', self.applicable_groups)
        options = self.apply_field_filter(options, 'categories', self.applicable_categories)
        options = self.apply_field_filter(options, 'product_models', self.applicable_product_models)

        logger.debug(f"Applicable alanlara göre filtrelenen seçenekler: {options}")
        return options.distinct()

    def apply_field_filter(self, options: QuerySet[Option], field_name: str, applicable_ids: Set[int]) -> QuerySet[Option]:
        """
        Dinamik olarak belirli bir alan için filtreleme yapar.
        """
        if applicable_ids:
            filter_key = f"applicable_{field_name}__id__in"
            options = options.filter(**{filter_key: applicable_ids})
            logger.debug(f"{field_name} için filtreleme uygulandi: {applicable_ids}")
        return options

    def validate_applicable_filters(self) -> bool:
        """
        Applicable filtrelerde tutarsizlik olup olmadigini kontrol eder.
        """
        if not self.applicable_brands and not self.applicable_groups:
            logger.error("Applicable alanlarda hiçbir geçerli marka veya grup yok.")
            raise ValueError("Geçersiz applicable filtre: Marka veya grup seçimi yapilmadi.")

        if self.applicable_product_models and not self.selected_category:
            logger.error("Applicable urun modelleri mevcut ancak kategori seçilmemis.")
            raise ValueError("Geçersiz applicable filtre: Kategori seçimi eksik.")
        
        return True

    def refine_options(self, options: QuerySet[Option]) -> QuerySet[Option]:
        """
        Seçenekleri applicable ve dinamik filtrelere göre optimize eder.
        """
        self.validate_applicable_filters()
        options = self.apply_applicable_filters(options)
        options = self.apply_additional_filters(options)
        logger.debug(f"Son filtreleme sonrasi seçenekler: {options}")
        return options

    def _apply_default_context(self, context, question, answer):
        """
        Baglamin bosoldugu durumlarda varsayilan degerleri uygular.
        Varsayilan kategori, marka, grup ve model atanir.
        """
        try:
            # Varsayilan kategori seçimi
            default_category = Category.objects.filter(is_active=True).first()
            if default_category:
                context.selected_category = default_category
                context.applicable_categories.add(default_category.id)
                logger.debug(f"Varsayilan kategori atandi: {default_category.name}")

            # Varsayilan marka seçimi
            default_brand = Brand.objects.filter(is_active=True).first()
            if default_brand:
                context.selected_brand = default_brand
                context.applicable_brands.add(default_brand.id)
                logger.debug(f"Varsayilan marka atandi: {default_brand.name}")

            # Varsayilan grup seçimi
            default_group = ProductGroup.objects.filter(is_active=True).first()
            if default_group:
                context.selected_group = default_group
                context.applicable_groups.add(default_group.id)
                logger.debug(f"Varsayilan grup atandi: {default_group.name}")

            # Varsayilan urun modelleri
            if default_category:
                default_models = ProductModel.objects.filter(category=default_category, is_active=True)
                if default_models.exists():
                    context.applicable_product_models.update(default_models.values_list('id', flat=True))
                    logger.debug(f"Varsayilan modeller atandi: {list(default_models.values_list('name', flat=True))}")
                else:
                    logger.warning("Varsayilan kategoriye bagli model bulunamadi.")

        except Exception as e:
            logger.error(f"_apply_default_context sirasinda hata: {str(e)}")
            raise


    def apply_additional_filters(self, options: QuerySet[Option]) -> QuerySet[Option]:
        """
        Uygulanan ek filtreleri içeren fonksiyon.
        Ek filtreleme kurallarini buraya ekler.
        """
        try:
            # 1. Sadece aktif seçenekler
            options = options.filter(is_active=True)
            logger.debug(f"Ek filtre: Aktif seçenekler filtrelendi. Kalan seçenekler: {options.count()}")

            # 2. Populer seçenekler varsa öncelik ver
            if hasattr(self, "is_popular_filter") and self.is_popular_filter:
                options = options.filter(is_popular=True)
                logger.debug(f"Ek filtre: Populer seçenekler filtrelendi. Kalan seçenekler: {options.count()}")

            # 3. Fiyat araligi filtresi
            if hasattr(self, "price_min") and hasattr(self, "price_max"):
                options = options.filter(price_modifier__gte=self.price_min, price_modifier__lte=self.price_max)
                logger.debug(f"Ek filtre: Fiyat araligi ({self.price_min} - {self.price_max}) filtrelendi. Kalan seçenekler: {options.count()}")

            # 4. Anahtar kelime ile filtreleme (istege bagli)
            if hasattr(self, "keyword_filter") and self.keyword_filter:
                options = options.filter(name__icontains=self.keyword_filter)
                logger.debug(f"Ek filtre: Anahtar kelime ({self.keyword_filter}) filtrelendi. Kalan seçenekler: {options.count()}")

            # 5. Özel ismantiklari
            # İstege göre burada baska filtreleme kurallari eklenebilir.
            # Örnegin: Belirli bir kategori veya urun modeli bazinda özel filtreleme.

            # Sonuçlari distinct hale getir
            options = options.distinct()
            logger.debug(f"apply_additional_filters sonrasi seçenekler: {list(options.values_list('name', flat=True))}")

            return options

        except Exception as e:
            logger.error(f"apply_additional_filters sirasinda hata: {str(e)}")
            raise


    def reset_chain(self):
        """
        Zinciri sifirlar.
        """
        self.selected_brands = set()
        self.selected_groups = set()
        self.selected_categories = set()
        self.selected_product_models = set()

    def refine_options_by_previous_selections(self, context, current_options: QuerySet[Option]) -> QuerySet[Option]:
        """
        Önceki seçimlere ve mevcut baglama (context) göre seçenekleri filtreler.
        """
        try:
            # 1. Eger baglamda aktif filtre yoksa, mevcut seçenekleri oldugu gibi döndur
            if not context.has_filters:
                logger.debug("Baglamda aktif filtre yok, tum seçenekler dönduruluyor.")
                return current_options

            # 2. Applicable filtreleri uygula
            filtered_options = context.apply_applicable_filters(current_options)
            logger.debug(f"Applicable filtre sonrasi seçenekler: {list(filtered_options.values_list('name', flat=True))}")

            # 3. Seçim geçmisine göre filtreleme yap
            selection_history = context.selection_history
            category_ids = set()
            model_ids = set()

            # Seçim geçmisinden applicable alanlari topla
            for answer in selection_history.values():
                if 'applicable_categories' in answer:
                    category_ids.update(answer['applicable_categories'])
                if 'applicable_product_models' in answer:
                    model_ids.update(answer['applicable_product_models'])

            # 4. Kategori bazli filtreleme
            if category_ids:
                filtered_options = filtered_options.filter(applicable_categories__id__in=category_ids)
                logger.debug(f"Kategori bazli filtre sonrasi seçenekler: {list(filtered_options.values_list('name', flat=True))}")

            # 5. urun modeli bazli filtreleme (Master sorular sonrasi)
            if model_ids and context.is_after_master_questions:
                filtered_options = filtered_options.filter(applicable_product_models__id__in=model_ids)
                logger.debug(f"urun modeli bazli filtre sonrasi seçenekler: {list(filtered_options.values_list('name', flat=True))}")

            # 6. Ek filtreler uygula
            filtered_options = context.apply_additional_filters(filtered_options)
            logger.debug(f"Ek filtre sonrasi seçenekler: {list(filtered_options.values_list('name', flat=True))}")

            # 7. Sonuçlari distinct olarak döndur
            return filtered_options.distinct()

        except Exception as e:
            logger.error(f"Seçenekleri filtrelerken hata olustu: {str(e)}")
            raise

    @property
    def has_filters(self) -> bool:
        """Aktif filtre varligini kontrol eder."""
        return any([
            self.applicable_brands,
            self.applicable_groups,
            self.applicable_categories,
            self.applicable_product_models
        ])
    
    def _update_with_intersection(self, field_type: str, new_ids: Set[int]) -> None:
        """
        Belirli bir alani guncellemek için set operasyonlarini kullanir.
        """
        field_map = {
            "brands": self.applicable_brands,
            "groups": self.applicable_groups,
            "categories": self.applicable_categories,
            "product_models": self.applicable_product_models
        }

        current_set = field_map[field_type]

        if not current_set:
            # Eger mevcut set bossa, yeni ID'leri ekle
            current_set.update(new_ids)
            logger.debug(f"{field_type} alani ilk kez guncelleniyor: {new_ids}")
        else:
            # Mevcut set ile yeni ID'lerin kesisimini al
            intersection = current_set & new_ids
            current_set.clear()
            current_set.update(intersection)
            logger.debug(f"{field_type} alani kesisim sonucu guncellendi: {intersection}")
    
    def is_applicable_with_question(self, question: Question) -> bool:
        """
        Sorunun context'e uygun olup olmadığını kontrol eder.
        """
        # Master sorular her zaman uygundur
        if question.category_type == Question.QuestionCategoryType.MASTER_QUESTION:
            return True

        # Ürün modeliyle ilişkili sorular
        if question.applicable_product_models.exists() and self.is_after_master_questions:
            model_ids = set(question.applicable_product_models.values_list('id', flat=True))
            return bool(self.applicable_product_models & model_ids)

        return False

    
    def evaluate_chain_applicability(self, question):
        """Zincir uygunlugunu kontrol eder."""
        # Marka kontrolu
        if question.applicable_brands.exists():
            brand_ids = set(question.applicable_brands.values_list('id', flat=True))
            if not (self.applicable_brands & brand_ids):
                return False
                
        # Kategori kontrolu
        if question.applicable_categories.exists():
            category_ids = set(question.applicable_categories.values_list('id', flat=True))
            if not (self.applicable_categories & category_ids):
                return False
                
        # Model kontrolu
        if question.applicable_product_models.exists() and self.is_after_master_questions:
            model_ids = set(question.applicable_product_models.values_list('id', flat=True))
            if not (self.applicable_product_models & model_ids):
                return False
                
        return True