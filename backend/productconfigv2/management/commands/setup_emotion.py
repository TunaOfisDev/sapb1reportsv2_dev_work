# backend/productconfigv2/management/commands/setup_emotion.py
from django.core.management.base import BaseCommand
from productconfigv2.models import (
    ProductFamily, Product, SpecificationType,
    SpecOption, ProductSpecification, SpecificationOption
)
from collections import defaultdict

# Excel verilerini temsil eden veri seti.
# Her satır: (sıra no, özellik, özellik seçeneği, variant_code, variant_description)
EMOTION_DATA = [
   

(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI KAPLAMA", "K0", "MASA TABLASI KAPLAMA"),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI ALPI 10.51 KAPLAMA", "K1", "MASA TABLA ALPI10.51"),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI ALPI 12.12 KAPLAMA", "K2", "MASA TABLA ALPI12.12"),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI ALPI 12.96 KAPLAMA", "K3", "MASA TABLA ALPI12.96"),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI ALPI 10.43 KAPLAMA", "K4", "MASA TABLA ALPI10.43"),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI ALPI 12.94 KAPLAMA", "K5", "MASA TABLA ALPI12.94"),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI BRONCE MESE KAPLAMA", "K6", "MASA TABLA BRONCE MESE"),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI LAMINAT", "L0", "MASA TABLA LAM"),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI BEYAZ LAMINAT", "L1", "MASA TABLA BEYAZ LAM"),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI BEJ LAMINAT", "L2", "MASA TABLA BEJ LAM"),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI KUMBEJI LAMINAT", "L3", "MASA TABLA KUMBEJI LAM"),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI VIZON LAMINAT", "L4", "MASA TABLA VIZON LAM"),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI ANTRASIT LAMINAT", "L5", "MASA TABLA ANTRASIT LAM"),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI YENI CEVIZ LAMINAT", "L6", "MASA TABLA Y.CEVIZ LAM"),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI AND.CEVIZ LAMINAT", "L7", "MASA TABLA AND.CEVIZ LAM"),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI SAFIR MESE LAMINAT", "L8", "MASA TABLA S.MESE LAM"),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI MYL", "M0", "MASA TABLA MYL"),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI BEYAZ MYL", "M1", "MASA TABLA BEYAZ MYL"),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI BEJ MYL", "M2", "MASA TABLA BEJ MYL"),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI KUMBEJI MYL", "M3", "MASA TABLA KUMBEJI MYL"),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI VIZON MYL", "M4", "MASA TABLA VIZON MYL"),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI ANTRASIT MYL", "M5", "MASA TABLA ANTRASIT MYL"),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI YENI CEVIZ MYL", "M6", "MASA TABLA Y.CEVIZ MYL"),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI AND.CEVIZ MYL", "M7", "MASA TABLA AND.CEVIZ MYL"),
(20, "MASA TABLASI MALZEME VE RENK", "MASA TABLASI SAFIR MESE MYL", "M8", "MASA TABLA S.MESE MYL"),
(30, "MASA FLAP MALZEME VE RENK", "MASA FLAP ALUMINYUM", "ALU", "FLAP ALUMINYUM"),
(30, "MASA FLAP MALZEME VE RENK", "MASA FLAP KAPLAMA", "K0", "FLAP"),
(30, "MASA FLAP MALZEME VE RENK", "MASA FLAP ALPI 10.51 KAPLAMA", "K1", "FLAP ALPI10.51"),
(30, "MASA FLAP MALZEME VE RENK", "MASA FLAP ALPI 12.12 KAPLAMA", "K2", "FLAP ALPI12.12"),
(30, "MASA FLAP MALZEME VE RENK", "MASA FLAP ALPI 12.96 KAPLAMA", "K3", "FLAP ALPI12.96"),
(30, "MASA FLAP MALZEME VE RENK", "MASA FLAP ALPI 10.43 KAPLAMA", "K4", "FLAP ALPI10.43"),
(30, "MASA FLAP MALZEME VE RENK", "MASA FLAP ALPI 12.94 KAPLAMA", "K5", "FLAP ALPI12.94"),
(30, "MASA FLAP MALZEME VE RENK", "MASA FLAP BRONCE MESE KAPLAMA", "K6", "FLAP BRONCE MESE"),
(30, "MASA FLAP MALZEME VE RENK", "MASA FLAP LAMINAT", "L0", "FLAP LAM"),
(30, "MASA FLAP MALZEME VE RENK", "MASA FLAP BEYAZ LAMINAT", "L1", "FLAP BEYAZ LAM"),
(30, "MASA FLAP MALZEME VE RENK", "MASA FLAP BEJ LAMINAT", "L2", "FLAP BEJ LAM"),
(30, "MASA FLAP MALZEME VE RENK", "MASA FLAP KUMBEJI LAMINAT", "L3", "FLAP KUMBEJI LAM"),
(30, "MASA FLAP MALZEME VE RENK", "MASA FLAP VIZON LAMINAT", "L4", "FLAP VIZON LAM"),
(30, "MASA FLAP MALZEME VE RENK", "MASA FLAP ANTRASIT LAMINAT", "L5", "FLAP ANTRASIT LAM"),
(30, "MASA FLAP MALZEME VE RENK", "MASA FLAP YENI CEVIZ LAMINAT", "L6", "FLAP Y.CEVIZ LAM"),
(30, "MASA FLAP MALZEME VE RENK", "MASA FLAP AND.CEVIZ LAMINAT", "L7", "FLAP AND.CEVIZ LAM"),
(30, "MASA FLAP MALZEME VE RENK", "MASA FLAP SAFIR MESE LAMINAT", "L8", "FLAP S.MESE LAM"),
(30, "MASA FLAP MALZEME VE RENK", "MASA FLAP MYL", "M0", "FLAP MYL"),
(30, "MASA FLAP MALZEME VE RENK", "MASA FLAP BEYAZ MYL", "M1", "FLAP BEYAZ MYL"),
(30, "MASA FLAP MALZEME VE RENK", "MASA FLAP BEJ MYL", "M2", "FLAP BEJ MYL"),
(30, "MASA FLAP MALZEME VE RENK", "MASA FLAP KUMBEJI MYL", "M3", "FLAP KUMBEJI MYL"),
(30, "MASA FLAP MALZEME VE RENK", "MASA FLAP VIZON MYL", "M4", "FLAP VIZON MYL"),
(30, "MASA FLAP MALZEME VE RENK", "MASA FLAP ANTRASIT MYL", "M5", "FLAP ANTRASIT MYL"),
(30, "MASA FLAP MALZEME VE RENK", "MASA FLAP YENI CEVIZ MYL", "M6", "FLAP Y.CEVIZ MYL"),
(30, "MASA FLAP MALZEME VE RENK", "MASA FLAP AND.CEVIZ MYL", "M7", "FLAP AND.CEVIZ MYL"),
(30, "MASA FLAP MALZEME VE RENK", "MASA FLAP SAFIR MESE MYL", "M8", "FLAP S.MESE MYL"),
(40, "MASA AYAK MALZEME VE RENK", "MASA AYAK E.S BOYALI", "E0", "AYAK E.S BOYA"),
(40, "MASA AYAK MALZEME VE RENK", "MASA AYAK RAL1013 E.S BOYALI", "E1", "AYAK T1013E.S"),
(40, "MASA AYAK MALZEME VE RENK", "MASA AYAK RAL1019 E.S BOYALI", "E2", "AYAK T1019E.S"),
(40, "MASA AYAK MALZEME VE RENK", "MASA AYAK RAL7016 E.S BOYALI", "E3", "AYAK T7016E.S"),
(40, "MASA AYAK MALZEME VE RENK", "MASA AYAK RAL7022 E.S BOYALI", "E4", "AYAK T7022E.S"),
(40, "MASA AYAK MALZEME VE RENK", "MASA AYAK RAL9005 E.S BOYALI", "E5", "AYAK T9005E.S"),
(40, "MASA AYAK MALZEME VE RENK", "MASA AYAK RAL9007 E.S BOYALI", "E6", "AYAK T9007E.S"),
(40, "MASA AYAK MALZEME VE RENK", "MASA AYAK RAL9016 E.S BOYALI", "E7", "AYAK T9016E.S"),
(50, "MODESTY PANEL MALZEME VE RENK", "MODESTY PANEL KAPLAMA", "K0", "M.PANEL"),
(50, "MODESTY PANEL MALZEME VE RENK", "MODESTY PANEL ALPI 10.51 KAPLAMA", "K1", "M.PANEL ALPI10.51"),
(50, "MODESTY PANEL MALZEME VE RENK", "MODESTY PANEL ALPI 12.12 KAPLAMA", "K2", "M.PANEL ALPI12.12"),
(50, "MODESTY PANEL MALZEME VE RENK", "MODESTY PANEL ALPI 12.96 KAPLAMA", "K3", "M.PANEL ALPI12.96"),
(50, "MODESTY PANEL MALZEME VE RENK", "MODESTY PANEL ALPI 10.43 KAPLAMA", "K4", "M.PANEL ALPI10.43"),
(50, "MODESTY PANEL MALZEME VE RENK", "MODESTY PANEL ALPI 12.94 KAPLAMA", "K5", "M.PANEL ALPI12.94"),
(50, "MODESTY PANEL MALZEME VE RENK", "MODESTY PANEL BRONCE MESE KAPLAMA", "K6", "M.PANEL BRONCE MESE"),
(50, "MODESTY PANEL MALZEME VE RENK", "MODESTY PANEL LAMINAT", "L0", "M.PANEL LAM"),
(50, "MODESTY PANEL MALZEME VE RENK", "MODESTY PANEL BEYAZ LAMINAT", "L1", "M.PANEL BEYAZ LAM"),
(50, "MODESTY PANEL MALZEME VE RENK", "MODESTY PANEL BEJ LAMINAT", "L2", "M.PANEL BEJ LAM"),
(50, "MODESTY PANEL MALZEME VE RENK", "MODESTY PANEL KUMBEJI LAMINAT", "L3", "M.PANEL KUMBEJI LAM"),
(50, "MODESTY PANEL MALZEME VE RENK", "MODESTY PANEL VIZON LAMINAT", "L4", "M.PANEL VIZON LAM"),
(50, "MODESTY PANEL MALZEME VE RENK", "MODESTY PANEL ANTRASIT LAMINAT", "L5", "M.PANEL ANTRASIT LAM"),
(50, "MODESTY PANEL MALZEME VE RENK", "MODESTY PANEL YENI CEVIZ LAMINAT", "L6", "M.PANEL Y.CEVIZ LAM"),
(50, "MODESTY PANEL MALZEME VE RENK", "MODESTY PANEL AND.CEVIZ LAMINAT", "L7", "M.PANEL AND.CEVIZ LAM"),
(50, "MODESTY PANEL MALZEME VE RENK", "MODESTY PANEL SAFIR MESE LAMINAT", "L8", "M.PANEL S.MESE LAM"),
(50, "MODESTY PANEL MALZEME VE RENK", "MODESTY PANEL MYL", "M0", "M.PANEL MYL"),
(50, "MODESTY PANEL MALZEME VE RENK", "MODESTY PANEL BEYAZ MYL", "M1", "M.PANEL BEYAZ MYL"),
(50, "MODESTY PANEL MALZEME VE RENK", "MODESTY PANEL BEJ MYL", "M2", "M.PANEL BEJ MYL"),
(50, "MODESTY PANEL MALZEME VE RENK", "MODESTY PANEL KUMBEJI MYL", "M3", "M.PANEL KUMBEJI MYL"),
(50, "MODESTY PANEL MALZEME VE RENK", "MODESTY PANEL VIZON MYL", "M4", "M.PANEL VIZON MYL"),
(50, "MODESTY PANEL MALZEME VE RENK", "MODESTY PANEL ANTRASIT MYL", "M5", "M.PANEL ANTRASIT MYL"),
(50, "MODESTY PANEL MALZEME VE RENK", "MODESTY PANEL YENI CEVIZ MYL", "M6", "M.PANEL Y.CEVIZ MYL"),
(50, "MODESTY PANEL MALZEME VE RENK", "MODESTY PANEL AND.CEVIZ MYL", "M7", "M.PANEL AND.CEVIZ MYL"),
(50, "MODESTY PANEL MALZEME VE RENK", "MODESTY PANEL SAFIR MESE MYL", "M8", "M.PANEL S.MESE MYL"),
(110, "ÖN KUMAS PANEL KATEGÖRİSİ", "KATEGORİ 1 ÖN KUMAŞ", "KT1", "KT1"),
(110, "ÖN KUMAS PANEL KATEGÖRİSİ", "KATEGORİ 3 ÖN KUMAŞ", "KT3", "KT3"),
(120, "ÖN PANEL KUMAS RENK", "ÖN PANEL KUMAS ERACSE02", "KT1-1", "ÖN PANEL  ERACSE02 "),
(120, "ÖN PANEL KUMAS RENK", "ÖN PANEL KUMAS ERACSE33", "KT1-10", "ÖN PANEL  ERACSE33"),
(120, "ÖN PANEL KUMAS RENK", "ÖN PANEL KUMAS ERACSE34", "KT1-11", "ÖN PANEL  ERACSE34"),
(120, "ÖN PANEL KUMAS RENK", "ÖN PANEL KUMAS ERACSE39", "KT1-12", "ÖN PANEL  ERACSE39"),
(120, "ÖN PANEL KUMAS RENK", "ÖN PANEL KUMAS ERACSE40", "KT1-13", "ÖN PANEL  ERACSE40"),
(120, "ÖN PANEL KUMAS RENK", "ÖN PANEL KUMAS ERACSE42", "KT1-14", "ÖN PANEL  ERACSE42"),
(120, "ÖN PANEL KUMAS RENK", "ÖN PANEL KUMAS ERACSE44", "KT1-15", "ÖN PANEL  ERACSE44"),
(120, "ÖN PANEL KUMAS RENK", "ÖN PANEL KUMAS ERACSE03", "KT1-2", "ÖN PANEL  ERACSE03"),
(120, "ÖN PANEL KUMAS RENK", "ÖN PANEL KUMAS ERACSE07", "KT1-3", "ÖN PANEL  ERACSE07"),
(120, "ÖN PANEL KUMAS RENK", "ÖN PANEL KUMAS ERACSE13", "KT1-4", "ÖN PANEL  ERACSE13"),
(120, "ÖN PANEL KUMAS RENK", "ÖN PANEL KUMAS ERACSE14", "KT1-5", "ÖN PANEL  ERACSE14"),
(120, "ÖN PANEL KUMAS RENK", "ÖN PANEL KUMAS ERACSE23", "KT1-6", "ÖN PANEL  ERACSE23"),
(120, "ÖN PANEL KUMAS RENK", "ÖN PANEL KUMAS ERACSE27", "KT1-7", "ÖN PANEL  ERACSE27"),
(120, "ÖN PANEL KUMAS RENK", "ÖN PANEL KUMAS ERACSE28", "KT1-8", "ÖN PANEL  ERACSE28"),
(120, "ÖN PANEL KUMAS RENK", "ÖN PANEL KUMAS ERACSE29", "KT1-9", "ÖN PANEL  ERACSE29"),
(120, "ÖN PANEL KUMAS RENK", "ÖN PANEL KUMAS LDS16", "KT3-1", "ÖN PANEL  LDS16"),
(120, "ÖN PANEL KUMAS RENK", "ÖN PANEL KUMAS LDS62", "KT3-10", "ÖN PANEL  LDS62"),
(120, "ÖN PANEL KUMAS RENK", "ÖN PANEL KUMAS LDS73", "KT3-11", "ÖN PANEL  LDS73"),
(120, "ÖN PANEL KUMAS RENK", "ÖN PANEL KUMAS LDS74", "KT3-12", "ÖN PANEL  LDS74"),
(120, "ÖN PANEL KUMAS RENK", "ÖN PANEL KUMAS LDS76", "KT3-13", "ÖN PANEL  LDS76"),
(120, "ÖN PANEL KUMAS RENK", "ÖN PANEL KUMAS LDS84", "KT3-14", "ÖN PANEL  LDS84"),
(120, "ÖN PANEL KUMAS RENK", "ÖN PANEL KUMAS LDS86", "KT3-15", "ÖN PANEL  LDS86"),
(120, "ÖN PANEL KUMAS RENK", "ÖN PANEL KUMAS LDS17", "KT3-2", "ÖN PANEL  LDS17"),
(120, "ÖN PANEL KUMAS RENK", "ÖN PANEL KUMAS LDS33", "KT3-3", "ÖN PANEL  LDS33"),
(120, "ÖN PANEL KUMAS RENK", "ÖN PANEL KUMAS LDS45", "KT3-4", "ÖN PANEL  LDS45"),
(120, "ÖN PANEL KUMAS RENK", "ÖN PANEL KUMAS LDS46", "KT3-5", "ÖN PANEL  LDS46"),
(120, "ÖN PANEL KUMAS RENK", "ÖN PANEL KUMAS LDS47", "KT3-6", "ÖN PANEL  LDS47"),
(120, "ÖN PANEL KUMAS RENK", "ÖN PANEL KUMAS LDS48", "KT3-7", "ÖN PANEL  LDS48"),
(120, "ÖN PANEL KUMAS RENK", "ÖN PANEL KUMAS LDS55", "KT3-8", "ÖN PANEL  LDS55"),
(120, "ÖN PANEL KUMAS RENK", "ÖN PANEL KUMAS LDS56", "KT3-9", "ÖN PANEL  LDS56"),
(130, "MASA ÖLÇÜSÜ", "L100 D60 H75 CM", "10060", "L100 D60 H75 CM"),
(130, "MASA ÖLÇÜSÜ", "L100 D80 H75 CM", "10080", "L100 D80 H75 CM"),
(130, "MASA ÖLÇÜSÜ", "L120 D60 H75 CM", "12060", "L120 D60 H75 CM"),
(130, "MASA ÖLÇÜSÜ", "L120 D80 H75 CM", "12080", "L120 D80 H75 CM"),
(130, "MASA ÖLÇÜSÜ", "L140 D60 H75 CM", "14060", "L140 D60 H75 CM"),
(130, "MASA ÖLÇÜSÜ", "L140 D80 H75 CM", "14080", "L140 D80 H75 CM"),
(130, "MASA ÖLÇÜSÜ", "L160 D60 H75 CM", "16060", "L160 D60 H75 CM"),
(130, "MASA ÖLÇÜSÜ", "L160 D80 H75 CM", "16080", "L160 D80 H75 CM"),
(130, "MASA ÖLÇÜSÜ", "L160 D90 H75 CM", "16090", "L160 D90 H75 CM"),
(130, "MASA ÖLÇÜSÜ", "L180 D60 H75 CM", "18060", "L180 D60 H75 CM"),
(130, "MASA ÖLÇÜSÜ", "L180 D80 H75 CM", "18080", "L180 D80 H75 CM"),
(130, "MASA ÖLÇÜSÜ", "L180 D90 H75 CM", "18090", "L180 D90 H75 CM"),
(130, "MASA ÖLÇÜSÜ", "L200 D80 H75 CM", "20080", "L200 D80 H75 CM"),
(130, "MASA ÖLÇÜSÜ", "L200 D90 H75 CM", "20090", "L200 D90 H75 CM"),
(130, "MASA ÖLÇÜSÜ", "L220 D90 H75 CM", "22090", "L220 D90 H75 CM"),
(130, "MASA ÖLÇÜSÜ", "L240 D90 H75 CM", "24090", "L240 D90 H75 CM"),
(130, "MASA ÖLÇÜSÜ", "L80 D60 H75 CM", "8060", "L80 D60 H75 CM"),


]

