// frontend/src/components/FileShareHub/utils/thumbnail.js
import { FaFilePdf, FaFileWord, FaFileExcel, FaFilePowerpoint, FaFileImage, FaFileArchive, FaFileAlt, FaFileVideo, FaFileAudio, FaFile, FaFolder } from 'react-icons/fa';

// Desteklenen dosya uzantıları
const IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tif', 'tiff', 'webp'];
const PDF_EXTENSIONS = ['pdf'];
const WORD_EXTENSIONS = ['doc', 'docx'];
const EXCEL_EXTENSIONS = ['xls', 'xlsx'];
const POWERPOINT_EXTENSIONS = ['ppt', 'pptx'];
const ARCHIVE_EXTENSIONS = ['zip', 'rar', '7z'];
const VIDEO_EXTENSIONS = ['mp4', 'avi', 'mkv', 'mov'];
const AUDIO_EXTENSIONS = ['mp3', 'wav', 'ogg'];
const DWG_EXTENSIONS = ['dwg'];

export const getThumbnailOrIcon = (fileName) => {
  const fileExtension = fileName.split('.').pop().toLowerCase();

  // Görsel dosyaları için küçük önizleme (thumbnail)
  if (IMAGE_EXTENSIONS.includes(fileExtension)) {
    return <FaFileImage size={40} />; // Görsel dosyaları için genel ikon
  }

  // PDF dosyaları
  if (PDF_EXTENSIONS.includes(fileExtension)) {
    return <FaFilePdf size={40} color="#E53E3E" />;
  }

  // Word dosyaları
  if (WORD_EXTENSIONS.includes(fileExtension)) {
    return <FaFileWord size={40} color="#2B6CB0" />;
  }

  // Excel dosyaları
  if (EXCEL_EXTENSIONS.includes(fileExtension)) {
    return <FaFileExcel size={40} color="#2F855A" />;
  }

  // PowerPoint dosyaları
  if (POWERPOINT_EXTENSIONS.includes(fileExtension)) {
    return <FaFilePowerpoint size={40} color="#D69E2E" />;
  }

  // Arşiv dosyaları (zip, rar, vb.)
  if (ARCHIVE_EXTENSIONS.includes(fileExtension)) {
    return <FaFileArchive size={40} color="#DD6B20" />;
  }

  // Video dosyaları
  if (VIDEO_EXTENSIONS.includes(fileExtension)) {
    return <FaFileVideo size={40} color="#805AD5" />;
  }

  // Ses dosyaları
  if (AUDIO_EXTENSIONS.includes(fileExtension)) {
    return <FaFileAudio size={40} color="#ED64A6" />;
  }

  // DWG dosyaları (mimari çizimler için)
  if (DWG_EXTENSIONS.includes(fileExtension)) {
    return <FaFile size={40} color="#718096" />;
  }

  // Genel metin dosyaları
  if (fileExtension === 'txt') {
    return <FaFileAlt size={40} color="#A0AEC0" />;
  }

  // Klasörler
  if (!fileExtension) {
    return <FaFolder size={40} color="#ECC94B" />;
  }

  // Diğer dosya türleri için genel ikon
  return <FaFile size={40} color="#718096" />;
};

export default getThumbnailOrIcon;