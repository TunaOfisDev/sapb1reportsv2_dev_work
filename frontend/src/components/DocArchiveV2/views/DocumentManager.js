// frontend/src/components/DocArchiveV2/views/DocumentManager.js
import React from 'react';
import DocumentForm from './DocumentForm';
import DocumentList from './DocumentList';
import '../css/DocumentManager.css';

const DocumentManager = () => {
    return (
        <div className="document-manager">
            <div className="document-manager__form">
                <h2>Yeni Belge Ekle</h2>
                <DocumentForm />
            </div>
            <div className="document-manager__list">
                <h2>Document List</h2>
                <DocumentList />
            </div>
        </div>
    );
};

export default DocumentManager;
