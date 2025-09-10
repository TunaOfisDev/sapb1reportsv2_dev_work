# path: backend/nexuscore/management/commands/refresh_metadata.py
from django.core.management.base import BaseCommand
from nexuscore.models import VirtualTable
from nexuscore.services import connection_manager
from django.db import transaction

class Command(BaseCommand):
    help = 'Tüm Sanal Tabloların (VirtualTable) kolon meta verilerini yeniden oluşturur.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Meta veri yenileme işlemi başlıyor...'))
        
        tables_to_update = VirtualTable.objects.select_related('connection').all()
        updated_count = 0
        failed_count = 0

        for table in tables_to_update:
            self.stdout.write(f"-> İşleniyor: '{table.title}' (ID: {table.id})")
            try:
                with transaction.atomic():
                    result = connection_manager.generate_metadata_for_query(
                        table.connection,
                        table.sql_query
                    )
                    
                    if result.get('success'):
                        table.column_metadata = result.get('metadata')
                        table.save(update_fields=['column_metadata', 'updated_at'])
                        updated_count += 1
                        self.stdout.write(self.style.SUCCESS(f"   Başarılı."))
                    else:
                        failed_count += 1
                        self.stderr.write(self.style.ERROR(f"   HATA: {result.get('error')}"))

            except Exception as e:
                failed_count += 1
                self.stderr.write(self.style.ERROR(f"   KRİTİK HATA: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS('='*30))
        self.stdout.write(self.style.SUCCESS(f'İşlem Tamamlandı. {updated_count} tablo güncellendi, {failed_count} tabloda hata oluştu.'))