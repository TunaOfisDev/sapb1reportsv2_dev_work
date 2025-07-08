# backend/logo_supplier_receivables_aging/tasks.py
from decimal import Decimal
from collections import defaultdict
from .utils.data_fetcher import fetch_logo_db_data
from .models.models import SupplierRawTransaction
from .models.closinginvoice import SupplierAgingSummary
from django.db import transaction
from datetime import datetime

def save_raw_transactions(token):
    raw_data = fetch_logo_db_data(token)
    if not raw_data:
        print("Ham veri alınamadı.")
        return

    with transaction.atomic():
        for item in raw_data:
            # Virgüllü formatı temizle
            borc = Decimal(str(item["Borç"]).replace(',', ''))
            alacak = Decimal(str(item["Alacak"]).replace(',', ''))
            SupplierRawTransaction.objects.update_or_create(
                cari_kod=item["Cari Kod"],
                ay=item["Ay"],
                yil=item["Yıl"],
                defaults={
                    "cari_ad": item["Cari Ad"],
                    "borc": borc,
                    "alacak": alacak,
                }
            )
    print(f"{len(raw_data)} kayıt başarıyla güncellendi.")



def generate_closing_invoices():
    rows = SupplierRawTransaction.objects.all().order_by("cari_kod", "yil", "ay")

    ay_adlari = {
        1: "Oca", 2: "Şub", 3: "Mar", 4: "Nis", 5: "May",
        6: "Haz", 7: "Tem", 8: "Ağu", 9: "Eyl", 10: "Eki",
        11: "Kas", 12: "Ara"
    }

    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month

    grouped = defaultdict(list)
    for row in rows:
        key = (row.cari_kod, row.cari_ad)
        grouped[key].append(row)

    with transaction.atomic():
        for (cari_kod, cari_ad), items in grouped.items():
            total_borc = sum(i.borc for i in items)
            kalan_borc = total_borc
            oncesi = Decimal("0.00")
            tum_aylar = {}
            toplam_fazla_alacak = Decimal("0.00")

            for i in items:
                alacak = i.alacak

                if kalan_borc <= 0:
                    kalan_alacak = alacak
                elif kalan_borc < alacak:
                    kalan_alacak = alacak - kalan_borc
                    kalan_borc = Decimal("0.00")
                else:
                    kalan_alacak = Decimal("0.00")
                    kalan_borc -= alacak

                kalan_alacak = round(kalan_alacak, 3)
                toplam_fazla_alacak += kalan_alacak

                ay_label = f"{ay_adlari[i.ay]}{str(i.yil)[-2:]}"
                # Öncesi: Son 4 ayın dışındaki hareketler
                if i.yil < current_year or (i.yil == current_year and i.ay < current_month - 3):
                    oncesi -= kalan_alacak
                else:
                    tum_aylar[(i.yil, i.ay)] = (ay_label, float(-kalan_alacak))

            # Son 4 ayı tanımla
            son_dort_ay = []
            for i in range(3, -1, -1):
                ay = current_month - i
                yil = current_year
                if ay <= 0:
                    ay += 12
                    yil -= 1
                ay_label = f"{ay_adlari[ay]}{str(yil)[-2:]}"
                son_dort_ay.append((yil, ay, ay_label))

            # JSON verisini oluştur
            json_data = [["Öncesi", float(round(oncesi, 3))]]
            for yil, ay, ay_label in son_dort_ay:
                value = tum_aylar.get((yil, ay), (ay_label, 0.0))[1]
                json_data.append([ay_label, value])

            # Güncel bakiye = toplam fazla alacak (tüm aylardan)
            guncel_bakiye = float(-round(toplam_fazla_alacak, 3))

            # Modelle uyumlu update_or_create
            SupplierAgingSummary.objects.update_or_create(
                cari_kod=cari_kod,
                defaults={
                    "cari_ad": cari_ad,
                    "guncel_bakiye": guncel_bakiye,
                    "aylik_kalan_alacak": json_data
                }
            )

    print("Tüm tedarikçiler için özet yaşlandırma hesaplandı.")