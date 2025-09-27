// frontend/src/components/FileShareHub_V2/components/FileList.jsx
import React, { memo, useCallback } from "react";
import styles from "../css/FileList.module.css";
import ThumbPreview from "./ThumbPreview";
import {
  getFileType,
  getFileIconByExtension,
  formatFileSize,
} from "../utils/fileUtils";
import DownloadButton from "./DownloadButton";

/**
 * File list for FileShareHub V2.
 *
 * @param {Array}  files       – Dosya/klasör listesi
 * @param {Function} onFileClick – Dosya tıklama callback’i (sadece dosya için)
 */
function FileList({ files = [], onFileClick }) {
  /** Tek bir memoize tıklama fonksiyonu */
  const handleFileClick = useCallback(
    (file) => {
      if (!file?.is_dir && onFileClick) {
        onFileClick(file);
      }
    },
    [onFileClick]
  );

  if (!Array.isArray(files) || files.length === 0) {
    return <div className={styles["file-list__empty"]}>Gösterilecek dosya yok</div>;
  }

  return (
    <div className={styles["file-list"]}>
      {files.map((file, idx) => {
        if (!file || !file.name) return null;

        const key = file.file_id ?? `file-${idx}`;
        const type = getFileType(file);

        return (
          <div
            key={key}
            className={styles["file-list__item"]}
            onClick={() => handleFileClick(file)}
          >
            {/* ---------- İkon veya küçük ön-izleme ---------- */}
            {type === "image" ? (
              <ThumbPreview file={file} />
            ) : (
              <>
                <div className={styles["file-list__icon"]}>
                  {getFileIconByExtension(file.ext)}
                </div>
                <div className={styles["file-list__name"]}>{file.name}</div>
              </>
            )}

            {/* ---------- Sağ aksiyonlar ---------- */}
            {!file.is_dir && (
              <DownloadButton path={file.full_path ?? file.name} />
            )}

            {file.size != null && (
              <div className={styles["file-list__size"]}>
                {formatFileSize(file.size)}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

export default memo(FileList);
