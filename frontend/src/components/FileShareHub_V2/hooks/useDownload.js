// frontend/src/components/FileShareHub_V2/hooks/useDownload.js
import { useState } from "react";
import { downloadFile } from "../api/fileApi";

export default function useDownload() {
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState(null);

  const triggerDownload = async (path) => {
    setDownloading(true);
    setError(null);

    try {
      const { blob, filename } = await downloadFile(path);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename || "dosya");
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Download error:", err);
      setError("Dosya indirilemedi.");
    } finally {
      setDownloading(false);
    }
  };

  return {
    downloading,
    error,
    triggerDownload,
  };
}
