# backend/productconfig/admin/old_component_code.py
from django.utils.html import format_html
from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from ..models import OldComponentCode, Question, Option


class OldComponentCodeResource(resources.ModelResource):
   """OldComponentCode için Import/Export kaynağı."""
   
   # Question ForeignKey alanları
   question_1 = fields.Field(
       column_name='soru_1',
       attribute='question_1',
       widget=ForeignKeyWidget(Question, field='name')
   )
   question_2 = fields.Field(
       column_name='soru_2',
       attribute='question_2',
       widget=ForeignKeyWidget(Question, field='name')
   )
   question_3 = fields.Field(
       column_name='soru_3',
       attribute='question_3',
       widget=ForeignKeyWidget(Question, field='name')
   )

   # ManyToMany Option alanları
   expected_options_1 = fields.Field(
       column_name='beklenen_secenekler_1',
       attribute='expected_options_1',
       widget=ManyToManyWidget(Option, field='name', separator='|')
   )
   expected_options_2 = fields.Field(
       column_name='beklenen_secenekler_2',
       attribute='expected_options_2',
       widget=ManyToManyWidget(Option, field='name', separator='|')
   )
   expected_options_3 = fields.Field(
       column_name='beklenen_secenekler_3',
       attribute='expected_options_3',
       widget=ManyToManyWidget(Option, field='name', separator='|')
   )

   type_sequence_no = fields.Field(
       column_name='tip_sira_no',
       attribute='type_sequence_no'
   )

   number_of_codes = fields.Field(
       column_name='uretilecek_kod_sayisi',
       attribute='number_of_codes'
   )

   class Meta:
       model = OldComponentCode
       import_id_fields = ('name',)
       export_order = (
           'id', 'name', 'number_of_codes',
           'question_1', 'expected_options_1', 'code_part_1', 'type_sequence_no',
           'question_2', 'expected_options_2', 'code_part_2',
           'question_3', 'expected_options_3', 'code_part_3',
           'code_format', 'supports_multiple', 
           'is_active', 'created_at', 'updated_at'
       )
       skip_unchanged = True
       report_skipped = True


@admin.register(OldComponentCode)
class OldComponentCodeAdmin(ImportExportModelAdmin):
   """OldComponentCode için admin panel ayarları."""
   
   resource_class = OldComponentCodeResource

   list_display = [
       'name',
       'number_of_codes',
       'get_questions_and_codes',
       'get_type_sequence_numbers',
       'get_generated_codes',  # Yeni eklenen alan
       'supports_multiple',
       'is_active'
   ]

   list_filter = [
       'number_of_codes',
       'supports_multiple',
       'is_active',
       'question_1',
       'question_2',
       'question_3'
   ]

   search_fields = [
       'name',
       'code_part_1',
       'code_part_2',
       'code_part_3',
       'type_sequence_no'
   ]

   filter_horizontal = [
       'expected_options_1',
       'expected_options_2',
       'expected_options_3'
   ]
   
   # Oluşturma ve güncelleme tarihlerini gizlemek için:
   exclude = ['created_at', 'updated_at']
   list_per_page = 20

   def get_questions_and_codes(self, obj):
       """Soruları ve kod parçalarını formatlı gösterir."""
       parts = []
       for i in range(1, 4):
           question = getattr(obj, f'question_{i}')
           code_part = getattr(obj, f'code_part_{i}')
           parts.append(f"S{i}: {question.name[:20]}... ({code_part})")
       return ' | '.join(parts)
   get_questions_and_codes.short_description = 'Sorular ve Kod Parçaları'

   def get_type_sequence_numbers(self, obj):
       """Tip sıra numaralarını formatlı gösterir."""
       sequence_numbers = obj.type_sequence_no.split(',')
       sequence_count = len(sequence_numbers)
       return f"{', '.join(sequence_numbers)} ({sequence_count} adet)"
   get_type_sequence_numbers.short_description = 'Tip Sıra Numaraları'

   def save_model(self, request, obj, form, change):
       """Model kaydedilmeden önce format ve tip sıra no kontrolü yapar."""
       try:
           # Format testi yap
           test_format = obj.code_format.format(
               part1='TEST1',
               tip_sıra_no='01',
               part2='TEST2',
               part3='TEST3'
           )
           
           # Tip sıra no sayısı kontrolü
           sequence_numbers = obj.type_sequence_no.split(',')
           if len(sequence_numbers) < obj.number_of_codes:
               self.message_user(
                   request, 
                   f"Tip sıra no sayısı ({len(sequence_numbers)}), üretilecek kod sayısından ({obj.number_of_codes}) az olamaz!", 
                   level='ERROR'
               )
               return
               
       except Exception as e:
           self.message_user(request, f"Hatalı kod formatı: {str(e)}", level='ERROR')
           return
       
       super().save_model(request, obj, form, change)

   def get_readonly_fields(self, request, obj=None):
       """Düzenleme sırasında bazı alanları readonly yapar."""
       if obj:  # Nesne düzenleniyorsa
           return ['created_at', 'updated_at']
       return []

   def get_import_formats(self):
       """İzin verilen import formatları."""
       formats = super().get_import_formats()
       return [f for f in formats if f.__name__ == 'XLSX']

   def get_export_formats(self):
       """İzin verilen export formatları."""
       formats = super().get_export_formats()
       return [f for f in formats if f.__name__ == 'XLSX']
   

   def get_generated_codes(self, obj):
    """
    Tip sıra numaralarını kullanarak örnek kodları gösterir.
    """
    try:
        sequence_numbers = [x.strip() for x in obj.type_sequence_no.split(',')]
        codes = []

        # Her tip sıra no için örnek kod oluştur
        for seq_no in sequence_numbers[:obj.number_of_codes]:
            code = obj.code_format.format(
                part1=obj.code_part_1 or 'N/A',
                tip_sıra_no=seq_no,
                part2=obj.code_part_2 or 'N/A',
                part3=obj.code_part_3 or 'N/A'
            )
            codes.append(f'<span style="font-family: monospace;">{code}</span>')

        return format_html('<br>'.join(codes))
    except Exception as e:
        return format_html(
            f'<span style="color: red;">Kod üretme hatası: {str(e)}</span>'
        )

            
   get_generated_codes.short_description = 'Üretilen Kodlar'
   get_generated_codes.allow_tags = True

    # Liste görünümünde stil eklemek için
   class Media:
        css = {
            'all': ('admin/css/old_component_codes.css',)
        } 