# backend/orderarchive/management/commands/delete_invalid_records.py
from django.core.management.base import BaseCommand
from orderarchive.models import OrderDetail

class Command(BaseCommand):
    help = "Belirli bir kritere göre hatalı verileri siler."

    def add_arguments(self, parser):
        # Silme işlemi için kriter ekleme
        parser.add_argument(
            '--order_date',
            type=str,
            help="Belirli bir tarih (YYYY-MM-DD) için verileri sil",
        )
        parser.add_argument(
            '--batch_id',
            type=int,
            help="Yükleme sırasında belirli bir batch ID için verileri sil",
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help="Tüm OrderDetail verilerini sil",
        )

    def handle(self, *args, **options):
        order_date = options['order_date']
        batch_id = options['batch_id']
        delete_all = options['all']

        try:
            if delete_all:
                # Tüm verileri silme
                count, _ = OrderDetail.objects.all().delete()
                self.stdout.write(self.style.SUCCESS(f"Tüm veriler silindi: {count} kayıt."))
                return

            if order_date:
                # Belirli bir tarih için verileri silme
                count, _ = OrderDetail.objects.filter(order_date=order_date).delete()
                self.stdout.write(self.style.SUCCESS(f"Tarih {order_date} için {count} kayıt silindi."))

            if batch_id:
                # Belirli bir batch ID için verileri silme
                count, _ = OrderDetail.objects.filter(batch_id=batch_id).delete()
                self.stdout.write(self.style.SUCCESS(f"Batch ID {batch_id} için {count} kayıt silindi."))

            if not order_date and not batch_id and not delete_all:
                self.stdout.write(self.style.ERROR("En az bir kriter (--order_date, --batch_id veya --all) belirtmeniz gerekiyor."))
        except Exception as e:
            self.stderr.write(f"Hata oluştu: {e}")




'''
### Nasıl Kullanılır?

Bu komutu çalıştırmak için terminalde şu şekilde kullanabilirsiniz:

1. **Belirli Bir Tarih İçin Kayıtları Silmek:**
   ```bash
   python manage.py delete_invalid_records --order_date=2023-12-01
   ```

2. **Batch ID'ye Göre Kayıtları Silmek:**
   ```bash
   python manage.py delete_invalid_records --batch_id=12345
   ```

3. **Tüm Kayıtları Silmek:**
   ```bash
   python manage.py delete_invalid_records --all
   ```

---

### Avantajlar:
1. **Seçici Silme:** Kriterlere göre belirli verileri silebilirsiniz.
2. **Loglama:** Django'nun komut sistemini kullandığınız için işlem detaylarını konsolda görürsünüz.
3. **Güvenlik:** Yanlışlıkla tüm verileri silmemeniz için kriter belirtilmediğinde uyarı verir.


'''