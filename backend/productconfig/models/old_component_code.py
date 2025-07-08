# backend/productconfig/models/old_component_code.py
from django.db import models
from .base import BaseModel
from .question import Question
from .option import Option
import logging

logger = logging.getLogger(__name__)

class OldComponentCode(BaseModel):
    """Eski bileşen kodlarını oluşturmak için kullanılan model"""
    

    number_of_codes = models.PositiveIntegerField(
        default=1,
        verbose_name="Üretilecek Eski Kod Sayısı"
    )

    name = models.CharField(max_length=255, verbose_name="Kod Adı")


    # Kod parçaları için gerekli sorular
    question_1 = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='codes_for_part1',
        verbose_name="Soru 1"
    )
    expected_options_1 = models.ManyToManyField(
        Option,
        related_name='codes_for_part1',
        verbose_name="Beklenen Seçenekler 1"
    )
    code_part_1 = models.CharField(
        max_length=50,
        verbose_name="Kod Parçası 1"
    )
    type_sequence_no = models.CharField(
        max_length=50,
        verbose_name="Tip Sıra No",
        help_text="Virgülle ayrılmış değerler girilebilir (örn: 01,02)"
    )

    question_2 = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='codes_for_part2',
        verbose_name="Soru 2"
    )
    expected_options_2 = models.ManyToManyField(
        Option,
        related_name='codes_for_part2',
        verbose_name="Beklenen Seçenekler 2"
    )
    code_part_2 = models.CharField(
        max_length=50,
        verbose_name="Kod Parçası 2"
    )

    question_3 = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='codes_for_part3',
        verbose_name="Soru 3"
    )
    expected_options_3 = models.ManyToManyField(
        Option,
        related_name='codes_for_part3',
        verbose_name="Beklenen Seçenekler 3"
    )
    code_part_3 = models.CharField(
        max_length=50,
        verbose_name="Kod Parçası 3"
    )

    code_format = models.CharField(
        max_length=255,
        verbose_name="Kod Formatı",
        help_text="Örnek: {part1} {tip_sıra_no}{part2} {part3}",
        default="{part1} {tip_sıra_no}{part2} {part3}"
    )

    supports_multiple = models.BooleanField(
        default=False,
        verbose_name="Çoklu Seçim Desteği"
    )

    class Meta:
        verbose_name = "12-Eski Bileşen Kodu"
        verbose_name_plural = "12-Eski Bileşen Kodları"
        ordering = ['name',]

    def __str__(self):
        return f"{self.name}"

    def generate_code(self, variant_answers):
        """
        Variant cevaplarına göre eski bileşen kodunu oluşturur
        
        Args:
            variant_answers: Variant'ın text_answers sözlüğü
            
        Returns:
            Dict: {
                'codes': List[str],  # Oluşturulan kodlar
                'sequence_numbers': List[str],  # Kullanılan sıra numaraları
                'number_of_codes': int,  # Üretilen kod sayısı
                'code_format': str  # Kullanılan kod formatı
            }
        """
        try:
            # Her soru için cevapları kontrol et
            codes = []
            code_parts = []
            
            # Soru 1, 2, 3 için kontrolleri yap
            for q_num in range(1, 4):
                question = getattr(self, f'question_{q_num}')
                expected_options = getattr(self, f'expected_options_{q_num}').all()
                code_part = getattr(self, f'code_part_{q_num}')
                
                # Sorunun cevabını al
                answer = variant_answers.get(str(question.id))
                if not answer:
                    logger.warning(f"Soru {question.id} için cevap bulunamadı")
                    return None

                # Cevap kontrolü ve kod parçasını ekle
                if 'answer_id' in answer:
                    option_id = answer['answer_id']
                    if Option.objects.get(id=option_id) in expected_options:
                        code_parts.append(code_part)
                    else:
                        logger.warning(f"Geçersiz seçenek - Soru {question.id}, Option ID: {option_id}")
                        return None
                elif 'answer_ids' in answer and self.supports_multiple:
                    # Çoklu seçim desteği varsa
                    option_ids = answer['answer_ids']
                    matched_options = [opt for opt in expected_options if opt.id in option_ids]
                    if matched_options:
                        code_parts.extend([code_part for _ in matched_options])
                    else:
                        logger.warning(f"Geçersiz seçenekler - Soru {question.id}, Options: {option_ids}")
                        return None
                else:
                    logger.warning(f"Geçersiz cevap formatı - Soru {question.id}")
                    return None

            # Tip sıra numaralarını al
            sequence_numbers = [x.strip() for x in self.type_sequence_no.split(',')]
            
            # Üretilecek kod sayısını kontrol et ve sınırla
            number_of_codes = min(self.number_of_codes, len(sequence_numbers))
            
            # Her tip sıra no için kod oluştur
            for seq_no in sequence_numbers[:number_of_codes]:
                if code_parts:
                    code = self.code_format.format(
                        part1=code_parts[0],
                        tip_sıra_no=seq_no,
                        part2=code_parts[1] if len(code_parts) > 1 else '',
                        part3=code_parts[2] if len(code_parts) > 2 else ''
                    )
                    codes.append(code)

            if not codes:
                logger.warning("Kod oluşturulamadı - Yeterli parça yok")
                return None

            # Sonucu formatla ve döndür
            return {
                'codes': codes,
                'sequence_numbers': sequence_numbers[:number_of_codes],
                'number_of_codes': number_of_codes,
                'code_format': self.code_format
            }

        except Exception as e:
            logger.error(f"Kod oluşturma hatası: {str(e)}")
            return None