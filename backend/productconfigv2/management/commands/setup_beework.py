# backend/productconfigv2/management/commands/setup_beework.py
from django.core.management.base import BaseCommand
from productconfigv2.models import (
    ProductFamily, Product, SpecificationType,
    SpecOption, ProductSpecification, SpecificationOption
)
from collections import defaultdict
from decimal import Decimal, InvalidOperation

# Excel verilerini temsil eden veri seti.
# Her satır: (sıra no, özellik, özellik seçeneği, variant_code, variant_description)
BEEWORK_DATA = [


(10, "MASA ÖLÇÜSÜ", "L120 D70 H75 CM MYL", "12070", "L120 D70 H75 CM ", "0", "1","12070",),
(10, "MASA ÖLÇÜSÜ", "L120 D70 H75 CM LAMİNAT ", "12070", "L120 D70 H75 CM ", "0", "1","12070",),
(10, "MASA ÖLÇÜSÜ", "L120 D70 H75 CM KAPLAMA", "12070", "L120 D70 H75 CM ", "0", "1","12070",),
(10, "MASA ÖLÇÜSÜ", "L120 D80 H75 CM MYL", "12080", "L120 D80 H75 CM ", "16", "1","12080",),
(10, "MASA ÖLÇÜSÜ", "L120 D80 H75 CM LAMİNAT", "12080", "L120 D80 H75 CM ", "19", "1","12080",),
(10, "MASA ÖLÇÜSÜ", "L120 D80 H75 CM KAPLAMA", "12080", "L120 D80 H75 CM ", "-27", "1","12080",),
(10, "MASA ÖLÇÜSÜ", "L140 D70 H75 CM MYL", "14070", "L140 D70 H75 CM ", "17", "1","14070",),
(10, "MASA ÖLÇÜSÜ", "L140 D70 H75 CM LAMİNAT", "14070", "L140 D70 H75 CM ", "22", "1","14070",),
(10, "MASA ÖLÇÜSÜ", "L140 D70 H75 CM KAPLAMA", "14070", "L140 D70 H75 CM ", "34", "1","14070",),
(10, "MASA ÖLÇÜSÜ", "L140 D80 H75 CM MYL", "14080", "L140 D80 H75 CM ", "61", "1","14080",),
(10, "MASA ÖLÇÜSÜ", "L140 D80 H75 CM LAMİNAT", "14080", "L140 D80 H75 CM ", "86", "1","14080",),
(10, "MASA ÖLÇÜSÜ", "L140 D80 H75 CM KAPLAMA", "14080", "L140 D80 H75 CM ", "46", "1","14080",),
(10, "MASA ÖLÇÜSÜ", "L140 D90 H75 CM MYL", "14090", "L140 D90 H75 CM ", "57", "1","14090",),
(10, "MASA ÖLÇÜSÜ", "L140 D90 H75 CM LAMİNAT", "14090", "L140 D90 H75 CM ", "83", "1","14090",),
(10, "MASA ÖLÇÜSÜ", "L140 D90 H75 CM KAPLAMA", "14090", "L140 D90 H75 CM ", "75", "1","14090",),
(10, "MASA ÖLÇÜSÜ", "L160 D70 H75 CM MYL", "16070", "L160 D70 H75 CM ", "49", "1","16070",),
(10, "MASA ÖLÇÜSÜ", "L160 D70 H75 CM LAMİNAT", "16070", "L160 D70 H75 CM ", "81", "1","16070",),
(10, "MASA ÖLÇÜSÜ", "L160 D70 H75 CM KAPLAMA", "16070", "L160 D70 H75 CM ", "116", "1","16070",),
(10, "MASA ÖLÇÜSÜ", "L160 D80 H75 CM MYL", "16080", "L160 D80 H75 CM ", "66", "1","16080",),
(10, "MASA ÖLÇÜSÜ", "L160 D80 H75 CM LAMİNAT", "16080", "L160 D80 H75 CM ", "104", "1","16080",),
(10, "MASA ÖLÇÜSÜ", "L160 D80 H75 CM KAPLAMA", "16080", "L160 D80 H75 CM ", "116", "1","16080",),
(10, "MASA ÖLÇÜSÜ", "L160 D90 H75 CM MYL", "16090", "L160 D90 H75 CM ", "104", "1","16090",),
(10, "MASA ÖLÇÜSÜ", "L160 D90 H75 CM LAMİNAT", "16090", "L160 D90 H75 CM ", "155", "1","16090",),
(10, "MASA ÖLÇÜSÜ", "L160 D90 H75 CM KAPLAMA", "16090", "L160 D90 H75 CM ", "191", "1","16090",),
(10, "MASA ÖLÇÜSÜ", "L180 D70 H75 CM MYL", "18070", "L180 D70 H75 CM ", "73", "1","18070",),
(10, "MASA ÖLÇÜSÜ", "L180 D70 H75 CM LAMİNAT", "18070", "L180 D70 H75 CM ", "119", "1","18070",),
(10, "MASA ÖLÇÜSÜ", "L180 D70 H75 CM KAPLAMA", "18070", "L180 D70 H75 CM ", "193", "1","18070",),
(10, "MASA ÖLÇÜSÜ", "L180 D80 H75 CM MYL", "18080", "L180 D80 H75 CM ", "92", "1","18080",),
(10, "MASA ÖLÇÜSÜ", "L180 D80 H75 CM LAMİNAT", "18080", "L180 D80 H75 CM ", "144", "1","18080",),
(10, "MASA ÖLÇÜSÜ", "L180 D80 H75 CM KAPLAMA", "18080", "L180 D80 H75 CM ", "193", "1","18080",),
(10, "MASA ÖLÇÜSÜ", "L180 D90 H75 CM MYL", "18090", "L180 D90 H75 CM ", "110", "1","18090",),
(10, "MASA ÖLÇÜSÜ", "L180 D90 H75 CM LAMİNAT", "18090", "L180 D90 H75 CM ", "170", "1","18090",),
(10, "MASA ÖLÇÜSÜ", "L180 D90 H75 CM KAPLAMA", "18090", "L180 D90 H75 CM ", "230", "1","18090",),
(10, "MASA ÖLÇÜSÜ", "L200 D70 H75 CM MYL", "20070", "L200 D70 H75 CM ", "94", "1","20070",),
(10, "MASA ÖLÇÜSÜ", "L200 D70 H75 CM LAMİNAT", "20070", "L200 D70 H75 CM ", "159", "1","20070",),
(10, "MASA ÖLÇÜSÜ", "L200 D70 H75 CM KAPLAMA", "20070", "L200 D70 H75 CM ", "265", "1","20070",),
(10, "MASA ÖLÇÜSÜ", "L200 D80 H75 CM MYL", "20080", "L200 D80 H75 CM ", "114", "1","20080",),
(10, "MASA ÖLÇÜSÜ", "L200 D80 H75 CM LAMİNAT", "20080", "L200 D80 H75 CM ", "185", "1","20080",),
(10, "MASA ÖLÇÜSÜ", "L200 D80 H75 CM KAPLAMA", "20080", "L200 D80 H75 CM ", "265", "1","20080",),
(10, "MASA ÖLÇÜSÜ", "L200 D90 H75 CM MYL", "20090", "L200 D90 H75 CM ", "132", "1","20090",),
(10, "MASA ÖLÇÜSÜ", "L200 D90 H75 CM LAMİNAT", "20090", "L200 D90 H75 CM ", "209", "1","20090",),
(10, "MASA ÖLÇÜSÜ", "L200 D90 H75 CM KAPLAMA", "20090", "L200 D90 H75 CM ", "303", "1","20090",),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI KAPLAMA", "K0", "MASA TABLASI KAPLAMA", "340", "1","K0",),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI ALPI 10.51 KAPLAMA", "K1", "MASA TABLA ALPI10.51", "340", "1","K0",),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI ALPI 12.12 KAPLAMA", "K2", "MASA TABLA ALPI12.12", "340", "1","K0",),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI ALPI 12.96 KAPLAMA", "K3", "MASA TABLA ALPI12.96", "340", "1","K0",),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI ALPI 10.43 KAPLAMA", "K4", "MASA TABLA ALPI10.43", "340", "1","K0",),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI ALPI 12.94 KAPLAMA", "K5", "MASA TABLA ALPI12.94", "340", "1","K0",),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI LAMINAT", "L0", "MASA TABLA LAM", "109", "1","L0",),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI BEYAZ LAMINAT", "L1", "MASA TABLA BEYAZ LAM", "109", "1","L0",),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI BEJ LAMINAT", "L2", "MASA TABLA BEJ LAM", "109", "1","L0",),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI KUMBEJI LAMINAT", "L3", "MASA TABLA KUMBEJI LAM", "109", "1","L0",),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI VIZON LAMINAT", "L4", "MASA TABLA VIZON LAM", "109", "1","L0",),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI ANTRASIT LAMINAT", "L5", "MASA TABLA ANTRASIT LAM", "109", "1","L0",),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI AND.CEVIZ LAMINAT", "L6", "MASA TABLA AND.CEVIZ LAM", "109", "1","L0",),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI SAFIR MESE LAMINAT", "L7", "MASA TABLA S.MESE LAM", "109", "1","L0",),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI MYL", "M0", "MASA TABLA MYL", "0", "1","M0",),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI BEYAZ MYL", "M1", "MASA TABLA BEYAZ MYL", "0", "1","M0",),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI BEJ MYL", "M2", "MASA TABLA BEJ MYL", "0", "1","M0",),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI KUMBEJI MYL", "M3", "MASA TABLA KUMBEJI MYL", "0", "1","M0",),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI VIZON MYL", "M4", "MASA TABLA VIZON MYL", "0", "1","M0",),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI ANTRASIT MYL", "M5", "MASA TABLA ANTRASIT MYL", "0", "1","M0",),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI AND.CEVIZ MYL", "M6", "MASA TABLA AND.CEVIZ MYL", "0", "1","M0",),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI SAFIR MESE MYL", "M7", "MASA TABLA S.MESE MYL", "0", "1","M0",),
(30, "MASA AYAK MALZEME VE RENK", "MASA AYAK E.S BOYALI", "E0", "AYAK E.S BOYA", "0", "1","E0",),
(30, "MASA AYAK MALZEME VE RENK", "MASA AYAK RAL1013 E.S BOYALI", "E1", "AYAK T1013E.S", "0", "1","E0",),
(30, "MASA AYAK MALZEME VE RENK", "MASA AYAK RAL1019 E.S BOYALI", "E2", "AYAK T1019E.S", "0", "1","E0",),
(30, "MASA AYAK MALZEME VE RENK", "MASA AYAK RAL7016 E.S BOYALI", "E3", "AYAK T7016E.S", "0", "1","E0",),
(30, "MASA AYAK MALZEME VE RENK", "MASA AYAK RAL7022 E.S BOYALI", "E4", "AYAK T7022E.S", "0", "1","E0",),
(30, "MASA AYAK MALZEME VE RENK", "MASA AYAK RAL9005 E.S BOYALI", "E5", "AYAK T9005E.S", "0", "1","E0",),
(30, "MASA AYAK MALZEME VE RENK", "MASA AYAK RAL9007 E.S BOYALI", "E6", "AYAK T9007E.S", "0", "1","E0",),
(30, "MASA AYAK MALZEME VE RENK", "MASA AYAK RAL9016 E.S BOYALI", "E7", "AYAK T9016E.S", "0", "1","E0",),
(60, "MASA FLAP MALZEME VE RENK", "MASA FLAP ALUMINYUM", "ALU", "FLAP ALUMINYUM", "60", "1","ALU",),
(60, "MASA FLAP MALZEME VE RENK", "MASA FLAP KAPLAMA", "K0", "FLAP", "0", "1","AHS",),
(60, "MASA FLAP MALZEME VE RENK", "MASA FLAP ALPI 10.51 KAPLAMA", "K1", "FLAP ALPI10.51", "0", "1","AHS",),
(60, "MASA FLAP MALZEME VE RENK", "MASA FLAP ALPI 12.12 KAPLAMA", "K2", "FLAP ALPI12.12", "0", "1","AHS",),
(60, "MASA FLAP MALZEME VE RENK", "MASA FLAP ALPI 12.96 KAPLAMA", "K3", "FLAP ALPI12.96", "0", "1","AHS",),
(60, "MASA FLAP MALZEME VE RENK", "MASA FLAP ALPI 10.43 KAPLAMA", "K4", "FLAP ALPI10.43", "0", "1","AHS",),
(60, "MASA FLAP MALZEME VE RENK", "MASA FLAP ALPI 12.94 KAPLAMA", "K5", "FLAP ALPI12.94", "0", "1","AHS",),
(60, "MASA FLAP MALZEME VE RENK", "MASA FLAP LAMINAT", "L0", "FLAP LAM", "0", "1","AHS",),
(60, "MASA FLAP MALZEME VE RENK", "MASA FLAP BEYAZ LAMINAT", "L1", "FLAP BEYAZ LAM", "0", "1","AHS",),
(60, "MASA FLAP MALZEME VE RENK", "MASA FLAP BEJ LAMINAT", "L2", "FLAP BEJ LAM", "0", "1","AHS",),
(60, "MASA FLAP MALZEME VE RENK", "MASA FLAP KUMBEJI LAMINAT", "L3", "FLAP KUMBEJI LAM", "0", "1","AHS",),
(60, "MASA FLAP MALZEME VE RENK", "MASA FLAP VIZON LAMINAT", "L4", "FLAP VIZON LAM", "0", "1","AHS",),
(60, "MASA FLAP MALZEME VE RENK", "MASA FLAP ANTRASIT LAMINAT", "L5", "FLAP ANTRASIT LAM", "0", "1","AHS",),
(60, "MASA FLAP MALZEME VE RENK", "MASA FLAP AND.CEVIZ LAMINAT", "L6", "FLAP AND.CEVIZ LAM", "0", "1","AHS",),
(60, "MASA FLAP MALZEME VE RENK", "MASA FLAP SAFIR MESE LAMINAT", "L7", "FLAP S.MESE LAM", "0", "1","AHS",),
(60, "MASA FLAP MALZEME VE RENK", "MASA FLAP MYL", "M0", "FLAP MYL", "0", "1","AHS",),
(60, "MASA FLAP MALZEME VE RENK", "MASA FLAP BEYAZ MYL", "M1", "FLAP BEYAZ MYL", "0", "1","AHS",),
(60, "MASA FLAP MALZEME VE RENK", "MASA FLAP BEJ MYL", "M2", "FLAP BEJ MYL", "0", "1","AHS",),
(60, "MASA FLAP MALZEME VE RENK", "MASA FLAP KUMBEJI MYL", "M3", "FLAP KUMBEJI MYL", "0", "1","AHS",),
(60, "MASA FLAP MALZEME VE RENK", "MASA FLAP VIZON MYL", "M4", "FLAP VIZON MYL", "0", "1","AHS",),
(60, "MASA FLAP MALZEME VE RENK", "MASA FLAP ANTRASIT MYL", "M5", "FLAP ANTRASIT MYL", "0", "1","AHS",),
(60, "MASA FLAP MALZEME VE RENK", "MASA FLAP AND.CEVIZ MYL", "M6", "FLAP AND.CEVIZ MYL", "0", "1","AHS",),
(60, "MASA FLAP MALZEME VE RENK", "MASA FLAP SAFIR MESE MYL", "M7", "FLAP S.MESE MYL", "0", "1","AHS",),



]



