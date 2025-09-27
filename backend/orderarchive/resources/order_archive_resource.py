# backend/orderarchive/resources/order_archive_resource.py

from import_export import resources, fields
from ..models.order_archive_model import OrderDetail

class OrderDetailResource(resources.ModelResource):
    """
    OrderDetail modeline ait verilerin import-export işlemleri için kaynak sınıfı.
    """

    id = fields.Field(
        attribute='id',
        column_name='id'  # İçe aktarma dosyanızdaki başlık ismi
    )

    class Meta:
        model = OrderDetail
        import_id_fields = ['id']  # 'id' alanını eşleştirme için kullan
        fields = (
            "id",
            "seller",
            "order_number",
            "order_date",
            "year",
            "month",
            "delivery_date",
            "country",
            "city",
            "customer_code",
            "customer_name",
            "document_description",
            "color_code",
            "detail_description",
            "line_number",
            "item_code",
            "item_description",
            "quantity",
            "unit_price",
            "vat_percentage",
            "vat_amount",
            "discount_rate",
            "discount_amount",
            "currency",
            "exchange_rate",
            "currency_price",
            "currency_movement_amount",
        )
