# backend/sapbot_api/utils/file_handlers.py
"""
SAPBot API File Handlers

Bu modül dosya işleme, doğrulama ve güvenlik fonksiyonlarını içerir.
PDF, video ve diğer dosya türleri için specialized handler'lar.
"""

import os
import hashlib
import mimetypes
import magic
import uuid
from typing import Dict, List, Any
from pathlib import Path
from datetime import datetime
import logging

# PDF işleme
import PyPDF2
import pdfplumber
from PIL import Image

# Video işleme
import cv2
import whisper
import ffmpeg
import subprocess

# Dosya güvenliği
import yara
from django.core.files.uploadedfile import UploadedFile
from django.core.files.storage import default_storage
from django.conf import settings

from .exceptions import (
    FileUploadError,
    DocumentProcessingError,
    ValidationException,
    ConfigurationError
)

logger = logging.getLogger(__name__)


class FileValidator:
    """Dosya doğrulama ve güvenlik kontrolleri"""
    
    ALLOWED_EXTENSIONS = {
        'pdf': ['.pdf'],
        'video': ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.m4v'],
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
        'document': ['.doc', '.docx', '.txt', '.rtf'],
        'audio': ['.mp3', '.wav', '.m4a', '.ogg']
    }
    
    ALLOWED_MIMETYPES = {
        'pdf': ['application/pdf'],
        'video': [
            'video/mp4', 'video/avi', 'video/quicktime', 
            'video/x-msvideo', 'video/webm', 'video/x-matroska'
        ],
        'image': [
            'image/jpeg', 'image/png', 'image/gif', 
            'image/bmp', 'image/tiff'
        ],
        'document': [
            'application/msword', 
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain', 'application/rtf'
        ],
        'audio': [
            'audio/mpeg', 'audio/wav', 'audio/x-m4a', 'audio/ogg'
        ]
    }
    
    MAX_FILE_SIZES = {
        'pdf': 100 * 1024 * 1024,      # 100MB
        'video': 500 * 1024 * 1024,    # 500MB
        'image': 10 * 1024 * 1024,     # 10MB
        'document': 50 * 1024 * 1024,  # 50MB
        'audio': 100 * 1024 * 1024     # 100MB
    }
    
    def __init__(self):
        self.magic_instance = magic.Magic(mime=True)
    
    def validate_file(self, file: UploadedFile) -> Dict[str, Any]:
        """Dosya doğrulama ana fonksiyonu"""
        try:
            # Temel validasyonlar
            file_info = self._get_file_info(file)
            
            # Dosya boyutu kontrolü
            self._validate_file_size(file, file_info['type'])
            
            # Dosya tipi kontrolü
            self._validate_file_type(file, file_info)
            
            # Dosya içeriği kontrolü
            self._validate_file_content(file, file_info['type'])
            
            # Güvenlik kontrolü
            self._security_scan(file)
            
            return {
                'valid': True,
                'file_info': file_info,
                'message': 'Dosya doğrulandı'
            }
            
        except Exception as e:
            logger.error(f"Dosya doğrulama hatası: {e}")
            return {
                'valid': False,
                'error': str(e),
                'message': 'Dosya doğrulama başarısız'
            }
    
    def _get_file_info(self, file: UploadedFile) -> Dict[str, Any]:
        """Dosya bilgilerini al"""
        file_extension = Path(file.name).suffix.lower()
        
        # MIME type tespiti
        file.seek(0)
        mime_type = self.magic_instance.from_buffer(file.read(2048))
        file.seek(0)
        
        # Dosya tipini belirle
        file_type = self._determine_file_type(file_extension, mime_type)
        
        return {
            'name': file.name,
            'size': file.size,
            'extension': file_extension,
            'mime_type': mime_type,
            'type': file_type,
            'hash': self._calculate_file_hash(file)
        }
    
    def _determine_file_type(self, extension: str, mime_type: str) -> str:
        """Dosya tipini belirle"""
        for file_type, extensions in self.ALLOWED_EXTENSIONS.items():
            if extension in extensions:
                # MIME type kontrolü
                if mime_type in self.ALLOWED_MIMETYPES.get(file_type, []):
                    return file_type
        
        raise ValidationException(
            message=f"Desteklenmeyen dosya tipi: {extension}",
            field="file_type",
            value=extension
        )
    
    def _validate_file_size(self, file: UploadedFile, file_type: str):
        """Dosya boyutu kontrolü"""
        max_size = self.MAX_FILE_SIZES.get(file_type, 50 * 1024 * 1024)
        
        if file.size > max_size:
            raise FileUploadError(
                message=f"Dosya boyutu çok büyük. Maksimum: {max_size // (1024*1024)}MB",
                file_name=file.name,
                file_size=file.size,
                max_size=max_size
            )
    
    def _validate_file_type(self, file: UploadedFile, file_info: Dict):
        """Dosya tipi kontrolü"""
        file_type = file_info['type']
        mime_type = file_info['mime_type']
        
        allowed_mimes = self.ALLOWED_MIMETYPES.get(file_type, [])
        
        if mime_type not in allowed_mimes:
            raise ValidationException(
                message=f"Geçersiz MIME type: {mime_type}",
                field="mime_type",
                value=mime_type
            )
    
    def _validate_file_content(self, file: UploadedFile, file_type: str):
        """Dosya içeriği kontrolü"""
        file.seek(0)
        
        if file_type == 'pdf':
            self._validate_pdf_content(file)
        elif file_type == 'video':
            self._validate_video_content(file)
        elif file_type == 'image':
            self._validate_image_content(file)
        
        file.seek(0)
    
    def _validate_pdf_content(self, file: UploadedFile):
        """PDF içeriği kontrolü"""
        try:
            reader = PyPDF2.PdfReader(file)
            
            # PDF şifreli mi?
            if reader.is_encrypted:
                raise ValidationException(
                    message="Şifreli PDF dosyaları desteklenmemektedir",
                    field="pdf_encrypted"
                )
            
            # Sayfa sayısı kontrolü
            if len(reader.pages) > 2000:
                raise ValidationException(
                    message="PDF dosyası çok fazla sayfa içeriyor (max: 2000)",
                    field="pdf_pages",
                    value=len(reader.pages)
                )
            
            # En az bir sayfa okunabilir metin içermeli
            has_text = False
            for page in reader.pages[:5]:  # İlk 5 sayfayı kontrol et
                if page.extract_text().strip():
                    has_text = True
                    break
            
            if not has_text:
                logger.warning(f"PDF dosyasında okunabilir metin bulunamadı: {file.name}")
                
        except Exception as e:
            raise DocumentProcessingError(
                message=f"PDF doğrulama hatası: {str(e)}",
                processing_stage="validation"
            )
    
    def _validate_video_content(self, file: UploadedFile):
        """Video içeriği kontrolü"""
        try:
            # Geçici dosya oluştur
            temp_path = self._create_temp_file(file)
            
            # Video bilgilerini al
            cap = cv2.VideoCapture(temp_path)
            
            if not cap.isOpened():
                raise ValidationException(
                    message="Video dosyası açılamadı",
                    field="video_corrupted"
                )
            
            # Video süresi kontrolü
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            duration = frame_count / fps if fps > 0 else 0
            
            if duration > 7200:  # 2 saat
                raise ValidationException(
                    message="Video süresi çok uzun (max: 2 saat)",
                    field="video_duration",
                    value=duration
                )
            
            cap.release()
            os.unlink(temp_path)
            
        except Exception as e:
            raise DocumentProcessingError(
                message=f"Video doğrulama hatası: {str(e)}",
                processing_stage="validation"
            )
    
    def _validate_image_content(self, file: UploadedFile):
        """Resim içeriği kontrolü"""
        try:
            image = Image.open(file)
            
            # Resim boyutu kontrolü
            width, height = image.size
            if width > 10000 or height > 10000:
                raise ValidationException(
                    message="Resim boyutu çok büyük (max: 10000x10000)",
                    field="image_dimensions",
                    value=f"{width}x{height}"
                )
            
            # Resim formatı kontrolü
            if image.format not in ['JPEG', 'PNG', 'GIF', 'BMP', 'TIFF']:
                raise ValidationException(
                    message=f"Desteklenmeyen resim formatı: {image.format}",
                    field="image_format",
                    value=image.format
                )
            
        except Exception as e:
            raise DocumentProcessingError(
                message=f"Resim doğrulama hatası: {str(e)}",
                processing_stage="validation"
            )
    
    def _security_scan(self, file: UploadedFile):
        """Güvenlik taraması"""
        try:
            # Dosya başlığı kontrolü
            file.seek(0)
            header = file.read(512)
            
            # Zararlı pattern'lar
            malicious_patterns = [
                b'<script',
                b'javascript:',
                b'vbscript:',
                b'onload=',
                b'onerror=',
                b'<?php',
                b'<%',
                b'exec(',
                b'system(',
                b'shell_exec'
            ]
            
            for pattern in malicious_patterns:
                if pattern in header:
                    raise ValidationException(
                        message="Dosya güvenlik taramasından geçemedi",
                        field="security_scan"
                    )
            
            file.seek(0)
            
        except Exception as e:
            logger.error(f"Güvenlik taraması hatası: {e}")
            raise
    
    def _calculate_file_hash(self, file: UploadedFile) -> str:
        """Dosya hash'i hesapla"""
        file.seek(0)
        hash_sha256 = hashlib.sha256()
        
        for chunk in iter(lambda: file.read(8192), b""):
            hash_sha256.update(chunk)
        
        file.seek(0)
        return hash_sha256.hexdigest()
    
    def _create_temp_file(self, file: UploadedFile) -> str:
        """Geçici dosya oluştur"""
        temp_dir = getattr(settings, 'TEMP_DIR', '/tmp')
        os.makedirs(temp_dir, exist_ok=True)
        
        temp_filename = f"{uuid.uuid4()}{Path(file.name).suffix}"
        temp_path = os.path.join(temp_dir, temp_filename)
        
        with open(temp_path, 'wb') as temp_file:
            file.seek(0)
            for chunk in file.chunks():
                temp_file.write(chunk)
        
        return temp_path