class Command(BaseCommand):
    help = "BEEWORK SETUP (Ürün Bazlı Referans Kod Desteğiyle)"

    def handle(self, *args, **options):
        # 1. Ürün ailesi ve ürün oluşturuluyor.
        family, _ = ProductFamily.objects.get_or_create(name="Operasyonel Tekil Masa")
        
        # GÜNCELLEME 1: Temel referans kodu ("55.BW") doğrudan ürünün kendisine kaydediliyor.
        product, created_prod = Product.objects.update_or_create(
            name="BEEWORK TEKİL MASA",
            family=family,
            defaults={
                "code": "30.BW", 
                "reference_product_code": "55.BW", # 55'li kodun temeli artık burada
                "variant_code": "30.BW", 
                "variant_description": "BEEWORK TEKİL MASA",
                "base_price": 338.00, 
                "currency": "EUR", 
                "variant_order": 1,
            }
        )
        if created_prod:
            self.stdout.write(self.style.SUCCESS(f"Yeni ürün oluşturuldu: {product.name}"))
        else:
            self.stdout.write(f"Ürün zaten vardı ve güncellendi: {product.name}")

        # GÜNCELLEME 2: Gereksiz "MODEL" özelliğini oluşturan blok KALDIRILDI.
        # Script artık doğrudan BEEWORK_DATA'yı işlemeye başlıyor.

        # 2. Verileri gruplama ve işleme
        specs_dict = defaultdict(dict)

        for row in BEEWORK_DATA:
            # 8 elemanlı satırı okumaya devam ediyoruz
            sira_no, spec_name, option_name, variant_code, variant_description, price_str, is_required_str, reference_code_part = row
            
            spec_group_data = specs_dict[sira_no].setdefault(spec_name, {
                "options": [],
                "is_required": True 
            })
            
            spec_group_data["options"].append({
                "option_name": option_name,
                "variant_code": variant_code,
                "variant_description": variant_description,
                "price_str": price_str,
                "reference_code_part": reference_code_part
            })
            spec_group_data["is_required"] = (is_required_str == '1')


        for sira_no in sorted(specs_dict.keys()):
            for spec_name, spec_group_data in specs_dict[sira_no].items():
                
                option_list = spec_group_data["options"]
                is_required_value = spec_group_data["is_required"]

                spec_type, created = SpecificationType.objects.update_or_create(
                    name=spec_name,
                    defaults={
                        "group": "BEEWORK", "is_required": is_required_value, "allow_multiple": False,
                        "variant_order": sira_no, "display_order": sira_no, "multiplier": 1.00
                    }
                )

                ProductSpecification.objects.update_or_create(
                    product=product,
                    spec_type=spec_type,
                    defaults={
                        "is_required": is_required_value, "allow_multiple": False,
                        "variant_order": sira_no, "display_order": sira_no
                    }
                )

                for idx, item in enumerate(option_list, start=1):
                    opt_name = item["option_name"]
                    var_code = item["variant_code"]
                    var_desc = item["variant_description"]
                    price_str = item["price_str"]
                    reference_code_part = item["reference_code_part"]

                    price_value = Decimal('0.00')
                    if price_str:
                        try:
                            price_value = Decimal(price_str.replace(',', '.'))
                        except InvalidOperation:
                            self.stdout.write(self.style.ERROR(
                                f"Hatalı fiyat formatı: '{price_str}' ({opt_name}). 0.00 olarak ayarlandı."
                            ))
                    
                    spec_option, created_opt = SpecOption.objects.update_or_create(
                        spec_type=spec_type,
                        name=opt_name,
                        defaults={
                            "variant_code": var_code,
                            "variant_description": var_desc,
                            "price_delta": price_value,
                            "reference_code": reference_code_part,
                            "is_default": False,
                            "display_order": idx
                        }
                    )
                    
                    if created_opt:
                        self.stdout.write(f"  → [SpecOption] {opt_name} (Fiyat: {price_value}) eklendi.")
                    else:
                        self.stdout.write(f"  → [SpecOption] {opt_name} (Fiyat: {price_value}) güncellendi.")

                    SpecificationOption.objects.get_or_create(
                        product=product, spec_type=spec_type, option=spec_option,
                        defaults={"is_default": False, "display_order": idx}
                    )

                status_text = "ZORUNLU" if is_required_value else "OPSİYONEL"
                self.stdout.write(self.style.SUCCESS(f"→ {spec_name} ({status_text}) için tüm işlemler tamamlandı."))

        self.stdout.write(self.style.SUCCESS("BEEWORK kurulumu başarıyla tamamlandı/güncellendi."))


