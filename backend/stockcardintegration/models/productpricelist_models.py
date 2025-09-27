# backend/stockcardintegration/models/productpricelist_models.py
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class ProductPriceList(models.Model):
    """
    SAP Business One HANA’dan çekilen ‘Ürün fiyat listesi + eski bileşen’ verisini
    kalıcı olarak tutar.  HANA servisi her çalıştığında `item_code` üzerinden UPSERT
    yapılır; böylece tekil ve güncel kayıt garanti edilir.
    """

    # ──────────────── Ana Alanlar ────────────────
    item_code = models.CharField("Ürün Kodu", max_length=50, unique=True, db_index=True)
    item_name = models.CharField("Ürün Adı", max_length=255)

    price_list_name = models.CharField("Satış Fiyat Listesi", max_length=120, default="YOK")
    price = models.DecimalField(
        "Satış Fiyatı",
        max_digits=18,
        decimal_places=4,
        validators=[MinValueValidator(Decimal("0"))],
        default=Decimal("0.0000"),
    )
    currency = models.CharField("Para Birimi", max_length=3, default="TRY")

    old_component_code = models.CharField("Eski Bileşen Kodu", max_length=100, blank=True, default="")

    # ──────────────── Meta Bilgiler ────────────────
    created_at = models.DateTimeField("Oluşturulma", auto_now_add=True)
    updated_at = models.DateTimeField("Güncellenme", auto_now=True)

    class Meta:
        verbose_name = "Ürün Fiyat Listesi Kaydı"
        verbose_name_plural = "Ürün Fiyat Listeleri"
        db_table = "product_price_list"
        ordering = ["item_code"]
        indexes = [
            models.Index(fields=["item_code"], name="idx_ppl_itemcode"),
            models.Index(fields=["price_list_name"], name="idx_ppl_pricelist"),
        ]

    # ──────────────── Yardımcı Metodlar ────────────────
    def __str__(self) -> str:  # noqa: D401
        return f"{self.item_code} – {self.item_name} ({self.price} {self.currency})"

    @classmethod
    def upsert_from_hana(cls, record: dict) -> "ProductPriceList":
        """
        HANA API’sinden gelen tek satırı (dict) karşılar, mevcutsa günceller,
        yoksa oluşturur.  Beklenen anahtar isimleri SQL çıktınla aynıdır.
        """
        cleaned = {
            "item_code": record.get("Ürün Kodu"),
            "item_name": record.get("Ürün Adı"),
            "price_list_name": record.get("Satış Fiyat Listesi") or "YOK",
            "price": record.get("Satış Fiyatı") or 0,
            "currency": record.get("Para Birimi") or "TRY",
            "old_component_code": record.get("Eski Bileşen Kodu") or "",
        }
        obj, _ = cls.objects.update_or_create(
            item_code=cleaned["item_code"],
            defaults=cleaned,
        )
        return obj