class Command(BaseCommand):
    help = "EMOTION TEKİL MASA SETUP (Yeni Model Yapısına Uyumlu)"

    def handle(self, *args, **options):
        # 1. Ürün ailesi ve ürün oluşturuluyor.
        family, _ = ProductFamily.objects.get_or_create(
            name="Operasyonel Tekil Masa"
        )

        product, created_prod = Product.objects.get_or_create(
            name="EMOTION TEKİL MASA",
            family=family,
            defaults={
                "code": "30.EM",
                "variant_code": "30.EM",
                "variant_description": "EMOTION TEKİL MASA",
                "base_price": 400,
                "currency": "EUR",
                "variant_order": 2,
            }
        )
        if created_prod:
            self.stdout.write(self.style.SUCCESS(f"Yeni ürün oluşturuldu: {product.name}"))
        else:
            self.stdout.write(f"Ürün zaten var: {product.name}")

        # 2. Verileri gruplayarak SpecificationType, SpecOption, SpecificationOption ve ProductSpecification oluşturuluyor.
        specs_dict = defaultdict(lambda: defaultdict(list))

        for row in EMOTION_DATA:
            sira_no, spec_name, option_name, variant_code, variant_description = row
            specs_dict[sira_no][spec_name].append({
                "option_name": option_name,
                "variant_code": variant_code,
                "variant_description": variant_description
            })

        for sira_no in sorted(specs_dict.keys()):
            for spec_name, option_list in specs_dict[sira_no].items():
                spec_type, created = SpecificationType.objects.get_or_create(
                    name=spec_name,
                    defaults={
                        "group": "EMOTION",
                        "is_required": True,
                        "allow_multiple": False,
                        "variant_order": sira_no,
                        "display_order": sira_no,
                        "multiplier": 1.00
                    }
                )
                if created:
                    self.stdout.write(f"[SpecType] Yeni oluşturuldu: {spec_name}")
                else:
                    self.stdout.write(f"[SpecType] Zaten vardı: {spec_name}")

                ProductSpecification.objects.get_or_create(
                    product=product,
                    spec_type=spec_type,
                    defaults={
                        "is_required": True,
                        "allow_multiple": False,
                        "variant_order": sira_no,
                        "display_order": sira_no
                    }
                )

                for idx, item in enumerate(option_list, start=1):
                    opt_name = item["option_name"]
                    var_code = item["variant_code"]
                    var_desc = item["variant_description"]

                    spec_option, created_opt = SpecOption.objects.get_or_create(
                        spec_type=spec_type,
                        name=opt_name,
                        defaults={
                            "variant_code": var_code,
                            "variant_description": var_desc,
                            "image": None,
                            "price_delta": 0.00,
                            "is_default": False,
                            "display_order": idx
                        }
                    )
                    if created_opt:
                        self.stdout.write(f"  → [SpecOption] {opt_name} eklendi.")
                    else:
                        self.stdout.write(f"  → [SpecOption] {opt_name} zaten vardı.")

                    SpecificationOption.objects.get_or_create(
                        product=product,
                        spec_type=spec_type,
                        option=spec_option,
                        defaults={
                            "is_default": False,
                            "display_order": idx
                        }
                    )

                self.stdout.write(self.style.SUCCESS(f"→ {spec_name} eklendi ve eşleşmeler tamamlandı"))

        self.stdout.write(self.style.SUCCESS("Tüm özellikler, seçenekler ve eşlemeler oluşturuldu."))