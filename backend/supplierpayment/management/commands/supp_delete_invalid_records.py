# backend/supplierpayment/management/commands/supp_delete_invalid_records.py
# sudo -u www-data /var/www/sapb1reportsv2/venv/bin/python /var/www/sapb1reportsv2/backend/manage.py supp_delete_invalid_records --all
from django.core.management.base import BaseCommand
from supplierpayment.models.models import SupplierPayment
from django.db.models import Q

class Command(BaseCommand):
    help = "Belirli bir kritere göre hatalı veya geçersiz SupplierPayment verilerini siler."

    def add_arguments(self, parser):
        parser.add_argument(
            '--belge_tarih',
            type=str,
            help="Belirli bir belge tarihi (YYYY-MM-DD) için verileri sil",
        )
        parser.add_argument(
            '--cari_kod',
            type=str,
            help="Belirli bir cari kodu için verileri sil",
        )
        parser.add_argument(
            '--invalid',
            action='store_true',
            help="Geçersiz kayıtları sil: trans_id veya line_id eksik ya da line_id 0 olan kayıtlar.",
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help="Tüm SupplierPayment verilerini sil",
        )

    def handle(self, *args, **options):
        belge_tarih = options.get('belge_tarih')
        cari_kod = options.get('cari_kod')
        delete_invalid = options.get('invalid')
        delete_all = options.get('all')

        try:
            if delete_all:
                count, _ = SupplierPayment.objects.all().delete()
                self.stdout.write(self.style.SUCCESS(f"Tüm veriler silindi: {count} kayıt."))
            
            elif delete_invalid:
                # Geçersiz kayıtları sil
                invalid_qs = SupplierPayment.objects.filter(
                    Q(trans_id__isnull=True) | 
                    Q(line_id__isnull=True) | 
                    Q(line_id=0)
                )
                count, _ = invalid_qs.delete()
                self.stdout.write(self.style.SUCCESS(f"Geçersiz kayıtlar silindi: {count} kayıt."))
            
            elif belge_tarih:
                count, _ = SupplierPayment.objects.filter(belge_tarih=belge_tarih).delete()
                self.stdout.write(self.style.SUCCESS(f"Belge tarihi {belge_tarih} için {count} kayıt silindi."))
            
            elif cari_kod:
                count, _ = SupplierPayment.objects.filter(cari_kod=cari_kod).delete()
                self.stdout.write(self.style.SUCCESS(f"Cari kod {cari_kod} için {count} kayıt silindi."))
            
            else:
                self.stdout.write(self.style.ERROR(
                    "En az bir kriter (--belge_tarih, --cari_kod, --invalid veya --all) belirtmeniz gerekiyor."
                ))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Hata oluştu: {e}"))