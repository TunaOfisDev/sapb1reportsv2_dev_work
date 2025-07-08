// frontend/src/components/SalesBudgetEur/container/salesbudgeteurContainer.js
import React, { useEffect } from 'react';
import { Button, Spinner } from 'react-bootstrap';
import useSalesBudgetEUR from '../hooks/Usesalesbudgeteur';
import SalesBudgetEURTable from './salesbudgeteurTable';
import ErrorMessage from '../utils/ErrorMessage';
import '../css/salesbudgeteurContainer.css';

const SalesBudgetEURContainer = () => {
  const {
    data: salesBudgets,
    loading,
    exporting,
    error,
    lastUpdated,   // 🔹 hook’tan doğrudan
    reload,
    fetchFromHana,
    exportToExcel,
  } = useSalesBudgetEUR();

  /* Mount’ta yerel veriyi çek (isteğe bağlı, hook zaten ilk çekimini yapıyor) */
  useEffect(() => {
    reload();
  }, [reload]);

  /* --- Handler’lar --- */
  const handleFetchLocal = () => reload();
  const handleFetchHana  = () => fetchFromHana();
  const handleExport     = () => exportToExcel();

  const disableButtons = loading || exporting;

  return (
    <div className="sales-budgeteur-container">
      {/* Üst bar */}
      <div className="sales-budgeteur-container__topbar">
        <h2 className="sales-budgeteur-container__title">
          Satış Bütçesi 2025 (EUR)
        </h2>

        <div className="sales-budgeteur-container__last-updated">
          Son Güncelleme:&nbsp;
          {lastUpdated || 'Bilinmiyor'}
        </div>

        <div className="sales-budgeteur-container__button-wrapper">
          <Button
            onClick={handleFetchLocal}
            disabled={disableButtons}
            className="sales-budgeteur-container__button"
          >
            {loading ? 'Yükleniyor…' : 'Yerel Veriyi Çek'}
          </Button>

          <Button
            onClick={handleFetchHana}
            disabled={disableButtons}
            className="sales-budgeteur-container__button"
          >
            {loading ? 'Yükleniyor…' : 'HANA Verisini Çek'}
          </Button>

          <Button
            onClick={handleExport}
            disabled={disableButtons || salesBudgets.length === 0}
            className="sales-budgeteur-container__button sales-budgeteur-container__button--secondary"
          >
            {exporting ? 'Aktarılıyor…' : "Excel'e Aktar"}
          </Button>
        </div>
      </div>

      {/* Alt çizgi */}
      <div className="sales-budgeteur-container__divider" />

      {/* İçerik */}
      {loading && (
        <div className="text-center mt-3">
          <Spinner animation="border" role="status" />
        </div>
      )}

      {error && <ErrorMessage message={`Hata: ${error.message || error}`} />}

      {!loading && salesBudgets.length > 0 ? (
        <SalesBudgetEURTable
          salesBudgets={salesBudgets}
          loading={loading}
          error={error}
        />
      ) : (
        !loading && (
          <p className="text-center mt-3">
            Veri bulunamadı. Lütfen üstteki butonları kullanarak veriyi çekin.
          </p>
        )
      )}
    </div>
  );
};

export default SalesBudgetEURContainer;
