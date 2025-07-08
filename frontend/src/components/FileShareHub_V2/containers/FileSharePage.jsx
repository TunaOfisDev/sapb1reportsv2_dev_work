// frontend/src/components/FileShareHub_V2/containers/FileSharePage.jsx
import React, { useState } from "react";
import styles from "../css/FileSharePage.module.css";
import { joinPath, getParentPath } from "../utils/pathUtils";
import useFileList from "../hooks/useFileList";
import FolderList from "../components/FolderList";
import FileList from "../components/FileList";
import HeaderBar from "../components/HeaderBar";

export default function FileSharePage() {
  const [path, setPath] = useState("");
  const { data, loading, error, setPath: updatePath } = useFileList(path);

  const handleFolderClick = (folder) => {
    const newPath = joinPath(path, folder.name);
    setPath(newPath);
    updatePath(newPath);
  };

  const handleBackClick = () => {
    const parent = getParentPath(path);
    setPath(parent);
    updatePath(parent);
  };

  const handleHomeClick = () => {
    setPath("");
    updatePath("");
  };

  const handleNavigate = (targetPath) => {
    setPath(targetPath);
    updatePath(targetPath);
  };

  return (
    <div className={styles["file-share-page"]}>
      <HeaderBar
        currentPath={path}
        onBack={handleBackClick}
        onHome={handleHomeClick}
        onNavigate={handleNavigate}
      />

      {loading && <div>Yükleniyor...</div>}
      {error && <div>Hata: {error}</div>}

      <div className={styles["file-layout"]}>
        <aside className={styles["folder-sidebar"]}>
          <FolderList
            folders={data.directories}
            onFolderClick={handleFolderClick}
            onBackClick={handleBackClick}
            onHomeClick={handleHomeClick}
          />
        </aside>
        <section className={styles["file-content"]}>
          <FileList files={data.files} onFileClick={() => {}} />
        </section>
      </div>
    </div>
  );
}