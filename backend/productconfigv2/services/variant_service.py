from django.db import transaction
from django.core.exceptions import ValidationError
from ..models import (
    Variant, VariantSelection, Product,
    SpecificationType, SpecOption,
    ProductSpecification, SpecificationOption
)
from ..utils.price_calculator import calculate_variant_price
from ..utils.variant_code_generator import generate_variant_code, generate_variant_description
import logging

logger = logging.getLogger(__name__)

@transaction.atomic
def create_variant_with_selections(product_id, selections, user=None):
    """
    Kullanıcının seçimlerine göre yeni bir varyant oluşturur.
    """
    try:
        product = Product.objects.get(id=product_id)

        # None olan seçimleri temizle
        cleaned_selections = {
            k: v for k, v in selections.items() if v is not None
        }

        validated_selections = {}
        for spec_type_id, option_id in cleaned_selections.items():
            try:
                spec_type = SpecificationType.objects.get(id=spec_type_id)
                option = SpecOption.objects.get(id=option_id, spec_type=spec_type)

                if not ProductSpecification.objects.filter(product=product, spec_type=spec_type).exists():
                    raise ValidationError(f"{spec_type.name} özelliği bu ürüne ait değil")

                if not SpecificationOption.objects.filter(product=product, spec_type=spec_type, option=option).exists():
                    raise ValidationError(f"{option.name} seçeneği {spec_type.name} için geçerli değil")

                validated_selections[spec_type_id] = option_id

            except SpecificationType.DoesNotExist:
                raise ValidationError(f"{spec_type_id} ID'li özellik tipi bulunamadı")
            except SpecOption.DoesNotExist:
                raise ValidationError(f"{option_id} ID'li seçenek bulunamadı veya {spec_type_id} özellik tipine ait değil")

        # Varyant bilgileri
        variant_code = generate_variant_code(product, validated_selections)
        variant_description = generate_variant_description(product, validated_selections)
        total_price = calculate_variant_price(product, validated_selections)

        variant = Variant.objects.create(
            product=product,
            new_variant_code=variant_code,
            new_variant_description=variant_description,
            total_price=total_price,
            currency="EUR",
            is_generated=True,
            created_by=user,
            updated_by=user,
        )

        for spec_type_id, option_id in validated_selections.items():
            VariantSelection.objects.create(
                variant=variant,
                spec_type_id=spec_type_id,
                option_id=option_id,
                created_by=user,
                updated_by=user,
            )

        logger.info(
            f"Yeni varyant oluşturuldu: {variant_code} (ID: {variant.id}) - Ürün: {product.code} (ID: {product.id})"
        )

        return variant

    except Product.DoesNotExist:
        raise ValidationError("Belirtilen ID ile ürün bulunamadı")
    except Exception as e:
        logger.error(
            f"Varyant oluşturma hatası - Ürün ID: {product_id}, Seçimler: {selections}, Hata: {str(e)}"
        )
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

        return {
            "preview_code": generate_variant_code(product, validated_selections),
            "preview_price": calculate_variant_price(product, validated_selections),
            "currency": "EUR",
            "is_valid": len(validated_selections) == len(cleaned_selections)
        }

    except Product.DoesNotExist:
        return {
            "error": "Belirtilen ID ile ürün bulunamadı",
            "is_valid": False
        }


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
