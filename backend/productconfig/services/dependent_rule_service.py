# backend/productconfig/services/dependent_rule_service.py
from django.db.models import QuerySet
from ..models import DependentRule, Question, Variant, Option
from ..utils.dependent_rule_helper import DependentRuleHelper
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class DependentRuleService:
    def __init__(self):
        self.helper = DependentRuleHelper()

    def get_rules_for_question(self, question: Question) -> List[DependentRule]:
        return self.helper.get_rules_for_question(question)

    def create_rule(self, data: dict) -> DependentRule:
        """Yeni bir kural oluşturur"""
        rule = DependentRule.objects.create(**data)
        logger.info(f"Yeni bağımlı kural oluşturuldu - ID: {rule.id}, Ad: {rule.name}")
        return rule

    def get_active_rules_for_question(self, question: Question) -> List[DependentRule]:
        """Soru için aktif kuralları helper üzerinden getirir"""
        logger.debug(f"Aktif kurallar alınıyor: Soru ID {question.id}")
        return self.helper.get_rules_for_question(question)

    def process_rules_for_answer(self, question: Question, variant: Variant, selected_option: Optional[Option] = None):
        """Yanıtlanan soru için bağımlı kuralları işler"""
        rules = self.get_active_rules_for_question(question)

        for rule in rules:
            # İşte burada sadece 2 parametre gönderiyoruz
            is_triggered = self.helper.evaluate_rule(rule, variant)

            dependent_questions = self.helper.get_dependent_questions(rule)
            
            if rule.rule_type == DependentRule.RuleType.SHOW_ON_OPTION:
                if is_triggered:
                    self._activate_dependent_questions(dependent_questions, variant)
                else:
                    self._deactivate_dependent_questions(dependent_questions, variant)
            else:  # HIDE_ON_OPTION
                if is_triggered:
                    self._deactivate_dependent_questions(dependent_questions, variant)
                else:
                    self._activate_dependent_questions(dependent_questions, variant)

        self._evaluate_all_dependent_questions(variant)


    def _evaluate_all_dependent_questions(self, variant: Variant):
        """Tüm bağımlı soruları yeniden değerlendirir"""
        for rule in DependentRule.objects.filter(is_active=True):
            is_triggered = self.helper.evaluate_rule(rule, variant)
            dependent_questions = self.helper.get_dependent_questions(rule)

            if is_triggered:
                self._activate_dependent_questions(dependent_questions, variant)
            else:
                self._deactivate_dependent_questions(dependent_questions, variant)

    def _activate_dependent_questions(self, questions: QuerySet, variant: Variant):
        """Bağımlı soruları aktifleştirir"""
        for question in questions:
            if question not in variant.answered_questions.all():
                variant.answered_questions.add(question)
                question.is_active = True
                question.save()

    def _deactivate_dependent_questions(self, questions: QuerySet, variant: Variant):
        """Bağımlı soruları devre dışı bırakır"""
        for question in questions:
            if question in variant.answered_questions.all():
                variant.answered_questions.remove(question)
                question.is_active = False
                question.save()

    def evaluate_rule(self, rule: DependentRule, variant) -> bool:
        """Bir kuralı değerlendirir"""
        try:
            return rule.evaluate(variant)
        except Exception as e:
            logger.error(f"Kural değerlendirme hatası: {str(e)}")
            return False