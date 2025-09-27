// frontend/src/components/ProcureCompare/containers/ProcureCompareContainer.jsx

import React, { useRef, useState } from 'react';
import useProcureCompare from '../hooks/useProcureCompare';
import SyncButton from '../components/SyncButton';
import ProcureCompareTable from '../components/ProcureCompareTable';
import { formatDateTime } from '../utils/DateTimeFormat';
import exportToExcel from '../utils/ExcelExport';
import { handleExportPDF } from '../utils/PdfExportReact';
import NotsShowModal from '../utils/NotsShowModal';
import '../css/ProcureCompareContainer.css';

const ProcureCompareContainer = () => {
  const {
    comparisons,
    loading,
    syncing,
    error,
    syncFromHana,
    lastSyncedAt
  } = useProcureCompare();

  const tableRef = useRef();
  const [showNotes, setShowNotes] = useState(false);

  const getFilteredRows = () => {
    return tableRef.current?.getFilteredRows?.() || comparisons;
  };

  const handleExcelExport = () => {
    const filtered = getFilteredRows();
    exportToExcel(filtered, 'satin-alma-karsilastirma.xlsx');
  };

  const handlePdfExport = () => {
    const filtered = getFilteredRows();
    handleExportPDF(filtered);
  };

  return (
    <div className="procure-compare-container">
      <div className="procure-compare-container__header">
  <h2 className="procure-compare-container__title">Satınalma Karşılaştırma Raporu</h2>

  {lastSyncedAt && (
    <div className="procure-compare-container__last-updated">
      Son Güncelleme: {formatDateTime(lastSyncedAt)}
    </div>
  )}

  <div className="procure-compare-container__actions">
    <button className="procure-compare-container__button procure-compare-container__button--excel" onClick={handleExcelExport}>
      Excel'e Aktar
    </button>
    <button className="procure-compare-container__button procure-compare-container__button--pdf" onClick={handlePdfExport}>
      PDF'e Aktar
    </button>
    <button className="procure-compare-container__button procure-compare-container__button--notes" onClick={() => setShowNotes(true)}>
      Notlar
    </button>
    <SyncButton onClick={syncFromHana} loading={syncing} />
  </div>
</div>


      {error && (
        <div className="procure-compare-container__error">
          Hata oluştu: {error.message || 'Bilinmeyen hata'}
        </div>
      )}

      {loading ? (
        <p className="procure-compare-container__loading">Yükleniyor...</p>
      ) : (
        <ProcureCompareTable ref={tableRef} data={comparisons} />
      )}

      {showNotes && <NotsShowModal onClose={() => setShowNotes(false)} />}
    </div>
  );
};

export default ProcureCompareContainer;

