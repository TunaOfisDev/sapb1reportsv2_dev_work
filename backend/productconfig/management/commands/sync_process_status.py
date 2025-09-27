# backend/productconfig/management/commands/sync_process_status.py
from django.core.management.base import BaseCommand
from django.db import transaction
from productconfig.models import ProductModel, ProcessStatus

class Command(BaseCommand):
    help = 'Tüm ürün modelleri için process status kayıtlarını senkronize eder'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Mevcut process status kayıtlarını sil ve yeniden oluştur',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        with transaction.atomic():
            if force:
                self.stdout.write('Mevcut process status kayıtları siliniyor...')
                ProcessStatus.objects.all().delete()

            # Tüm ürün modellerini al
            product_models = ProductModel.objects.all()
            total = product_models.count()
            created = 0
            updated = 0
            
            self.stdout.write(f'Toplam {total} ürün modeli işlenecek...')

            # Her ürün modeli için process status oluştur/güncelle
            for product_model in product_models:
                status, was_created = ProcessStatus.objects.get_or_create(
                    product_model=product_model
                )
                status.update_status()
                
                if was_created:
                    created += 1
                else:
                    updated += 1
                
                # İlerleme göster
                self.stdout.write(
                    f'İşleniyor... ({created + updated}/{total})',
                    ending='\r'
                )

            self.stdout.write(self.style.SUCCESS(
                f'\nTamamlandı! {created} yeni kayıt oluşturuldu, '
                f'{updated} kayıt güncellendi.'
            ))



