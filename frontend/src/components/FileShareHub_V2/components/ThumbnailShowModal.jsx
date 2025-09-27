// frontend/src/components/FileShareHub_V2/components/ThumbnailShowModal.jsx
import { useEffect } from "react";
import PropTypes from "prop-types";
import "../css/ThumbnailShowModal.css";

/**
 * Kurumsal Thumbnail Show Modal
 * -------------------------------------------------------------
 * Görev: Mevcut thumbnail görselini 2× boyutta (max-width: 90vw) kullanıcıya sunar.
 * ESC veya Space tuşu ile kapatılabilir. Arka plan scroll'u da devre dışı bırakılır.
 */
export default function ThumbnailShowModal({ open, src, alt, onClose }) {
  useEffect(() => {
    if (!open) return;

    document.body.style.overflow = "hidden";

    const handleKey = (e) => {
      if (e.key === "Escape" || e.code === "Space") {
        e.preventDefault();
        onClose();
      }
    };

    window.addEventListener("keydown", handleKey);
    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", handleKey);
    };
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="tsm-overlay" onClick={onClose}>
      <div className="tsm-dialog" onClick={(e) => e.stopPropagation()}>
        <img src={src} alt={alt} className="tsm-image" />
        <button className="tsm-close" onClick={onClose} aria-label="Kapat">
          ✕
        </button>
      </div>
    </div>
  );
}

ThumbnailShowModal.propTypes = {
  open: PropTypes.bool.isRequired,
  src: PropTypes.string.isRequired,
  alt: PropTypes.string,
  onClose: PropTypes.func.isRequired,
};

ThumbnailShowModal.defaultProps = {
  alt: "thumbnail-preview",
};
