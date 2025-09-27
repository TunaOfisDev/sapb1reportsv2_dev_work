# File: procure_compare/api/serializers.py

from rest_framework import serializers
from procure_compare.models import (
    PurchaseOrder,
    PurchaseQuote,
    PurchaseComparison,
    PurchaseApproval
)


class PurchaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = "__all__"


class PurchaseQuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseQuote
        fields = "__all__"


class PurchaseComparisonSerializer(serializers.ModelSerializer):
    # JSON field olarak parse edilen listeyi client'a açıyoruz
    teklif_fiyatlari_list = serializers.SerializerMethodField()
    uyari_var_mi = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseComparison
        fields = "__all__"
        read_only_fields = ["teklif_fiyatlari_list", "uyari_var_mi"]
        

    def get_teklif_fiyatlari_list(self, obj):
        try:
            import json

            parsed = json.loads(obj.teklif_fiyatlari_json or "{}")
            parsed_list = []

            for firma, detay in parsed.items():
                if isinstance(detay, dict):
                    fiyat_raw = detay.get("fiyat", "")
                    vade_gun = detay.get("vade_gun", "0")
                    teslim_gun = detay.get("teslim_gun", "0")
                else:
                    # Eski sistem destekli fallback
                    fiyat_raw = detay
                    vade_gun = "0"
                    teslim_gun = "0"

                import re
                match = re.match(r"([\d.,]+)\s+(\w{3})\s+\(Kur:\s*([\d.,]+)\)", fiyat_raw)
                if not match:
                    continue
                fiyat = float(match[1].replace(",", "."))
                doviz = match[2]
                kur = float(match[3].replace(",", "."))
                local_price = fiyat * kur

                parsed_list.append({
                    "firma": firma,
                    "fiyat": fiyat,
                    "kur": kur,
                    "doviz": doviz,
                    "local_price": round(local_price, 6),
                    "vade_gun": int(vade_gun),
                    "teslim_gun": int(teslim_gun)
                })

            return sorted(parsed_list, key=lambda x: x["local_price"])

        except Exception as e:
            print(f"Teklif parse hatası: {str(e)}")
            return []

        


    def get_uyari_var_mi(self, obj):
        import json

        # referans_teklifler boş mu?
        try:
            referanslar = json.loads(obj.referans_teklifler or '[]')
            referans_bos = not isinstance(referanslar, list) or len(referanslar) == 0
        except Exception:
            referans_bos = True

        # teklif_fiyatlari_json boş mu?
        teklif_json_bos = not obj.teklif_fiyatlari_json

        # teklif_fiyatlari_list boş mu?
        try:
            teklif_list = self.get_teklif_fiyatlari_list(obj)
            teklif_list_bos = not isinstance(teklif_list, list) or len(teklif_list) == 0
        except Exception:
            teklif_list_bos = True

        return referans_bos or teklif_json_bos or teklif_list_bos



class PurchaseApprovalSerializer(serializers.ModelSerializer):
    kullanici_email = serializers.EmailField(source='kullanici.email')

    class Meta:
        model = PurchaseApproval
        fields = [
            'belge_no',
            'uniq_detail_no',
            'action',
            'aciklama',
            'kullanici_email',
            'created_at'
        ]

class ApprovalHistoryGroupedSerializer(serializers.Serializer):
    sira = serializers.IntegerField()
    action = serializers.CharField()
    kullanici = serializers.EmailField()
    tarih = serializers.CharField()
    aciklama = serializers.CharField(allow_blank=True, required=False)
