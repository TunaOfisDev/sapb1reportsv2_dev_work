// frontend/src/components/FileShareHub/containers/FileShareHubContainer.js
import React from 'react';
import useFileShareHub from '../hooks/useFileShareHub';
import '../css/filesharehubcontainer.css';

const FileShareHubContainer = () => {
  const { path, contents, loading, error, loadDirectory, handleFileDownload } = useFileShareHub();

  const handleDirectoryClick = (directoryName) => {
    const newPath = path ? `${path}/${directoryName}` : directoryName;
    loadDirectory(newPath);
  };

  const handleBackClick = () => {
    if (path) {
      const newPath = path.substring(0, path.lastIndexOf('/'));
      loadDirectory(newPath);
    }
  };

  const handleHomeClick = () => {
    loadDirectory(''); // Kök dizine yönlendirmek için boş path ile çağır
  };

  const formatFileSize = (sizeInBytes) => {
    const sizeInMB = sizeInBytes / (1024 * 1024);
    return sizeInMB.toFixed(2) + ' MB';
  };

  return (
    <div className="filesharehub">
      <h1 className="filesharehub__title">File Share Hub</h1>
      {loading && <p className="filesharehub__loading">Yükleniyor...</p>}
      {error && <p className="filesharehub__error">{error}</p>}
      <div className="filesharehub__navigation">
        <h3 className="filesharehub__current-path">Geçerli Klasör: {path || 'Kök Dizin'}</h3>
        <button 
          className="filesharehub__back-button" 
          onClick={handleBackClick} 
          disabled={!path}
        >
          Geri
        </button>
        <button 
          className="filesharehub__home-button" 
          onClick={handleHomeClick}
        >
          Home
        </button>
      </div>
      <div className="filesharehub__content">
        <div className="filesharehub__left-panel">
          <div className="filesharehub__panel-header">
            <h4 className="filesharehub__section-title">Klasörler:</h4>
            <button 
              className="filesharehub__back-button filesharehub__back-button--small" 
              onClick={handleBackClick} 
              disabled={!path}
            >
              Üst Klasör
            </button>
          </div>
          <ul className="filesharehub__directory-list">
            {contents.directories && contents.directories.length > 0 ? (
              contents.directories.map((dir) => (
                <li 
                  key={dir.name} 
                  className="filesharehub__directory-item"
                  onClick={() => handleDirectoryClick(dir.name)}
                >
                  <span className="filesharehub__icon">&#128193;</span>
                  <span className="filesharehub__item-name">{dir.name}</span>
                </li>
              ))
            ) : (
              <li className="filesharehub__no-item">Klasör yok</li>
            )}
          </ul>
        </div>
        <div className="filesharehub__right-panel">
          <h4 className="filesharehub__section-title">Dosyalar:</h4>
          <ul className="filesharehub__file-list">
            {contents.files && contents.files.length > 0 ? (
              contents.files.map((file) => (
                <li key={file.name} className="filesharehub__file-item">
                  <span className="filesharehub__icon">&#128196;</span>
                  <span className="filesharehub__item-name">{file.name}</span>
                  <span className="filesharehub__item-size">{formatFileSize(file.size)}</span>
                  <button 
                    className="filesharehub__download-button" 
                    onClick={() => handleFileDownload(file.name)}
                  >
                    İndir
                  </button>
                </li>
              ))
            ) : (
              <li className="filesharehub__no-item">Dosya yok</li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default FileShareHubContainer;
