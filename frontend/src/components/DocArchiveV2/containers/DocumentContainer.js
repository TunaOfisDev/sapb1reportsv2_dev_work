// frontend/src/components/DocArchiveV2/containers/DocumentManager.js
import React from 'react';
import DocumentManager from '../views/DocumentManager';
import '../css/DocumentContainer.css'; // CSS dosyasını import edin

const DocumentContainer = () => {
    return (
        <div >
            <h2 className="document-container">Belge Yönetim Sistemi</h2>
            <DocumentManager />
        </div>
    );
};

export default DocumentContainer;

