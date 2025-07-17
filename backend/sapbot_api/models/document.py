# backend/sapbot_api/models/document.py
from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.core.validators import FileExtensionValidator
from .base import BaseModel, SoftDeleteModel
import os


class DocumentSource(SoftDeleteModel):
    """Döküman kaynak modeli"""
    
    DOCUMENT_TYPE_CHOICES = [
        ('pdf', 'PDF Döküman'),
        ('video', 'Video Dosyası'),
        ('manual', 'Manuel Giriş'),
        ('api', 'API Dokümantasyonu'),
        ('web', 'Web Sayfası'),
    ]
    
    LANGUAGE_CHOICES = [
        ('tr', 'Türkçe'),
        ('en', 'İngilizce'),
        ('mixed', 'Karışık (TR/EN)'),
    ]
    
    PROCESSING_STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('processing', 'İşleniyor'),
        ('completed', 'Tamamlandı'),
        ('failed', 'Başarısız'),
        ('cancelled', 'İptal Edildi'),
    ]
    
    title = models.CharField(
        max_length=255,
        verbose_name='Başlık'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='Açıklama'
    )
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPE_CHOICES,
        verbose_name='Döküman Tipi'
    )
    file_path = models.FileField(
        upload_to='sapbot_api/documents/%Y/%m/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'mp4', 'avi', 'mov', 'mkv', 'webm'])],
        verbose_name='Dosya Yolu'
    )
    file_size = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name='Dosya Boyutu (bytes)'
    )
    file_hash = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        unique=True,
        verbose_name='Dosya Hash'
    )
    language = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default='tr',
        verbose_name='Dil'
    )
    processing_status = models.CharField(
        max_length=20,
        choices=PROCESSING_STATUS_CHOICES,
        default='pending',
        verbose_name='İşleme Durumu'
    )
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='İşlenme Tarihi'
    )
    processing_error = models.TextField(
        null=True,
        blank=True,
        verbose_name='İşleme Hatası'
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_documents',
        verbose_name='Yükleyen'
    )
    source_url = models.URLField(
        null=True,
        blank=True,
        verbose_name='Kaynak URL'
    )
    version = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='Versiyon'
    )
    tags = JSONField(
        default=list,
        blank=True,
        verbose_name='Etiketler'
    )
    metadata = JSONField(
        default=dict,
        blank=True,
        verbose_name='Ek Bilgiler'
    )
    priority = models.IntegerField(
        default=1,
        choices=[
            (1, 'Düşük'),
            (2, 'Normal'),
            (3, 'Yüksek'),
            (4, 'Kritik'),
        ],
        verbose_name='Öncelik'
    )
    is_public = models.BooleanField(
        default=True,
        verbose_name='Herkese Açık mı?'
    )
    
    class Meta:
        db_table = 'sapbot_document_sources'
        verbose_name = 'Döküman Kaynağı'
        verbose_name_plural = 'Döküman Kaynakları'
        indexes = [
            models.Index(fields=['document_type', 'language']),
            models.Index(fields=['processing_status']),
            models.Index(fields=['file_hash']),
            models.Index(fields=['priority', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_document_type_display()})"
    
    @property
    def file_size_mb(self):
        """Dosya boyutu MB cinsinden"""
        return round(self.file_size / 1024 / 1024, 2) if self.file_size else 0
    
    @property
    def chunk_count(self):
        """Bu dökümanın chunk sayısı"""
        return self.chunks.count()
    
    @property
    def processing_progress(self):
        """İşleme ilerlemesi"""
        if self.processing_status == 'completed':
            return 100
        elif self.processing_status == 'processing':
            return 50
        elif self.processing_status == 'failed':
            return 0
        return 0
    
    def get_file_extension(self):
        """Dosya uzantısını al"""
        if self.file_path:
            return os.path.splitext(self.file_path.name)[1].lower()
        return ''


class KnowledgeChunk(BaseModel):
    """Bilgi parçası modeli"""
    
    TECHNICAL_LEVEL_CHOICES = [
        ('user', 'Son Kullanıcı'),
        ('admin', 'Yönetici'),
        ('developer', 'Geliştirici'),
        ('mixed', 'Karışık'),
    ]
    
    SAP_MODULE_CHOICES = [
        ('FI', 'Mali Muhasebe'),
        ('MM', 'Malzeme Yönetimi'),
        ('SD', 'Satış ve Dağıtım'),
        ('PP', 'Üretim Planlama'),
        ('HR', 'İnsan Kaynakları'),
        ('QM', 'Kalite Yönetimi'),
        ('PM', 'Tesis Bakımı'),
        ('CO', 'Maliyet Kontrolü'),
        ('WM', 'Depo Yönetimi'),
        ('CRM', 'Müşteri İlişkileri'),
        ('BI', 'Business Intelligence'),
        ('ADMIN', 'Sistem Yönetimi'),
        ('OTHER', 'Diğer'),
    ]
    
    source = models.ForeignKey(
        DocumentSource,
        on_delete=models.CASCADE,
        related_name='chunks',
        verbose_name='Kaynak Döküman'
    )
    content = models.TextField(
        verbose_name='İçerik'
    )
    content_hash = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        verbose_name='İçerik Hash'
    )
    content_length = models.IntegerField(
        verbose_name='İçerik Uzunluğu'
    )
    embedding = JSONField(
        null=True,
        blank=True,
        verbose_name='Vector Embedding'
    )
    embedding_model = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='Embedding Model'
    )
    page_number = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Sayfa Numarası'
    )
    section_title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Bölüm Başlığı'
    )
    sap_module = models.CharField(
        max_length=10,
        choices=SAP_MODULE_CHOICES,
        null=True,
        blank=True,
        verbose_name='SAP Modülü'
    )
    technical_level = models.CharField(
        max_length=20,
        choices=TECHNICAL_LEVEL_CHOICES,
        default='user',
        verbose_name='Teknik Seviye'
    )
    keywords = JSONField(
        default=list,
        blank=True,
        verbose_name='Anahtar Kelimeler'
    )
    relevance_score = models.FloatField(
        default=1.0,
        verbose_name='Relevans Skoru'
    )
    usage_count = models.IntegerField(
        default=0,
        verbose_name='Kullanım Sayısı'
    )
    last_used = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Son Kullanım'
    )
    quality_score = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Kalite Skoru'
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name='Doğrulanmış mı?'
    )
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_chunks',
        verbose_name='Doğrulayan'
    )
    
    class Meta:
        db_table = 'sapbot_knowledge_chunks'
        verbose_name = 'Bilgi Parçası'
        verbose_name_plural = 'Bilgi Parçaları'
        indexes = [
            models.Index(fields=['sap_module', 'technical_level']),
            models.Index(fields=['content_hash']),
            models.Index(fields=['usage_count']),
            models.Index(fields=['relevance_score']),
            models.Index(fields=['is_verified']),
        ]
    
    def __str__(self):
        preview = self.content[:100] + '...' if len(self.content) > 100 else self.content
        return f"Chunk - {self.source.title} - {preview}"
    
    def generate_content_hash(self):
        """İçerik hash'i oluştur"""
        import hashlib
        return hashlib.sha256(self.content.encode('utf-8')).hexdigest()
    
    def increment_usage(self):
        """Kullanım sayısını artır"""
        from django.utils import timezone
        self.usage_count += 1
        self.last_used = timezone.now()
        self.save(update_fields=['usage_count', 'last_used'])
    
    def save(self, *args, **kwargs):
        """Kaydetme sırasında hash ve uzunluk hesapla"""
        if not self.content_hash:
            self.content_hash = self.generate_content_hash()
        self.content_length = len(self.content)
        super().save(*args, **kwargs)


