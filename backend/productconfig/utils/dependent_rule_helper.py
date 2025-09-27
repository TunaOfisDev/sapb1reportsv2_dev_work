# backend/productconfig/utils/dependent_rule_helper.py
from ..models import DependentRule, Question, Option
from ..dto.rule_context import RuleContext
from django.db.models import QuerySet
import logging

logger = logging.getLogger(__name__)

class DependentRuleHelper:
    def __init__(self):
        self.context = RuleContext()  # Eğer hala kullanıyorsanız

    def get_rules_for_question(self, question: Question) -> QuerySet:
        """Belirli bir soruya bağlı kuralları getirir"""
        return DependentRule.objects.filter(
            parent_question=question,
            is_active=True
        ).order_by('order')


    def evaluate_rule(self, rule: DependentRule, variant) -> bool:
        """Kuralı değerlendirir"""
        try:
            answer = variant.text_answers.get(str(rule.parent_question.id))
            if not answer:
                return False
                
            answer_id = answer.get('answer_id')
            if not answer_id:
                return False
                
            if rule.rule_type == DependentRule.RuleType.SHOW_ON_OPTION:
                return answer_id == rule.trigger_option.id
            else:  # HIDE_ON_OPTION
                return answer_id != rule.trigger_option.id
        except Exception as e:
            logger.error(f"Kural değerlendirme hatası - Kural: {rule.id}, Hata: {str(e)}")
            return False



    def get_dependent_questions(self, rule: DependentRule) -> QuerySet:
        """Kuralın bağımlı sorularını getirir"""
        return rule.dependent_questions.filter(is_active=True)

    def check_rule_condition(self, rule: DependentRule, selected_option: Option) -> bool:
        """Seçilen seçeneğin kuralı tetikleyip tetiklemediğini kontrol eder"""
        return rule.trigger_option == selected_option

    def process_rule_result(self, rule: DependentRule, variant, result: bool):
        """Kural sonucuna göre soruların görünürlüğünü günceller"""
        dependent_questions = self.get_dependent_questions(rule)
        
        for question in dependent_questions:
            if result and rule.rule_type == DependentRule.RuleType.SHOW_ON_OPTION:
                self.context.add_visible_question(question.id)
            elif not result and rule.rule_type == DependentRule.RuleType.HIDE_ON_OPTION:
                self.context.add_hidden_question(question.id)

            logger.debug(f"Soru görünürlüğü güncellendi: Soru ID {question.id}, Görünür: {self.context.is_question_visible(question.id)}")