# backend/productconfig/services/question_option_relation_service.py
from ..models import Question, QuestionOptionRelation
from ..utils.question_option_relation_helper import QuestionOptionRelationHelper

class QuestionOptionRelationService:
    """
    Soru ve seçenek ilişkileri ile ilgili işlemleri yöneten servis.
    """

    def __init__(self):
        self.helper = QuestionOptionRelationHelper()

    def get_master_options(self, question: Question):
        """
        Master ilişki türüne göre soruya ait seçenekleri döner.
        """
        return self.helper.get_options_for_question(question, QuestionOptionRelation.RelationType.MASTER)

    def get_model_options(self, question: Question):
        """
        Model ilişki türüne göre soruya ait seçenekleri döner.
        """
        return self.helper.get_options_for_question(question, QuestionOptionRelation.RelationType.MODEL)

    def get_conditional_options(self, question: Question):
        """
        Koşullu ilişki türüne göre soruya ait seçenekleri döner.
        """
        return self.helper.get_options_for_question(question, QuestionOptionRelation.RelationType.CONDITIONAL)

    def get_all_ordered_options_for_question(self, question: Question):
        """
        Belirli bir soru için tüm ilişki türlerinden seçenekleri sıralı olarak döner.
        """
        ordered_relations = self.helper.get_ordered_relations_for_question(question)
        options = []
        for relation in ordered_relations:
            options.extend(relation.options.all())
        return options
