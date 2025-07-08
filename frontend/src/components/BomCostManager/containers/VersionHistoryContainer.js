// frontend/src/components/BomCostManager/containers/VersionHistoryContainer.js

import React, { useState, useEffect } from 'react';
import '../css/VersionHistoryContainer.css';

const VersionHistoryContainer = ({ fetchVersionHistory }) => {
    const [versions, setVersions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const loadVersions = async () => {
            try {
                const data = await fetchVersionHistory();
                setVersions(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };
        loadVersions();
    }, [fetchVersionHistory]);

    if (loading) return <p className="version-history-container__loading">Yükleniyor...</p>;
    if (error) return <p className="version-history-container__error">Hata: {error}</p>;

    return (
        <div className="version-history-container">
            <h2 className="version-history-container__header">Versiyon Geçmişi</h2>
            <ul className="version-history-container__list">
                {versions.map((version) => (
                    <li key={version.id} className="version-history-container__item">
                        <h3 className="version-history-container__item-title">{version.project_name}</h3>
                        <p className="version-history-container__item-date">Kaydedildi: {version.created_at}</p>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default VersionHistoryContainer;