class PDFProcessor:
    """PDF işleme sınıfı"""
    
    def __init__(self):
        self.validator = FileValidator()
    
    def extract_text(self, file_path: str) -> Dict[str, Any]:
        """PDF'den metin çıkarma"""
        try:
            text_content = []
            metadata = {}
            
            # PyPDF2 ile temel çıkarma
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Metadata
                metadata = {
                    'page_count': len(pdf_reader.pages),
                    'title': pdf_reader.metadata.get('/Title', ''),
                    'author': pdf_reader.metadata.get('/Author', ''),
                    'subject': pdf_reader.metadata.get('/Subject', ''),
                    'creator': pdf_reader.metadata.get('/Creator', ''),
                    'producer': pdf_reader.metadata.get('/Producer', ''),
                    'creation_date': pdf_reader.metadata.get('/CreationDate', '')
                }
                
                # Sayfa sayfa metin çıkar
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    page_text = page.extract_text()
                    
                    if page_text.strip():
                        text_content.append({
                            'page_number': page_num,
                            'text': self._clean_text(page_text),
                            'char_count': len(page_text)
                        })
            
            # pdfplumber ile gelişmiş çıkarma (tablo vs.)
            enhanced_content = self._extract_with_pdfplumber(file_path)
            
            return {
                'text_content': text_content,
                'enhanced_content': enhanced_content,
                'metadata': metadata,
                'total_pages': len(text_content),
                'total_characters': sum(page['char_count'] for page in text_content)
            }
            
        except Exception as e:
            logger.error(f"PDF metin çıkarma hatası: {e}")
            raise DocumentProcessingError(
                message=f"PDF metin çıkarma hatası: {str(e)}",
                processing_stage="text_extraction"
            )
    
    def _extract_with_pdfplumber(self, file_path: str) -> List[Dict]:
        """pdfplumber ile gelişmiş çıkarma"""
        try:
            enhanced_content = []
            
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    page_data = {
                        'page_number': page_num,
                        'text': page.extract_text() or '',
                        'tables': [],
                        'images': []
                    }
                    
                    # Tabloları çıkar
                    tables = page.extract_tables()
                    for table in tables:
                        if table:
                            page_data['tables'].append({
                                'data': table,
                                'text_representation': self._table_to_text(table)
                            })
                    
                    # Resim bilgilerini al
                    if hasattr(page, 'images'):
                        page_data['images'] = [
                            {
                                'bbox': img.get('bbox', []),
                                'width': img.get('width', 0),
                                'height': img.get('height', 0)
                            }
                            for img in page.images
                        ]
                    
                    enhanced_content.append(page_data)
            
            return enhanced_content
            
        except Exception as e:
            logger.warning(f"pdfplumber çıkarma hatası: {e}")
            return []
    
    def _table_to_text(self, table: List[List]) -> str:
        """Tabloyu metin formatına çevir"""
        try:
            text_lines = []
            for row in table:
                if row:
                    cleaned_row = [str(cell).strip() if cell else '' for cell in row]
                    text_lines.append(' | '.join(cleaned_row))
            return '\n'.join(text_lines)
        except:
            return ''
    
    def _clean_text(self, text: str) -> str:
        """Metin temizleme"""
        # Gereksiz boşlukları temizle
        text = ' '.join(text.split())
        
        # Özel karakterleri düzelt
        replacements = {
            'ð': 'ğ', 'Ð': 'Ğ', 'ý': 'ı', 'Ý': 'İ',
            'þ': 'ş', 'Þ': 'Ş', 'ç': 'ç', 'Ç': 'Ç',
            'ü': 'ü', 'Ü': 'Ü', 'ö': 'ö', 'Ö': 'Ö'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def extract_images_with_ocr(self, file_path: str) -> List[Dict]:
        """PDF'den resim çıkarma ve OCR"""
        try:
            images_text = []
            
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    if hasattr(page, 'images'):
                        for img_idx, img in enumerate(page.images):
                            try:
                                # OCR ile metin çıkar
                                # Bu kısım implementation'a göre değişebilir
                                ocr_text = "OCR implementation needed"
                                
                                if ocr_text.strip():
                                    images_text.append({
                                        'page_number': page_num,
                                        'image_index': img_idx,
                                        'text': ocr_text,
                                        'bbox': img.get('bbox', [])
                                    })
                            except Exception as e:
                                logger.warning(f"OCR hatası: {e}")
                                continue
            
            return images_text
            
        except Exception as e:
            logger.error(f"PDF resim çıkarma hatası: {e}")
            return []


class VideoProcessor:
    """Video işleme sınıfı"""
    
    def __init__(self):
        self.validator = FileValidator()
        self.whisper_model = None
    
    def extract_transcript(self, file_path: str) -> Dict[str, Any]:
        """Video'dan transkript çıkarma"""
        try:
            # Whisper modelini yükle
            if self.whisper_model is None:
                self.whisper_model = whisper.load_model("base")
            
            # Video bilgilerini al
            video_info = self._get_video_info(file_path)
            
            # Ses çıkarma
            audio_path = self._extract_audio(file_path)
            
            # Transkript oluştur
            result = self.whisper_model.transcribe(
                audio_path,
                language="tr",
                task="transcribe"
            )
            
            # Segmentleri işle
            segments = []
            for segment in result["segments"]:
                segments.append({
                    'start': segment["start"],
                    'end': segment["end"],
                    'text': segment["text"].strip(),
                    'confidence': segment.get("avg_logprob", 0)
                })
            
            # Geçici dosyayı sil
            os.unlink(audio_path)
            
            return {
                'video_info': video_info,
                'full_text': result["text"],
                'segments': segments,
                'language': result.get("language", "tr"),
                'duration': video_info['duration']
            }
            
        except Exception as e:
            logger.error(f"Video transkript çıkarma hatası: {e}")
            raise DocumentProcessingError(
                message=f"Video transkript çıkarma hatası: {str(e)}",
                processing_stage="transcript_extraction"
            )
    
    def _get_video_info(self, file_path: str) -> Dict[str, Any]:
        """Video bilgilerini al"""
        try:
            cap = cv2.VideoCapture(file_path)
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            cap.release()
            
            return {
                'fps': fps,
                'frame_count': frame_count,
                'width': width,
                'height': height,
                'duration': duration,
                'resolution': f"{width}x{height}"
            }
            
        except Exception as e:
            logger.error(f"Video bilgi alma hatası: {e}")
            return {}
    
    def _extract_audio(self, video_path: str) -> str:
        """Video'dan ses çıkar - FFmpeg kullanarak"""
        try:
            # Geçici ses dosyası
            temp_dir = getattr(settings, 'TEMP_DIR', '/tmp')
            audio_path = os.path.join(temp_dir, f"{uuid.uuid4()}.wav")
            
            # FFmpeg ile ses çıkar (2 farklı yöntem)
            try:
                # Yöntem 1: ffmpeg-python kütüphanesi
                (
                    ffmpeg
                    .input(video_path)
                    .output(audio_path, acodec='pcm_s16le', ac=1, ar='16000')
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True)
                )
            except Exception as e:
                logger.warning(f"ffmpeg-python hatası, subprocess deneniyor: {e}")
                
                # Yöntem 2: Doğrudan subprocess ile ffmpeg
                cmd = [
                    'ffmpeg', '-i', video_path, 
                    '-acodec', 'pcm_s16le', 
                    '-ac', '1', 
                    '-ar', '16000', 
                    '-y',  # overwrite
                    audio_path
                ]
                
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=300  # 5 dakika timeout
                )
                
                if result.returncode != 0:
                    raise Exception(f"FFmpeg hatası: {result.stderr}")
            
            # Dosyanın oluştuğunu kontrol et
            if not os.path.exists(audio_path):
                raise Exception("Ses dosyası oluşturulamadı")
            
            return audio_path
            
        except Exception as e:
            logger.error(f"Ses çıkarma hatası: {e}")
            raise DocumentProcessingError(
                message=f"Video ses çıkarma hatası: {str(e)}",
                processing_stage="audio_extraction"
            )


