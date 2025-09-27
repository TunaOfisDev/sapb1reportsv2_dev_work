// frontend/src/components/FileShareHub_V2/components/HeaderBar.jsx
import React, { useMemo } from "react";
import styles from "../css/HeaderBar.module.css";
import { Home, ArrowLeft } from "lucide-react";

export default function HeaderBar({ currentPath, onBack, onHome, onNavigate }) {
  /** -------------------------------------------------------------
   *  Breadcrumb’leri yalnızca currentPath | onNavigate değiştiğinde
   *  yeniden oluştur (performans iyileştirmesi)
   *  ------------------------------------------------------------- */
  const pathLinks = useMemo(() => {
    if (!currentPath) {
      return <span className={styles["header-bar__path"]}>/</span>;
    }

    const parts = currentPath.split("/").filter(Boolean);

    return (
      <span className={styles["header-bar__path"]}>
        {parts.map((segment, index) => {
          const subPath = parts.slice(0, index + 1).join("/");
          return (
            <span key={subPath} className={styles["header-bar__crumb"]}>
              <a
                href="#"
                onClick={(e) => {
                  e.preventDefault();
                  onNavigate?.(subPath);
                }}
              >
                {segment}
              </a>
              {index < parts.length - 1 && (
                <span className={styles["header-bar__separator"]}> / </span>
              )}
            </span>
          );
        })}
      </span>
    );
  }, [currentPath, onNavigate]);

  return (
    <div className={styles["header-bar"]}>
      {/* --- Sol aksiyon butonları --- */}
      <div className={styles["header-bar__actions"]}>
        <button
          className={styles["header-bar__button"]}
          onClick={onHome}
          title="Ana dizine dön"
        >
          <Home size={16} /> Ana Sayfa
        </button>

        {currentPath && (
          <button
            className={styles["header-bar__button"]}
            onClick={onBack}
            title="Bir üst dizine çık"
          >
            <ArrowLeft size={16} /> Geri
          </button>
        )}

        {/* Breadcrumb’ler */}
        {pathLinks}
      </div>

      {/* --- Başlık --- */}
      <h2 className={styles["header-bar__title"]}>Dosya Gezgini</h2>
    </div>
  );
}
