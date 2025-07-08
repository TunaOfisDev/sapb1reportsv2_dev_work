# File: backend/procure_compare/services/transformer.py

import json
import re
import logging

logger = logging.getLogger("procure_compare")  # 🔥 merkezi sistem

def parse_teklif_fiyatlari(teklif_json_str):
    try:
        teklif_json = json.loads(teklif_json_str)
        parsed_list = []
        for firma, fiyat_str in teklif_json.items():
            match = re.match(r"([\d.,]+)\s+(\w{3})\s+\(Kur:\s*([\d.,]+)\)", fiyat_str)
            if match:
                fiyat = float(match[1].replace(",", "."))
                doviz = match[2]
                kur = float(match[3].replace(",", "."))
                local_price = fiyat * kur
                parsed_list.append({
                    "firma": firma,
                    "fiyat": fiyat,
                    "kur": kur,
                    "doviz": doviz,
                    "local_price": round(local_price, 6)
                })
        return parsed_list
    except Exception as e:
        logger.error(f"Teklif fiyatları parse edilemedi: {e}")  # 🔻 WARNING yerine ERROR
        return []


def transform_procure_compare_data(raw_data):
    transformed = []

    if not isinstance(raw_data, list):
        logger.error("Beklenen veri tipi liste değil!")  # ⚠️ sadece ERROR
        return []

    for item in raw_data:
        try:
            teklif_fiyatlari_json = item.get("TeklifFiyatlariJSON", "{}")
            teklif_fiyatlari_list = parse_teklif_fiyatlari(teklif_fiyatlari_json)

            transformed_item = {
                "uniq_detail_no": item.get("UniqDetailNo"),
                "belge_no": item.get("BelgeNo"),
                "tedarikci_kod": item.get("TedarikciKod"),
                "tedarikci_ad": item.get("TedarikciAd"),
                "belge_tarih": item.get("BelgeTarih"),
                "teslim_tarih": item.get("TeslimTarih"),
                "belge_status": item.get("BelgeStatus"),
                "belge_aciklamasi": item.get("BelgeAciklamasi"),
                "sevk_adres": item.get("SevkAdres"),
                "kalem_grup": item.get("KalemGrup"),
                "satir_status": item.get("SatirStatus"),
                "satir_no": item.get("SatirNo"),
                "kalem_kod": item.get("KalemKod"),
                "kalem_tanimi": item.get("KalemTanimi"),
                "birim": item.get("Birim"),
                "sip_miktar": item.get("SipMiktar"),
                "detay_kur": item.get("DetayKur"),
                "detay_doviz": item.get("DetayDoviz"),
                "net_fiyat_dpb": item.get("NetFiyatDPB"),
                "net_tutar_ypb": item.get("NetTutarYPB"),
                "referans_teklifler": item.get("ReferansTeklifler"),
                "teklif_fiyatlari_json": teklif_fiyatlari_json,
                "teklif_fiyatlari_list": teklif_fiyatlari_list
            }

            # Bu log da kaldırıldı veya düşürüldü
            # logger.warning(...) ❌
            if not teklif_fiyatlari_list:
                # Sessizce geç, loglama yok
                pass

            transformed.append(transformed_item)

        except Exception as e:
            logger.exception(f"Veri dönüştürme hatası! Belge No: {item.get('BelgeNo')}, Hata: {e}")

    return transformed
