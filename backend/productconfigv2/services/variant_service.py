from django.db import transaction
from django.core.exceptions import ValidationError
from ..models import (
    Variant, VariantSelection, Product,
    SpecificationType, SpecOption,
    ProductSpecification, SpecificationOption
)
from ..utils.price_calculator import calculate_variant_price
from ..utils.variant_code_generator import generate_variant_code, generate_variant_description
from .sap_service_layer import get_price_by_item_code
import logging

logger = logging.getLogger(__name__)

@transaction.atomic
def create_variant_with_selections(product_id, selections, project_name, user=None):
    """
    Kullanıcının seçimlerine göre yeni bir varyant oluşturur.
    Fiyat, her zaman price_delta'lardan hesaplanır. SAP sorgusu, 
    daha sonra manuel olarak başka bir fonksiyonla tetiklenir.
    """
    try:
        product = Product.objects.get(id=product_id)

        # None olan seçimleri temizle
        cleaned_selections = {k: v for k, v in selections.items() if v is not None}

        # Seçimlerin geçerli olduğunu doğrula
        validated_selections = {}
        for spec_type_id, option_id in cleaned_selections.items():
            if SpecificationOption.objects.filter(product=product, spec_type_id=spec_type_id, option_id=option_id).exists():
                validated_selections[spec_type_id] = option_id
            else:
                logger.warning(f"Geçersiz seçim atlandı: product_id={product.id}, spec_type_id={spec_type_id}, option_id={option_id}")
                continue

        # Fiyat artık SADECE delta'lardan hesaplanıyor.
        total_price = calculate_variant_price(product, validated_selections)
        
        # Kodları ve açıklamayı üret
        reference_code_55 = generate_reference_code(product, validated_selections)
        variant_code = generate_variant_code(product, validated_selections)
        variant_description = generate_variant_description(product, validated_selections)
        
        # Varyantı, hesaplanan delta fiyatıyla veritabanına kaydet
        variant = Variant.objects.create(
            product=product,
            project_name=project_name,
            reference_code=reference_code_55,
            new_variant_code=variant_code,
            new_variant_description=variant_description,
            total_price=total_price,
            currency="EUR",
            is_generated=True,
            created_by=user,
            updated_by=user,
        )

        # Seçimleri varyanta bağla
        for spec_type_id, option_id in validated_selections.items():
            VariantSelection.objects.create(
                variant=variant,
                spec_type_id=spec_type_id,
                option_id=option_id,
            )

        logger.info(f"Yeni varyant oluşturuldu: {variant_code} (ID: {variant.id}) - Proje: {project_name} - Fiyat: {total_price}")
        return variant

    except Product.DoesNotExist:
        raise ValidationError("Belirtilen ID ile ürün bulunamadı")
    except Exception as e:
        logger.error(f"Varyant oluşturma hatası - Ürün ID: {product_id}, Seçimler: {selections}, Hata: {str(e)}")
        raise

def preview_variant(product_id, selections):
    """
    Varyant oluşturulmadan önce fiyat ve kodu tahmini olarak hesaplar.
    """
    try:
        product = Product.objects.get(id=product_id)

        # None olan seçimleri dışla
        cleaned_selections = {
            k: v for k, v in selections.items() if v is not None
        }

        validated_selections = {}
        for spec_type_id, option_id in cleaned_selections.items():
            try:
                spec_type = SpecificationType.objects.get(id=spec_type_id)
                option = SpecOption.objects.get(id=option_id, spec_type=spec_type)
                validated_selections[spec_type_id] = option_id
            except (SpecificationType.DoesNotExist, SpecOption.DoesNotExist):
                continue

        # DÜZELTME 3: Fonksiyon çağrısı 2 argüman alacak şekilde güncellendi.
        reference_code_preview = generate_reference_code(product, validated_selections)

        return {
            "preview_code": generate_variant_code(product, validated_selections),
            "preview_price": calculate_variant_price(product, validated_selections),
            "reference_code_55": reference_code_preview,
            "currency": "EUR",
            "is_valid": len(validated_selections) == len(cleaned_selections)
        }
    except Product.DoesNotExist:
        return {"error": "Belirtilen ID ile ürün bulunamadı", "is_valid": False}


@transaction.atomic
def batch_create_variants(product_id, combinations_list, user=None):
    """
    Seçim kombinasyonlarına göre toplu varyant oluşturur.
    
    Args:
        product_id (int): Ürün ID'si.
        combinations_list (list): Her biri {spec_type_id: option_id} formatında seçimler.
        user (User, optional): İşlemi yapan kullanıcı.
    
    Returns:
        dict: {
            "created_variants": [...],
            "errors": [...]
        }
    """
    created_variants = []
    errors = []
    
    for index, selections in enumerate(combinations_list):
        try:
            variant = create_variant_with_selections(product_id, selections, user)
            created_variants.append(variant)
        except Exception as e:
            errors.append({
                "index": index,
                "selections": selections,
                "error": str(e)
            })
            logger.error(
                f"Toplu varyant oluşturma hatası - Kombinasyon {index}: {selections}, Hata: {str(e)}"
            )
    
    if errors:
        logger.warning(
            f"Toplu varyant oluşturmada {len(errors)} hata oluştu, {len(created_variants)} başarılı"
        )
    
    return {
        "created_variants": created_variants,
        "errors": errors
    }



# DÜZELTME 1: Fonksiyon tanımı 2 argüman alacak şekilde güncellendi ve mantığı düzeltildi.
def generate_reference_code(product, selections):
    """
    Seçimlerden sıralı bir referans kodu oluşturur. Kodun başına ürünün kendi referans kodunu ekler.
    """
    if not product.reference_product_code:
        return None

    code_parts = [product.reference_product_code]
    
    option_ids = [v for v in selections.values() if v]
    if not option_ids:
        return product.reference_product_code

    selected_options = SpecOption.objects.filter(id__in=option_ids) \
                                          .select_related('spec_type') \
                                          .order_by('spec_type__variant_order')
    
    option_parts = [opt.reference_code for opt in selected_options if opt.reference_code]
    code_parts.extend(option_parts)
    
    return ".".join(filter(None, code_parts))
    

def update_variant_price_from_sap(variant_id):
    """
    Bir varyantın fiyatını SAP Service Layer'dan canlı olarak sorgular ve günceller.
    """
    try:
        variant = Variant.objects.get(id=variant_id)
        if not variant.reference_code:
            return False, "Bu varyant için bir referans kodu (55'li) bulunmuyor."

        # Yeni SAP servisimizden fiyatı sorgula
        sap_price = get_price_by_item_code(variant.reference_code)

        if sap_price is None:
            return False, f"'{variant.reference_code}' için SAP'de fiyat bulunamadı veya Service Layer'a bağlanılamadı."
        
        # Fiyatı al ve güncelle
        variant.total_price = sap_price
        variant.save(update_fields=['total_price', 'updated_at'])

        return True, f"Fiyat başarıyla {sap_price} {variant.currency} olarak güncellendi."

    except Variant.DoesNotExist:
        return False, "Varyant bulunamadı."
    except Exception as e:
        return False, f"Bilinmeyen bir hata oluştu: {str(e)}"