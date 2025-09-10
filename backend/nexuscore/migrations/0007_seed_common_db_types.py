# path: backend/nexuscore/migrations/0007_seed_common_db_types.py

from django.db import migrations

# Hangi veritabanları için başlangıç verisi ekleyeceğimizi tanımlayalım
DB_TYPES_TO_SEED = {
    'sql_server': {
        # Ham Tip Adı -> Standart Kategori
        'bigint': 'integer',
        'int': 'integer',
        'smallint': 'integer',
        'tinyint': 'integer',
        'bit': 'boolean',
        'decimal': 'decimal',
        'numeric': 'decimal',
        'money': 'decimal',
        'float': 'decimal',
        'real': 'decimal',
        'date': 'date',
        'datetime': 'datetime',
        'datetime2': 'datetime',
        'smalldatetime': 'datetime',
        'char': 'string',
        'varchar': 'string',
        'text': 'string',
        'nchar': 'string',
        'nvarchar': 'string',
        'ntext': 'string',
        'uniqueidentifier': 'string',
    },
    'postgresql': {
        # Ham Tip Adı -> Standart Kategori
        'bigint': 'integer',
        'integer': 'integer',
        'smallint': 'integer',
        'boolean': 'boolean',
        'numeric': 'decimal',
        'decimal': 'decimal',
        'double precision': 'decimal',
        'real': 'decimal',
        'money': 'decimal',
        'date': 'date',
        'timestamp': 'datetime',
        'timestamp without time zone': 'datetime',
        'timestamp with time zone': 'datetime',
        'char': 'string',
        'character': 'string',
        'varchar': 'string',
        'character varying': 'string',
        'text': 'string',
        'uuid': 'string',
        'json': 'json',
        'jsonb': 'json',
    }
}

def seed_data(apps, schema_editor):
    DBTypeMapping = apps.get_model('nexuscore', 'DBTypeMapping')
    
    mappings_to_create = []
    for db_type, mappings in DB_TYPES_TO_SEED.items():
        for source_type, general_category in mappings.items():
            # Eğer bu eşleşme zaten varsa ekleme (ignore_conflicts=True)
            mappings_to_create.append(
                DBTypeMapping(
                    db_type=db_type,
                    source_type=source_type,
                    general_category=general_category
                )
            )
    
    DBTypeMapping.objects.bulk_create(mappings_to_create, ignore_conflicts=True)
    print(f"\n{len(mappings_to_create)} adet başlangıç veri tipi eşleştirmesi eklendi.")


def reverse_seed_data(apps, schema_editor):
    # Bu migration geri alındığında veriyi silmek için.
    DBTypeMapping = apps.get_model('nexuscore', 'DBTypeMapping')
    
    for db_type, mappings in DB_TYPES_TO_SEED.items():
        for source_type in mappings.keys():
            DBTypeMapping.objects.filter(db_type=db_type, source_type=source_type).delete()
    print("\nBaşlangıç veri tipi eşleştirmeleri kaldırıldı.")


class Migration(migrations.Migration):

    dependencies = [
        ('nexuscore', '0006_alter_dbtypemapping_general_category_and_more'), 
    ]

    operations = [
        migrations.RunPython(seed_data, reverse_code=reverse_seed_data),
    ]