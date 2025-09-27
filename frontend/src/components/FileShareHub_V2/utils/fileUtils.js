// frontend/src/components/FileShareHub_V2/utils/fileUtils.js
// Kurumsal ikon seti – lucide-react ile genişletilmiş uzantı desteği

import {
  File as FileIcon,
  FileText,
  FileImage,
  FileArchive,
  FileAudio,
  FileVideo,
  Folder,
  PenTool,
  Brush,
  Box,
  Ruler,
} from "lucide-react";

import { isImageFile } from "../validators/fileRules";

// Sabitler için modüler uzantı grupları
const EXTENSION_GROUPS = {
  office: {
    pdf: { icon: FileText, className: "text-red-600" },
    doc: { icon: FileText, className: "text-blue-600" },
    docx: { icon: FileText, className: "text-blue-600" },
    xls: { icon: FileText, className: "text-green-600" },
    xlsx: { icon: FileText, className: "text-green-600" },
    ppt: { icon: FileText, className: "text-orange-600" },
    pptx: { icon: FileText, className: "text-orange-600" },
    txt: { icon: FileText },
    csv: { icon: FileText, className: "text-green-600" },
  },
  archive: {
    zip: { icon: FileArchive },
    rar: { icon: FileArchive },
    "7z": { icon: FileArchive },
  },
  audio: {
    mp3: { icon: FileAudio },
    wav: { icon: FileAudio },
    flac: { icon: FileAudio },
  },
  video: {
    mp4: { icon: FileVideo },
    mov: { icon: FileVideo },
    avi: { icon: FileVideo },
  },
  image: {
    jpg: { icon: FileImage, className: "text-teal-600" },
    jpeg: { icon: FileImage, className: "text-teal-600" },
    png: { icon: FileImage, className: "text-teal-600" },
    gif: { icon: FileImage, className: "text-teal-600" },
    webp: { icon: FileImage, className: "text-teal-600" },
    tif: { icon: FileImage, className: "text-teal-600" }, // TIFF eklendi
    tiff: { icon: FileImage, className: "text-teal-600" }, // TIFF eklendi
    svg: { icon: PenTool, className: "text-purple-600" },
    ai: { icon: PenTool, className: "text-purple-600" },
    eps: { icon: PenTool, className: "text-purple-600" },
    psd: { icon: Brush, className: "text-indigo-600" },
  },
  cad: {
    dwg: { icon: Ruler, className: "text-blue-500" },
    dxf: { icon: Ruler, className: "text-blue-500" },
    step: { icon: Ruler, className: "text-blue-500" },
    stp: { icon: Ruler, className: "text-blue-500" },
    igs: { icon: Ruler, className: "text-blue-500" },
    iges: { icon: Ruler, className: "text-blue-500" },
  },
  model3d: {
    stl: { icon: Box, className: "text-amber-600" },
    obj: { icon: Box, className: "text-amber-600" },
    max: { icon: Box, className: "text-amber-600" },
    "3ds": { icon: Box, className: "text-amber-600" },
    fbx: { icon: Box, className: "text-amber-600" },
    skp: { icon: Box, className: "text-amber-600" },
    glb: { icon: Box, className: "text-amber-600" },
    gltf: { icon: Box, className: "text-amber-600" },
  },
};

/**
 * Byte sayısını insan-okur formata çevirir.
 * @param {number} bytes - Dosya boyutu (byte cinsinden)
 * @returns {string} - Formatlanmış boyut (örn. "1.23 MB")
 */
export function formatFileSize(bytes) {
  if (!bytes || bytes <= 0) return "0 B";
  const units = ["B", "KB", "MB", "GB", "TB"];
  const idx = Math.min(
    Math.floor(Math.log(bytes) / Math.log(1024)),
    units.length - 1
  );
  const size = (bytes / Math.pow(1024, idx)).toFixed(2);
  return `${parseFloat(size)} ${units[idx]}`;
}

/**
 * Dosya veya klasör için JSX ikonu döndürür.
 * @param {string} ext - Dosya uzantısı (klasör için boş veya null)
 * @param {boolean} isDir - Dosyanın klasör olup olmadığı
 * @param {object} props - İkon için ek props (size, className vb.)
 * @returns {JSX.Element} - İlgili ikon bileşeni
 */
export function getFileIconByExtension(ext, isDir, props = {}) {
  if (isDir) {
    return <Folder {...props} className={`text-yellow-500 ${props.className || ""}`} />;
  }

  const normalizedExt = ext?.toLowerCase().replace(/^\./, "") || "";
  let IconComponent = FileIcon;
  let iconProps = { ...props };

  for (const group of Object.values(EXTENSION_GROUPS)) {
    if (group[normalizedExt]) {
      IconComponent = group[normalizedExt].icon;
      iconProps = { ...props, className: group[normalizedExt].className || props.className };
      break;
    }
  }

  return <IconComponent {...iconProps} />;
}

/**
 * Dosya tipini belirler (klasör, görsel veya dosya).
 * @param {object} file - Dosya objesi (name ve is_dir içerir)
 * @returns {string} - Dosya tipi ("folder", "image", "file")
 */
export function getFileType(file) {
  if (!file) return "file";
  if (file.is_dir) return "folder";
  if (isImageFile(file.name)) return "image";
  return "file";
}

/**
 * Dosya yolundan dosya adını çıkarır.
 * @param {string} path - Dosya yolu
 * @returns {string} - Dosya adı veya boş string
 */
export function extractFileNameFromPath(path) {
  return path?.split("/").filter(Boolean).pop() ?? "";
}

export function getFileExtension(name) {
  const parts = name.split(".");
  return parts.length > 1 ? parts.pop().toLowerCase() : "";
}
