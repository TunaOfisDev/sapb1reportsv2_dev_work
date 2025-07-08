// frontend/src/components/FileShareHub_V2/validators/fileRules.js
// İstemci tarafı dosya kuralları – backend "rules.py" ile uyumlu

// Genel limitler
const MIN_FILE_SIZE = 0.0001 * 1024 * 1024; // 0.0001 MB ≈ 100 B
const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50 MB (her tür dosya için)
const MAX_IMAGE_SIZE = 25 * 1024 * 1024; // 25 MB (thumbnail için)

// Gizli dosya isimleri
const HIDDEN_FILE_NAMES = [
  ".DS_Store",
  "Thumbs.db",
  ".lnk",
  ".Trash-1000",
  ".ini",
  ".tmp",
  ".bak",
];

/**
 * Dosya boyutunun geçerli olup olmadığını kontrol eder.
 * @param {number} size - Dosya boyutu (byte cinsinden)
 * @returns {boolean} - Geçerliyse true, değilse false
 */
export function isValidFileSize(size) {
  if (typeof size !== "number" || size < 0) return false;
  return size >= MIN_FILE_SIZE && size <= MAX_FILE_SIZE;
}

/**
 * Görsel dosya boyutunun thumbnail için geçerli olup olmadığını kontrol eder.
 * @param {number} size - Dosya boyutu (byte cinsinden)
 * @returns {boolean} - Geçerliyse true, değilse false
 */
export function isValidImageSize(size) {
  if (typeof size !== "number" || size < 0) return false;
  return size <= MAX_IMAGE_SIZE;
}

/**
 * Thumbnail üretiminin atlanıp atlanmayacağını kontrol eder.
 * @param {object} file - Dosya objesi (is_image ve size içerir)
 * @returns {boolean} - Thumbnail atlanacaksa true
 */
export function shouldSkipThumbnail(file) {
  if (!file || typeof file !== "object") return true;
  return !file.is_image || !isValidImageSize(file.size);
}

/**
 * Dosyanın gizlenip gizlenmeyeceğini kontrol eder.
 * @param {string} name - Dosya adı
 * @returns {boolean} - Gizlenmeli ise true
 */
export function shouldHideFile(name) {
  if (!name || typeof name !== "string") return true;
  return HIDDEN_FILE_NAMES.some(
    (hidden) =>
      name.toLowerCase().endsWith(hidden.toLowerCase()) ||
      name.toLowerCase() === hidden.toLowerCase()
  );
}

/**
 * Dosya adından uzantıyı çıkarır.
 * @param {string} fileName - Dosya adı
 * @returns {string} - Dosya uzantısı (küçük harf) veya boş string
 */
export function getFileExtension(fileName) {
  if (!fileName || typeof fileName !== "string") return "";
  const parts = fileName.split(".");
  return parts.length > 1 ? parts.pop().toLowerCase() : "";
}

/**
 * Dosyanın bir görsel olup olmadığını kontrol eder.
 * @param {string} fileName - Dosya adı
 * @returns {boolean} - Görsel dosya ise true
 */
export function isImageFile(fileName) {
  const imageExtensions = ["jpg", "jpeg", "png", "gif", "bmp", "webp"];
  return imageExtensions.includes(getFileExtension(fileName));
}

/**
 * Thumbnail durumunu belirler (UI kararları için).
 * @param {object} file - Dosya objesi (name ve is_dir içerir)
 * @returns {string} - Durum: 'hidden', 'skip' veya 'ok'
 */
export function getThumbnailStatus(file) {
  if (!file || typeof file !== "object") return "hidden";
  if (shouldHideFile(file.name)) return "hidden";
  if (shouldSkipThumbnail(file)) return "skip";
  return "ok";
}