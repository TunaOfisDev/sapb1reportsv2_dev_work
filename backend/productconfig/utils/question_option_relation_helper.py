# backend/productconfig/utils/question_option_relation_helper.py
from ..models import QuestionOptionRelation, Question

class QuestionOptionRelationHelper:
    """
    Soru ve seçenekler arasındaki ilişkileri yönetmek için yardımcı sınıf.
    """

    def get_options_for_question(self, question: Question, relation_type: str):
        """
        Verilen soru ve ilişki türüne göre seçenekleri döner.
        """
        relation = QuestionOptionRelation.objects.filter(
            question=question,
            relation_type=relation_type
        ).first()
        
        # İlgili ilişki varsa seçenekleri döner, yoksa boş bir liste döner
        return relation.options.all() if relation else []

    def get_relations_by_type(self, relation_type: str):
        """
        Belirli bir ilişki türüne göre ilişkili soruları ve seçenekleri getirir.
        """
        return QuestionOptionRelation.objects.filter(
            relation_type=relation_type
        ).select_related('question').prefetch_related('options').order_by('order')

    def get_ordered_relations_for_question(self, question: Question):
        """
        Verilen bir soru için ilişkileri sıralı bir şekilde döner.
        """
        return QuestionOptionRelation.objects.filter(
            question=question
        ).order_by('order')
