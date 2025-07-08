# backend/productconfig/management/commands/update_all_process_status.py
from django.core.management.base import BaseCommand
from django.db import transaction
from productconfig.models import ProductModel, ProcessStatus
from django.utils import timezone
import time

class Command(BaseCommand):
    help = 'Tüm ürün modellerinin process status kayıtlarını oluşturur veya günceller'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Mevcut process status kayıtlarını sil ve yeniden oluştur',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=50,
            help='Bir seferde işlenecek ürün modeli sayısı',
        )

    def handle(self, *args, **options):
        force = options['force']
        batch_size = options['batch_size']
        start_time = time.time()

        with transaction.atomic():
            if force:
                self.stdout.write(self.style.WARNING('Mevcut process status kayıtları siliniyor...'))
                ProcessStatus.objects.all().delete()
                self.stdout.write(self.style.SUCCESS('Mevcut kayıtlar silindi.'))

            # Toplam ürün modeli sayısını al
            total_products = ProductModel.objects.count()
            self.stdout.write(f'Toplam {total_products} ürün modeli işlenecek...')

            processed = 0
            created = 0
            updated = 0
            errors = 0

            # Batch işleme için ürün modellerini al
            for i in range(0, total_products, batch_size):
                batch = ProductModel.objects.all()[i:i+batch_size]
                
                for product in batch:
                    try:
                        # ProcessStatus kaydını oluştur veya güncelle
                        status, was_created = ProcessStatus.objects.get_or_create(
                            product_model=product
                        )
                        status.update_status()
                        
                        if was_created:
                            created += 1
                        else:
                            updated += 1
                            
                        processed += 1
                        
                        # İlerleme göster
                        if processed % 10 == 0:  # Her 10 işlemde bir güncelle
                            self.stdout.write(
                                f'İşleniyor... {processed}/{total_products} '
                                f'(Oluşturulan: {created}, Güncellenen: {updated}, Hata: {errors})',
                                ending='\r'
                            )
                    
                    except Exception as e:
                        errors += 1
                        self.stdout.write(
                            self.style.ERROR(
                                f'\nHata - Ürün Model ID {product.id}: {str(e)}'
                            )
                        )

                # Her batch sonrası commit
                transaction.on_commit(lambda: None)

        # İstatistikleri hesapla
        end_time = time.time()
        duration = end_time - start_time
        success_rate = ((processed - errors) / processed * 100) if processed > 0 else 0

        # Sonuç raporu
        self.stdout.write('\n' + '-'*80)
        self.stdout.write(self.style.SUCCESS('İşlem tamamlandı!'))
        self.stdout.write(f'Toplam işlenen: {processed}')
        self.stdout.write(f'Yeni oluşturulan: {created}')
        self.stdout.write(f'Güncellenen: {updated}')
        self.stdout.write(f'Hata sayısı: {errors}')
        self.stdout.write(f'Başarı oranı: %{success_rate:.2f}')
        self.stdout.write(f'Toplam süre: {duration:.2f} saniye')
        self.stdout.write(f'Ortalama işlem süresi: {(duration/processed):.3f} saniye/kayıt')
        self.stdout.write('-'*80)