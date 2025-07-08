# backend/productconfig/services/conditional_options_service.py
from typing import List, Dict, Optional
from ..utils.conditional_options_helper import ConditionalOptionsHelper
from ..models import  Question, ConditionalOption

class ConditionalOptionsService:
   def get_conditional_options(
       self,
       question_id: int, 
       user_selected_option_ids: List[int],
       standard_options: Optional[List[Dict]] = None
   ) -> List[Dict]:
       """
       Koşullu seçenekleri getirir.
       
       Args:
           question_id: Hedef soru ID'si
           user_selected_option_ids: Kullanıcının seçtiği seçeneklerin ID'leri  
           standard_options: Standart seçenekler (opsiyonel)
           
       Returns:
           List[Dict]: Görüntüleme moduna göre uygulanabilir seçenekler
       """
       return ConditionalOptionsHelper.get_applicable_options(
           user_selected_option_ids,
           question_id,
           standard_options
       )

   def get_options_for_question(
       self,
       question_id: int,
       user_selected_option_ids: List[int]
   ) -> List[Dict]:
       """
       Soru için tüm uygulanabilir seçenekleri getirir.
       """
       # Standart seçenekleri getir
       question = Question.objects.get(id=question_id)
       standard_options = [
           ConditionalOptionsHelper._serialize_option(opt)
           for opt in question.options.filter(is_active=True)
       ]

       # Koşullu seçenekleri al ve birleştir
       return self.get_conditional_options(
           question_id,
           user_selected_option_ids,
           standard_options
       )

   def merge_with_existing_options(
       self,
       question_id: int,
       existing_options: List[Dict],
       user_selected_option_ids: List[int]
   ) -> List[Dict]:
       """Mevcut seçenekleri koşullu seçeneklerle birleştirir."""
       conditional_options = self.get_conditional_options(
           question_id, 
           user_selected_option_ids,
           existing_options
       )
       
       # OVERRIDE modu kontrolü
       override_rule = ConditionalOption.objects.filter(
           display_mode=ConditionalOption.DisplayMode.OVERRIDE,
           trigger_option_1__id__in=user_selected_option_ids,
           trigger_option_2__id__in=user_selected_option_ids,
           target_question_id=question_id,
           is_active=True
       ).first()

       if override_rule:
           return conditional_options
           
       return conditional_options if not existing_options else ConditionalOptionsHelper.inject_conditional_options(
           existing_options,
           conditional_options
       )

   def validate_user_selection(
       self,
       user_selected_option_ids: List[int],
       all_available_option_ids: List[int]
   ) -> bool:
       """Kullanıcı seçimlerinin geçerliliğini kontrol eder."""
       invalid_options = set(user_selected_option_ids) - set(all_available_option_ids)
       return len(invalid_options) == 0