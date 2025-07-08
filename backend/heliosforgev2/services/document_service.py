# backend/heliosforgev2/services/document_service.py

from django.utils import timezone
from heliosforgev2.models.document import Document


def create_document_record(uploaded_file, page_count: int = 0) -> Document:
    """
    Yeni bir PDF belgesi kaydeder ve Document modeline işler.

    Args:
        uploaded_file: Django FILE nesnesi (request.FILES['file'])
        page_count: Sayfa sayısı (parser sonrası girilir)

    Returns:
        Kayıt edilen Document nesnesi
    """
    document = Document.objects.create(
        file=uploaded_file,
        page_count=page_count,
        status="pending"
    )
    return document


def update_document_status(document: Document, status: str) -> None:
    """
    Belgenin işlenme durumunu günceller (parsed, error vb.)

    Args:
        document: Güncellenecek belge
        status: 'parsed', 'error', vs.
    """
    document.status = status
    if status == "parsed":
        document.parsed_at = timezone.now()
    document.save()


def get_document_by_id(doc_id: int) -> Document:
    """
    ID ile belge getirir. Bulunamazsa exception fırlatır.
    """
    return Document.objects.get(id=doc_id)
