# backend\dynamicreport\models.py
from django.db import models
from django.utils import timezone

class Data(models.Model):
    table_name = models.CharField(max_length=255, unique=True, verbose_name="Tablo Adı") 
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")

    def __str__(self):
        return self.table_name

    class Meta:
        abstract = True

class SqlQuery(Data):
    query = models.TextField(verbose_name="SQL Sorgusu")
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    sys_table_columns = models.BooleanField(default=False, verbose_name="SYS.TABLE_COLUMNS Var mı?")

    class Meta:
        verbose_name = "Data - SQL Sorgusu"
        verbose_name_plural = "Data - SQL Sorguları"

    def save(self, *args, **kwargs):
        self.sys_table_columns = 'SYS.TABLE_COLUMNS' in self.query.upper()
        super(SqlQuery, self).save(*args, **kwargs)



class DynamicTable(Data):
    sql_query = models.ForeignKey(SqlQuery, on_delete=models.CASCADE, verbose_name="SQL Sorgusu")
    hana_data_set = models.JSONField(verbose_name="HANA DATA SET", default=dict, null=True, blank=True)
    fetched_at = models.DateTimeField(default=timezone.now, verbose_name="Veri Çekme Tarihi")

    class Meta:
        verbose_name = "Data - Dinamik Tablo"
        verbose_name_plural = "Data - Dinamik Tablolar"

class HanaDataType(models.Model):
    TYPE_CLASSES = [
                ('continuous_numeric', 'Sürekli Sayısal'),  # float, double, real
                ('discrete_numeric', 'Ayrık Sayısal'),  # integer, smallint, tinyint, bigint
                ('textual', 'Metinsel'),  # varchar, text, nvarchar, alphanum
                ('date_time', 'Tarih/Zaman'),  # date, time, timestamp, seconddate
                ('boolean', 'Mantıksal'),  # boolean
                ('spatial', 'Mekansal'),  # st_point, st_geometry
                ('binary', 'İkilik'),  # varbinary, blob
                ('large_object', 'Büyük Nesne'),  # clob, nclob
                ('array', 'Dizi'),  # array
                ('enumeration', 'Sıralama'),  # custom enums or types that have a limited set of valid values
                ('alphanum', 'Alfanümerik'),
            ]

    type_code = models.CharField(max_length=50, unique=True, verbose_name="Tip Kodu")
    type_description = models.CharField(max_length=255, verbose_name="Tip Açıklaması")
    type_class = models.CharField(max_length=20, choices=TYPE_CLASSES, default='other', null=True, blank=True, verbose_name="Tip Sınıfı")
    formatter_function_name = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = "Data - HANA Veri Tipi"
        verbose_name_plural = "Data - HANA Veri Tipleri"
        
    def save(self, *args, **kwargs):
        if not self.formatter_function_name:
            self.formatter_function_name = f'format_{self.type_code}'
        super(HanaDataType, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.type_code} - {self.type_description} - {self.get_type_class_display()}"

class DynamicHeaders(models.Model):  
    dynamic_table = models.ForeignKey(DynamicTable, on_delete=models.CASCADE, verbose_name="Dinamik Tablo", null=True)
    table_name = models.CharField(max_length=255, verbose_name="Tablo Adı")
    line_no = models.IntegerField(verbose_name="Sıra Numarası")
    header_name = models.CharField(max_length=255, verbose_name="Kolon Başlığı")
    type = models.ForeignKey(HanaDataType, on_delete=models.SET_NULL, null=True, verbose_name="Kolon Tipi")

    class Meta:
        verbose_name = "Data - Dinamik Kolon Başlığı"
        verbose_name_plural = "Data - Dinamik Kolon Başlıkları"

    def save(self, *args, **kwargs):
        sql_query_instance, created = SqlQuery.objects.get_or_create(table_name=self.table_name)
        dynamic_table, created = DynamicTable.objects.get_or_create(
            table_name=self.table_name, 
            sql_query=sql_query_instance
        )
        self.dynamic_table = dynamic_table
        super(DynamicHeaders, self).save(*args, **kwargs)

    def update_or_create_dynamic_headers(column_names, query_table_name):
        for i, column_name in enumerate(column_names):
            defaults = {'header_name': column_name}

            existing_dynamic_header = DynamicHeaders.objects.filter(table_name=query_table_name, line_no=i).first()
            if existing_dynamic_header is not None:
                defaults['type'] = existing_dynamic_header.type

            try:
                dynamic_table_instance = DynamicTable.objects.get(table_name=query_table_name)
                dynamic_header, created = DynamicHeaders.objects.update_or_create(
                    table_name=query_table_name,
                    line_no=i,
                    dynamic_table=dynamic_table_instance,
                    defaults=defaults,
                )
            except DynamicTable.DoesNotExist:
                print(f"DynamicTable nesnesi {query_table_name} için bulunamadı.")

