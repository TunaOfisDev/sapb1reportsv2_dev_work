// frontend/src/components/FileShareHub_V2/components/ThumbPreview.jsx
import React, { useState, useMemo, memo } from "react";
import useThumbnail from "../hooks/useThumbnail";
import ThumbnailShowModal from "./ThumbnailShowModal";
import {
  getFileIconByExtension,
  getFileExtension,
} from "../utils/fileUtils";
import styles from "../css/ThumbPreview.module.css";

function ThumbPreview({ file }) {
  const { url, loading, error } = useThumbnail(
    file?.file_id,
    file?.is_image,
    file?.name
  );
  const [open, setOpen] = useState(false);

  /** -------------------------------------------------------------
   *  Görüntü/ikon sadece `url`, `loading`, `error`, `file` değiştiğinde
   *  yeniden hesaplanır.
   *  ------------------------------------------------------------- */
  const previewContent = useMemo(() => {
    if (!file) {
      return (
        <div className={styles["thumb-preview__error"]}>Dosya bulunamadı</div>
      );
    }
    if (loading) {
      return (
        <div className={styles["thumb-preview__loading"]}>Yükleniyor…</div>
      );
    }
    if (url) {
      return (
        <img
          src={url}
          alt={file.name}
          className={styles["thumb-preview__image"]}
        />
      );
    }
    if (error) {
      return <div className={styles["thumb-preview__error"]}>{error}</div>;
    }
    return getFileIconByExtension(getFileExtension(file.name), file.is_dir, {
      className: styles["thumb-preview__icon"],
    });
  }, [file, loading, url, error]);

  return (
    <div className={styles["thumb-preview"]}>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className={styles["thumb-preview__button"]}
        aria-label="Önizle"
        disabled={!file}
      >
        {previewContent}
      </button>

      <div className={styles["thumb-preview__name"]}>
        {file?.name || "İsim yok"}
      </div>

      <ThumbnailShowModal
        open={open}
        src={url || `/media/thumbs/${file?.file_id || "default"}.jpg`}
        alt={file?.name || "Dosya"}
        onClose={() => setOpen(false)}
      />
    </div>
  );
}

export default memo(ThumbPreview);
