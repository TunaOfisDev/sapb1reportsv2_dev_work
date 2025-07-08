// frontend/src/components/FileShareHub_V2/components/DownloadButton.jsx
import React from "react";
import styles from "../css/DownloadButton.module.css";
import { downloadFile } from "../api/fileApi";

export default function DownloadButton({ path }) {
  const handleDownload = async () => {
    try {
      const { blob, filename } = await downloadFile(path);
      const url = window.URL.createObjectURL(new Blob([blob]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error("İndirme hatası:", error);
      alert("Dosya indirilemedi.");
    }
  };

  return (
    <button className={styles["download-button"]} onClick={handleDownload}>
      <span className={styles["download-button__icon"]}>⬇️</span> İndir
    </button>
  );
}
