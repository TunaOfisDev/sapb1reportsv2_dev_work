# path: sapb1reportsv2/stockcardintegration/services/create_or_update_card.py

from stockcardintegration.models.models import StockCard
from stockcardintegration.api.serializers import StockCardSerializer


def create_or_update_stock_card_by_code(item_code, data, user):
    """
    Güncelleme yapılmak istenen stok kodu sistemde yoksa önce local DB'ye kaydedilir, sonra güncellenir.
    """
    try:
        instance = StockCard.objects.get(item_code=item_code)
        serializer = StockCardSerializer(instance, data=data, partial=True, context={"request": user})
    except StockCard.DoesNotExist:
        data["item_code"] = item_code
        serializer = StockCardSerializer(data=data, context={"request": user})

    serializer.is_valid(raise_exception=True)
    return serializer.save()
