# backend/logocustomercollection/tasks.py
from decimal import Decimal
from collections import defaultdict
from datetime import datetime

from celery import shared_task
from django.db import transaction

from .utilities.data_fetcher import fetch_logo_db_data
from .models.models import LogoCustomerCollectionTransaction
from .models.closinginvoice import LogoCustomerCollectionAgingSummary


# ──────────────────────────────────────────────────────────────────────────────
# 1) H A M   V E R İ Y İ   K A Y D E T
# ──────────────────────────────────────────────────────────────────────────────
@shared_task(name="logocustomercollection.save_raw_transactions")
def save_raw_transactions(token: str) -> str:
    raw_data = fetch_logo_db_data(token)
    if not raw_data:
        return "Ham veri alınamadı."

    with transaction.atomic():
        for item in raw_data:
            borc   = Decimal(str(item["Borç"]).replace(",", ""))
            alacak = Decimal(str(item["Alacak"]).replace(",", ""))
            LogoCustomerCollectionTransaction.objects.update_or_create(
                cari_kod=item["Cari Kod"],
                ay=item["Ay"],
                yil=item["Yıl"],
                defaults={
                    "cari_ad": item["Cari Ad"],
                    "borc":    borc,
                    "alacak":  alacak,
                },
            )
    return f"{len(raw_data)} kayıt başarıyla güncellendi."


# ──────────────────────────────────────────────────────────────────────────────
# 2) Y A Ş L A N D I R M A  Ö Z E T İ N İ   O L U Ş T U R
# ──────────────────────────────────────────────────────────────────────────────
@shared_task(name="logocustomercollection.generate_aging_summaries")
def generate_aging_summaries() -> str:
    """
    FIFO mantığıyla:
      • Tüm alacaklar en eski borçlardan düşülür
      • Kalan borçlar “Öncesi” + son 4 takvim ayına dağıtılır
    """
    qs = (
        LogoCustomerCollectionTransaction
        .objects
        .all()
        .order_by("cari_kod", "yil", "ay")
    )

    ay_ad = {1:"Oca",2:"Şub",3:"Mar",4:"Nis",5:"May",6:"Haz",7:"Tem",8:"Ağu",9:"Eyl",10:"Eki",11:"Kas",12:"Ara"}
    today       = datetime.now()
    this_y, tm  = today.year, today.month

    # Cari bazında grupla
    grouped: dict[tuple[str,str], list[LogoCustomerCollectionTransaction]] = defaultdict(list)
    for row in qs:
        grouped[(row.cari_kod, row.cari_ad)].append(row)

    with transaction.atomic():
        for (c_kod, c_ad), trxs in grouped.items():

            # 1️⃣  Ay bazlı toplam B O R Ç  + global toplam A L A C A K
            borc_by_month: dict[tuple[int,int], Decimal] = defaultdict(Decimal)
            alacak_total  = Decimal("0.00")
            for t in trxs:
                borc_by_month[(t.yil, t.ay)] += t.borc
                alacak_total                 += t.alacak

            # 2️⃣  FIFO: alacaklar en eski borçlara mahsup edilir
            for key in sorted(borc_by_month.keys()):
                if alacak_total <= 0:
                    break
                if alacak_total >= borc_by_month[key]:
                    alacak_total       -= borc_by_month[key]
                    borc_by_month[key]  = Decimal("0.00")
                else:
                    borc_by_month[key] -= alacak_total
                    alacak_total        = Decimal("0.00")
                    break  # alacak bitti

            # 3️⃣  Son 4 takvim ayını çıkar
            son4 = []
            for i in range(3, -1, -1):
                ay  = tm - i
                yil = this_y
                if ay <= 0:
                    ay += 12
                    yil -= 1
                son4.append(((yil, ay), f"{ay_ad[ay]}{str(yil)[-2:]}"))
            son4_dict = dict(son4)

            # 4️⃣  JSON payload oluştur
            oncesi = Decimal("0.00")
            aylik_json = [["Öncesi", 0.0]]
            for (yil, ay), label in son4:
                val = borc_by_month.get((yil, ay), Decimal("0.00"))
                aylik_json.append([label, float(round(val, 2))])

            # “Öncesi”
            for key, val in borc_by_month.items():
                if key not in son4_dict:
                    oncesi += val
            aylik_json[0][1] = float(round(oncesi, 2))

            # 5️⃣  Güncel bakiye
            guncel_bakiye = sum(borc_by_month.values())
            if guncel_bakiye < 0:
                guncel_bakiye = Decimal("0.00")  # alacak fazlası varsa sıfırla

            # 6️⃣  Kaydet / güncelle
            LogoCustomerCollectionAgingSummary.objects.update_or_create(
                cari_kod=c_kod,
                defaults={
                    "cari_ad":          c_ad,
                    "guncel_bakiye":    guncel_bakiye,
                    "aylik_kalan_borc": aylik_json,
                },
            )

    return "Müşteri borç yaşlandırma özetleri FIFO mantığıyla güncellendi."
