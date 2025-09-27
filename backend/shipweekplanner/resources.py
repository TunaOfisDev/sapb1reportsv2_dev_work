# backend/shipweekplanner/resources.py
from import_export import resources, fields
from import_export.widgets import DateWidget
from .models.models import ShipmentOrder
from datetime import datetime, date

class ShipmentOrderResource(resources.ModelResource):
    """
    ShipmentOrder modelinde tarih formatlarını işlemek için özel kaynak sınıfı.
    """
    order_date = fields.Field(
        column_name='order_date',
        attribute='order_date',
        widget=DateWidget(format='%d.%m.%Y')
    )
    shipment_date = fields.Field(
        column_name='shipment_date',
        attribute='shipment_date',
        widget=DateWidget(format='%d.%m.%Y')
    )
    planned_date_mirror = fields.Field(
        column_name='planned_date_mirror',
        attribute='planned_date_mirror',
        widget=DateWidget(format='%d.%m.%Y')
    )

    def before_import_row(self, row, **kwargs):
        """
        Import sırasında her satırı işlemeden önce çalışan metod
        """
        # Tarih alanlarını düzenle
        date_fields = ['order_date', 'shipment_date', 'planned_date_mirror']
        for field in date_fields:
            if field in row and row[field]:
                try:
                    if isinstance(row[field], datetime):
                        row[field] = row[field].date()
                    elif isinstance(row[field], str):
                        if '.' in row[field]:
                            row[field] = datetime.strptime(row[field], '%d.%m.%Y').date()
                        else:
                            row[field] = datetime.strptime(row[field], '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    if field == 'planned_date_mirror':
                        row[field] = row[field]  # Orijinal değeri koru
                    else:
                        row[field] = None

    def import_field(self, field, obj, data, is_m2m=False, **kwargs):
        """
        Import field metodu
        """
        if field.attribute and field.column_name in data:
            field.save(obj, data, is_m2m)

    def save_instance(self, instance, *args, **kwargs):
        """
        Instance'ı kaydetmek için admin_save metodunu kullan
        """
        try:
            if instance.planned_dates is None:
                instance.planned_dates = []
            
            instance.admin_save()
            return instance
        except Exception as e:
            print(f"Error saving instance: {str(e)}")
            raise

    class Meta:
        model = ShipmentOrder
        fields = (
            'id',
            'order_number', 
            'customer_name', 
            'order_date', 
            'shipment_date',
            'planned_date_mirror',
            'sales_person',
            'shipment_details',
            'shipment_notes',
            'selected_color'
        )
        import_id_fields = ['order_number']
        skip_unchanged = True
        report_skipped = False