// frontend/src/features/FileShareHubV2/api/fileApi.js
import axios from "../../../api/axiosconfig";

/**
 * 🔍 Dizin içeriğini getirir
 * @param {string} path
 * @param {number} page
 * @param {number} pageSize
 */
export const fetchFileList = async (path = "", page = 1, pageSize = 50) => {
  try {
    const res = await axios.get("filesharehub-v2/files/", {
      params: { path, page, page_size: pageSize },
    });
    return res.data;
  } catch (err) {
    console.error("fetchFileList error:", err);
    return { directories: [], files: [] };
  }
};





/**
 * 🖼 Thumbnail getir – 202 dönerse retry tetiklenir
 * @param {number} fileId - Dosya ID'si
 * @param {object} options - Opsiyonel ayarlar
 * @param {string} options.responseType - Yanıt tipi (varsayılan: "blob")
 * @param {number} options.maxRetries - Maksimum tekrar deneme sayısı (varsayılan: 10)
 * @param {number} options.retryDelay - Tekrar deneme gecikmesi (ms, varsayılan: 20000)
 * @returns {Promise<Blob>} Thumbnail blob nesnesi
 */
export const fetchThumbnail = async (
  fileId,
  {
    responseType = "blob",
    maxRetries = 15,
    retryDelay = 30000,  // 30 saniye, backend'in retry_after ile uyumlu
  } = {}
) => {
  const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  let attempt = 0;

  while (attempt < maxRetries) {
    try {
      const res = await axios.get(`filesharehub-v2/thumb/${fileId}/`, {
        responseType,
        validateStatus: (status) => [200, 202, 404].includes(status),
      });

      const { status, headers, data } = res;
      const contentType = headers["content-type"];
      const retryAfter = headers["retry-after"] ? parseInt(headers["retry-after"]) * 1000 : retryDelay;

      if (status === 202) {
        attempt++;
        console.log(`[ThumbnailRetry] fileId=${fileId}, Deneme ${attempt}/${maxRetries}, Bekleme: ${retryAfter}ms`);
        await delay(retryAfter);
        continue;
      }

      if (status === 404) {
        throw new Error("Thumbnail dosyası bulunamadı.");
      }

      if (status === 200) {
        if (!contentType?.startsWith("image/")) {
          throw new Error(`Geçersiz içerik türü: ${contentType}`);
        }
        console.log(`[ThumbnailSuccess] fileId=${fileId} başarıyla alındı`);
        return data instanceof Blob ? data : new Blob([data], { type: contentType });
      }

    } catch (err) {
      if (attempt >= maxRetries - 1) {
        const code = err?.response?.status || "BağlantıYok";
        const msg = err?.response?.statusText || err.message;
        console.error(`[ThumbnailError] fileId=${fileId}, Hata: ${code} – ${msg}`);
        throw new Error("Thumbnail yüklenemedi, lütfen sayfayı yenileyin veya daha sonra tekrar deneyin.");
      }
      attempt++;
      await delay(retryDelay);
    }
  }
  console.error(`[ThumbnailError] fileId=${fileId}, Maksimum deneme hakkı aşıldı`);
  throw new Error("Thumbnail yüklenemedi, lütfen sayfayı yenileyin veya daha sonra tekrar deneyin.");
};






/**
 * ⬇ Dosya indir
 * @param {string} path
 */
export const downloadFile = async (path) => {
  const decoded = decodeURIComponent(path);
  const res = await axios.get("filesharehub-v2/download/", {
    params: { path: decoded },
    responseType: "blob",
  });

  const filename = _extractFilename(res.headers["content-disposition"]);
  return {
    blob: res.data,
    filename,
  };
};

/**
 * 📦 Content-Disposition içinden dosya adını çıkar
 */
function _extractFilename(cd) {
  if (!cd) return "indirilen_dosya";
  const utf8match = cd.match(/filename\*=UTF-8''([^;]+)/);
  if (utf8match && utf8match[1]) {
    return decodeURIComponent(utf8match[1]);
  }
  const fallback = cd.match(/filename="?([^";]+)"?/);
  return fallback ? decodeURIComponent(fallback[1]) : "indirilen_dosya";
}