class FileManager:
    """Dosya yönetimi sınıfı"""
    
    def __init__(self):
        self.validator = FileValidator()
        self.pdf_processor = PDFProcessor()
        self.video_processor = VideoProcessor()
    
    def save_uploaded_file(self, file: UploadedFile, folder: str = "documents") -> Dict[str, Any]:
        """Yüklenen dosyayı kaydet"""
        try:
            # Dosya doğrulaması
            validation_result = self.validator.validate_file(file)
            if not validation_result['valid']:
                raise FileUploadError(
                    message=validation_result['message'],
                    file_name=file.name
                )
            
            # Dosya yolunu oluştur
            file_info = validation_result['file_info']
            file_path = self._generate_file_path(file_info, folder)
            
            # Dosyayı kaydet
            saved_path = default_storage.save(file_path, file)
            
            return {
                'saved_path': saved_path,
                'file_info': file_info,
                'storage_url': default_storage.url(saved_path)
            }
            
        except Exception as e:
            logger.error(f"Dosya kaydetme hatası: {e}")
            raise FileUploadError(
                message=f"Dosya kaydetme hatası: {str(e)}",
                file_name=file.name
            )
    
    def _generate_file_path(self, file_info: Dict, folder: str) -> str:
        """Dosya yolu oluştur"""
        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        day = now.strftime("%d")
        
        # Unique filename
        filename = f"{uuid.uuid4()}{file_info['extension']}"
        
        return f"sapbot_api/{folder}/{year}/{month}/{day}/{filename}"
    
    def delete_file(self, file_path: str) -> bool:
        """Dosyayı sil"""
        try:
            if default_storage.exists(file_path):
                default_storage.delete(file_path)
                return True
            return False
        except Exception as e:
            logger.error(f"Dosya silme hatası: {e}")
            return False
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Dosya bilgilerini al"""
        try:
            if not default_storage.exists(file_path):
                return {'exists': False}
            
            file_size = default_storage.size(file_path)
            file_url = default_storage.url(file_path)
            
            return {
                'exists': True,
                'size': file_size,
                'url': file_url,
                'path': file_path
            }
            
        except Exception as e:
            logger.error(f"Dosya bilgi alma hatası: {e}")
            return {'exists': False, 'error': str(e)}


# Utility functions
def validate_file_type(file: UploadedFile) -> Dict[str, Any]:
    """Dosya tipi doğrulama"""
    validator = FileValidator()
    return validator.validate_file(file)


def get_file_hash(file: UploadedFile) -> str:
    """Dosya hash'i al"""
    validator = FileValidator()
    return validator._calculate_file_hash(file)


def extract_pdf_text(file_path: str) -> Dict[str, Any]:
    """PDF'den metin çıkar"""
    processor = PDFProcessor()
    return processor.extract_text(file_path)


def extract_video_transcript(file_path: str) -> Dict[str, Any]:
    """Video'dan transkript çıkar"""
    processor = VideoProcessor()
    return processor.extract_transcript(file_path)


def clean_temp_files():
    """Geçici dosyaları temizle"""
    try:
        temp_dir = getattr(settings, 'TEMP_DIR', '/tmp')
        if os.path.exists(temp_dir):
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                if os.path.isfile(file_path):
                    # 1 saatten eski dosyaları sil
                    if os.path.getctime(file_path) < (datetime.now().timestamp() - 3600):
                        os.unlink(file_path)
        return True
    except Exception as e:
        logger.error(f"Geçici dosya temizleme hatası: {e}")
        return False