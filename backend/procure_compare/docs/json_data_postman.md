get http://192.168.2.201/api/v2/procure_compare/comparisons/


-------------------
post

http://192.168.2.201/api/v2/procure_compare/approval-action/


{
  "belge_no": "7454",
  "uniq_detail_no": "12591-1-1",
  "action": "kismi_onay",
  "aciklama": "Fiyat uygun ancak teslim süresi uzun.",
  "satir_detay_json": {
    "belge_tarih": "2025-04-22",
    "kalem_tanimi": "KULP BERFİNO 102 ROMA L:192mm HAM BOYASIZ",
    "tedarikci": "AYDER MET.PLS.KALP.SAN.TİC.LTD.ŞTİ.",
    "sip_miktar": 50.0,
    "net_fiyat_dpb": 60.0,
    "detay_doviz": "TRY",
    "net_tutar_ypb": 3000.0,
    "teklif_fiyatlari": {
      "AYDER MET.PLS.KALP.S": "60,00 TRY (Kur: 1)",
      "BERFİNO MOBİLYA AKS.": "63,00 TRY (Kur: 1)",
      "STARWOOD YAPI MARK.": "80,00 TRY (Kur: 1)"
    },
    "referans_teklifler": ["2269", "2270", "2271"]
  }
}


onay_iptal json post

{
  "belge_no": "7454",
  "uniq_detail_no": "12591-1-1",
  "action": "onay_iptal",
  "aciklama": "Teslim süresi ve fiyat yanlış değerlendirilmiş, işlem iptal edilmiştir.",
  "satir_detay_json": {
    "belge_tarih": "2025-04-22",
    "kalem_tanimi": "KULP BERFİNO 102 ROMA L:192mm HAM BOYASIZ",
    "tedarikci": "AYDER MET.PLS.KALP.SAN.TİC.LTD.ŞTİ.",
    "sip_miktar": 50.0,
    "net_fiyat_dpb": 60.0,
    "detay_doviz": "TRY",
    "net_tutar_ypb": 3000.0,
    "teklif_fiyatlari": {
      "AYDER MET.PLS.KALP.S": "60,00 TRY (Kur: 1)",
      "BERFİNO MOBİLYA AKS.": "63,00 TRY (Kur: 1)",
      "STARWOOD YAPI MARK.": "80,00 TRY (Kur: 1)"
    },
    "referans_teklifler": ["2269", "2270", "2271"]
  }
}
