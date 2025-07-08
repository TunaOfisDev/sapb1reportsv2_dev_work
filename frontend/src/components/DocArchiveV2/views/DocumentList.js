// frontend/src/components/DocArchiveV2/views/DocumentList.js
import React from 'react';
import useDocuments from '../hooks/useDocuments';
import '../css/DocumentList.css';

const DocumentList = ({ onRefresh }) => {
    const { documents, loading, error } = useDocuments();

    if (loading) return <p>Loading documents...</p>;
    if (error) return <p>Error loading documents: {error.message}</p>;

    // Sıralama işlemi: id'ye göre azalan sırada
    const sortedDocuments = documents.sort((a, b) => b.id - a.id);

    return (
        <table className="document-list__table">
            <thead>
                <tr>
                    <th className="document-list__header">ID</th>  
                    <th className="document-list__header">Department</th>
                    <th className="document-list__header">Name</th>
                    <th className="document-list__header">Owner</th>
                    <th className="document-list__header">Files</th>
                    <th className="document-list__header">Comments</th>
                   
                </tr>
            </thead>
            <tbody>
                {sortedDocuments.map((doc) => (
                    <tr key={doc.id} className="document-list__row--hover">
                        <td className="document-list__cell">{doc.id}</td>  
                        <td className="document-list__cell">{doc.departmentName || 'No Department'}</td>
                        <td className="document-list__cell">{doc.name}</td>
                        <td className="document-list__cell">{doc.owner_name}</td>
                        <td className="document-list__cell">
                            {doc.files && doc.files.map((file, index) => (
                                <a key={index} href={file.file} target="_blank" rel="noopener noreferrer" className="document-list__link">
                                    View File {index + 1}
                                </a>
                            ))}
                        </td>
                        <td className="document-list__cell">{doc.comments}</td>
                      
                    </tr>
                ))}
            </tbody>
        </table>
    );
};

export default DocumentList;
