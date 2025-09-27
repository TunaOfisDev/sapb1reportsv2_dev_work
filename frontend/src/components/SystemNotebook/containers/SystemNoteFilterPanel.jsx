// frontend/src/components/SystemNotebook/containers/SystemNoteFilterPanel.jsx

import React, { useState } from 'react';
import '../css/systemnotebook-filter-panel.css';

const SystemNoteFilterPanel = ({ onFilter }) => {
  const [source, setSource] = useState('');
  const [title, setTitle] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();

    // Tümü seçildiyse source filtresini tamamen kaldır
    const filterParams = {};
    if (source) filterParams.source = source;
    if (title) filterParams.title = title;

    onFilter(filterParams);
  };

  return (
    <form className="systemnotebook-filter-panel" onSubmit={handleSubmit}>
      <div className="systemnotebook-filter-panel__group">
        <label className="systemnotebook-filter-panel__label">Kaynak</label>
        <select
          className="systemnotebook-filter-panel__select"
          value={source}
          onChange={(e) => setSource(e.target.value)}
        >
          <option value="">Tümü</option>
          <option value="github">GitHub</option>
          <option value="admin">SystemAdmin</option>
        </select>
      </div>

      <div className="systemnotebook-filter-panel__group">
        <label className="systemnotebook-filter-panel__label">Başlık İçeriği</label>
        <input
          type="text"
          className="systemnotebook-filter-panel__input"
          placeholder="Başlık ara..."
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
      </div>

      <div className="systemnotebook-filter-panel__group">
        <button type="submit" className="systemnotebook-filter-panel__button">
          Filtrele
        </button>
      </div>
    </form>
  );
};

export default SystemNoteFilterPanel;
