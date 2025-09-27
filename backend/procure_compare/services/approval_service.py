# File: backend/procure_compare/services/approval_service.py

import json
from procure_compare.models.approval import PurchaseApproval
from procure_compare.models.comparison import PurchaseComparison
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

def create_approval_record(data):
    belge_no = data.get("belge_no")
    uniq_detail_no = data.get("uniq_detail_no")
    action = data.get("action")
    aciklama = data.get("aciklama")
    kullanici = data.get("kullanici")  # email

    if not all([belge_no, uniq_detail_no, action, kullanici]):
        raise ValidationError("Eksik veri gönderildi.")

    try:
        user = User.objects.get(email=kullanici)
    except User.DoesNotExist:
        raise ValidationError("Kullanıcı bulunamadı.")

    # ✅ Departman bazlı yetki kontrolü
    allowed_department = 'Satin_Alma_Onay'
    user_departments = user.departments.values_list('name', flat=True)

    if allowed_department not in user_departments:
        raise ValidationError("Bu kullanıcı onaylama yetkisine sahip değil.")

    # ✅ Onay kayıt kontrolü - dinamik döngü mantığı
    if action in ["onay", "kismi_onay", "red", "onay_iptal"]:
        previous_records = list(
            PurchaseApproval.objects
            .filter(belge_no=belge_no, uniq_detail_no=uniq_detail_no)
            .order_by('-created_at')
        )

        if previous_records:
            last_action = previous_records[0].action

            if action == "onay_iptal":
                if last_action not in ["onay", "kismi_onay", "red"]:
                    raise ValidationError("İptal edebilmek için önce onay, kısmi onay veya red işlemi yapılmış olmalı.")
            else:
                if last_action in ["onay", "kismi_onay", "red"]:
                    raise ValidationError("Bu belge satırı için daha önce onay kaydı yapılmış.")
                elif last_action == "onay_iptal":
                    pass  # İptal edilmiş, tekrar onay yapılabilir
        else:
            if action == "onay_iptal":
                raise ValidationError("İptal işlemi için önce bir onay yapılmış olmalı.")

    # ✅ Satır detayını JSON formatına hazırla
    try:
        comparison = PurchaseComparison.objects.get(
            belge_no=belge_no,
            uniq_detail_no=uniq_detail_no
        )

        try:
            teklif_dict = json.loads(comparison.teklif_fiyatlari_json or "{}")
        except Exception:
            teklif_dict = {}

        referanslar = comparison.referans_teklifler
        if isinstance(referanslar, str):
            try:
                referanslar = json.loads(referanslar)
            except Exception:
                referanslar = []

        satir_detay = {
            "belge_tarih": comparison.belge_tarih.strftime("%Y-%m-%d"),
            "kalem_tanimi": comparison.kalem_tanimi,
            "tedarikci": comparison.tedarikci_ad,
            "sip_miktar": float(comparison.sip_miktar),
            "net_fiyat_dpb": float(comparison.net_fiyat_dpb),
            "detay_doviz": comparison.detay_doviz,
            "net_tutar_ypb": float(comparison.net_tutar_ypb),
            "teklif_fiyatlari": teklif_dict,
            "referans_teklifler": referanslar,
        }

    except PurchaseComparison.DoesNotExist:
        satir_detay = {}

    approval = PurchaseApproval.objects.create(
        belge_no=belge_no,
        uniq_detail_no=uniq_detail_no,
        action=action,
        aciklama=aciklama,
        kullanici=user,
        satir_detay_json=satir_detay
    )

    return approval
