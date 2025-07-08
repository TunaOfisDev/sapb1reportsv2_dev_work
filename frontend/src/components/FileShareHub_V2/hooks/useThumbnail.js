// frontend/src/components/FileShareHub_V2/hooks/useThumbnail.js
import { useEffect, useRef, useState } from "react";
import { fetchThumbnail } from "../api/fileApi";
import { getFileExtension } from "../validators/fileRules";

/**
 * Thumbnail çekme hook'u – exponential back-off ile retry mekanizması.
 * @param {number} fileId - SHA-1 tabanlı file_id
 * @param {boolean} isImage - Dosya gerçekten görsel mi?
 * @param {string} fileName - Dosya adı (TIFF kontrolü için)
 * @param {number} maxRetries - Kaç kez yeniden denesin (varsayılan 5)
 * @param {number} baseDelay - İlk bekleme süresi (ms) (varsayılan 2000)
 */
export default function useThumbnail(
  fileId,
  isImage,
  fileName,
  maxRetries = 5,
  baseDelay = 2000
) {
  const [url, setUrl] = useState(null);
  const [loading, setLoading] = useState(isImage);
  const [error, setError] = useState(null);

  const retryRef = useRef(0);
  const timerRef = useRef(null);

  useEffect(() => {
    // TIFF dosyaları için thumbnail üretilmeyecek
    const ext = getFileExtension(fileName);
    const isTiff = ["tif", "tiff"].includes(ext.toLowerCase());

    if (!fileId || !isImage || isTiff) {
      setUrl(null);
      setError(null);
      setLoading(false);
      return;
    }

    let cancelled = false;

    const tryFetch = async (attempt = 1) => {
      try {
        const blob = await fetchThumbnail(fileId, { responseType: "blob" });
        if (cancelled) return;

        const objectUrl = URL.createObjectURL(blob);
        setUrl(objectUrl);
        setLoading(false);
        setError(null);
      } catch (err) {
        if (cancelled) return;
        if (attempt >= maxRetries) {
          setError(err.message || "Thumbnail yüklenemedi");
          setLoading(false);
          return;
        }
        // Yalnızca "Thumbnail üretiliyor" mesajı için yeniden dene
        if (err.message.includes("Thumbnail üretiliyor")) {
          retryRef.current = attempt;
          const delay = baseDelay * Math.pow(1.5, attempt - 1);
          timerRef.current = setTimeout(() => tryFetch(attempt + 1), delay);
        } else {
          setError(err.message || "Thumbnail yüklenemedi");
          setLoading(false);
        }
      }
    };

    setLoading(true);
    tryFetch();

    return () => {
      cancelled = true;
      if (timerRef.current) clearTimeout(timerRef.current);
      if (url) URL.revokeObjectURL(url);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fileId, isImage, fileName, maxRetries, baseDelay]);

  return { url, loading, error, retryCount: retryRef.current };
}