class DocumentTag(BaseModel):
    """Döküman etiket modeli"""
    
    TAG_TYPE_CHOICES = [
        ('category', 'Kategori'),
        ('module', 'Modül'),
        ('feature', 'Özellik'),
        ('version', 'Versiyon'),
        ('custom', 'Özel'),
    ]
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Etiket Adı'
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name='Slug'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='Açıklama'
    )
    tag_type = models.CharField(
        max_length=20,
        choices=TAG_TYPE_CHOICES,
        default='custom',
        verbose_name='Etiket Tipi'
    )
    color = models.CharField(
        max_length=7,
        default='#007bff',
        verbose_name='Renk'
    )
    usage_count = models.IntegerField(
        default=0,
        verbose_name='Kullanım Sayısı'
    )
    
    class Meta:
        db_table = 'sapbot_document_tags'
        verbose_name = 'Döküman Etiketi'
        verbose_name_plural = 'Döküman Etiketleri'
        indexes = [
            models.Index(fields=['tag_type']),
            models.Index(fields=['usage_count']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Slug otomatik oluştur"""
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class DocumentChunkRelation(BaseModel):
    """Döküman chunk'ları arası ilişki modeli"""
    
    RELATION_TYPE_CHOICES = [
        ('follows', 'Takip Eder'),
        ('references', 'Referans Verir'),
        ('contradicts', 'Çelişir'),
        ('supports', 'Destekler'),
        ('updates', 'Günceller'),
    ]
    
    source_chunk = models.ForeignKey(
        KnowledgeChunk,
        on_delete=models.CASCADE,
        related_name='outgoing_relations',
        verbose_name='Kaynak Chunk'
    )
    target_chunk = models.ForeignKey(
        KnowledgeChunk,
        on_delete=models.CASCADE,
        related_name='incoming_relations',
        verbose_name='Hedef Chunk'
    )
    relation_type = models.CharField(
        max_length=20,
        choices=RELATION_TYPE_CHOICES,
        verbose_name='İlişki Tipi'
    )
    confidence = models.FloatField(
        default=1.0,
        verbose_name='Güven Değeri'
    )
    auto_generated = models.BooleanField(
        default=True,
        verbose_name='Otomatik Oluşturuldu mu?'
    )
    
    class Meta:
        db_table = 'sapbot_document_chunk_relations'
        verbose_name = 'Chunk İlişkisi'
        verbose_name_plural = 'Chunk İlişkileri'
        unique_together = ['source_chunk', 'target_chunk', 'relation_type']
    
    def __str__(self):
        return f"{self.source_chunk.id} -> {self.target_chunk.id} ({self.relation_type})"