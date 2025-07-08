// frontend/src/components/FileShareHub_V2/components/FolderList.jsx
import React, { memo, useCallback } from "react";
import styles from "../css/FolderList.module.css";
import { Folder, Home, ArrowLeft } from "lucide-react";

function FolderList({
  folders = [],
  onFolderClick,
  onBackClick,
  onHomeClick,
}) {
  /** Klasör tıklamasını memoize et – gereksiz render’ı engeller */
  const handleFolderClick = useCallback(
    (folder) => {
      onFolderClick?.(folder);
    },
    [onFolderClick]
  );

  return (
    <div className={styles["folder-panel"]}>
      {/* ---------- Üst Kontroller ---------- */}
      <div className={styles["folder-panel__header"]}>
        <button
          className={styles["folder-panel__control"]}
          onClick={onHomeClick}
          title="Ana dizine dön"
        >
          <Home size={16} /> Ana
        </button>

        <button
          className={styles["folder-panel__control"]}
          onClick={onBackClick}
          title="Bir üst dizine çık"
        >
          <ArrowLeft size={16} /> Geri
        </button>
      </div>

      {/* ---------- Klasör Listesi ---------- */}
      <ul className={styles["folder-panel__list"]}>
        {folders.length > 0 ? (
          folders.map((folder, idx) => (
            <li
              key={folder.file_id ?? `folder-${idx}`}
              className={styles["folder-panel__item"]}
              onClick={() => handleFolderClick(folder)}
              role="button"
              tabIndex={0}
            >
              <Folder size={18} className={styles["folder-panel__icon"]} />
              <span className={styles["folder-panel__name"]}>{folder.name}</span>
            </li>
          ))
        ) : (
          <li className={styles["folder-panel__empty"]}>Klasör yok</li>
        )}
      </ul>
    </div>
  );
}

export default memo(FolderList);
