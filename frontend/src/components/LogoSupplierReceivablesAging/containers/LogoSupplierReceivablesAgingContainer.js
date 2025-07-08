// frontend/src/components/LogoSupplierReceivablesAging/containers/LogoSupplierReceivablesAgingContainer.js
import { useCallback, useEffect } from 'react';
import useLogoSupplierReceivablesAging from '../hooks/useLogoSupplierReceivablesAging';
import LogoSupplierReceivablesAgingTable from './LogoSupplierReceivablesAgingTable';
import { formatDateTime } from '../utils/DateTimeFormat';
import XLSXExport from '../utils/XLSXExport';
import '../css/LogoSupplierReceivablesAgingContainer.css';

const LogoSupplierReceivablesAgingContainer = () => {
  const {
    data,
    filteredData,
    loading,
    error,
    fetchLocalSummary,
    fetchLiveSummary,
    lastUpdated,
  } = useLogoSupplierReceivablesAging();

  /** HANA’dan canlı veri tetikler → tablo + zaman otomatik yenilenir */
  const handleLiveFetch = useCallback(async () => {
    await fetchLiveSummary();
  }, [fetchLiveSummary]);

  /** Excel aktarımı */
  const handleExportExcel = useCallback(() => {
    if (!data.length) {
      alert('Aktarılacak veri yok.');
      return;
    }
    XLSXExport.exportToExcel(data, 'Tedarikci_Odemeleri');
  }, [data]);

  /** İlk yüklemede yerel özet + son güncelleme bilgisi */
  useEffect(() => {
    fetchLocalSummary();
  }, [fetchLocalSummary]);

  return (
    <div className="logo-supplier-aging">
      <div className="logo-supplier-aging__header">
        <h1 className="logo-supplier-aging__title">Sofitel Tedarikçi Ödemeleri</h1>

        <span className="logo-supplier-aging__last-updated">
          {lastUpdated
            ? `Son Güncelleme: ${formatDateTime(lastUpdated)}`
            : 'Güncellenme bilgisi alınıyor...'}
        </span>

        <div className="logo-supplier-aging__controls">
          <button
            className="logo-supplier-aging__button"
            title="Yerel özet veriyi çeker"
            onClick={fetchLocalSummary}
            disabled={loading}
          >
            Yerel Veri
          </button>

          <button
            className="logo-supplier-aging__button"
            title="HANA’dan canlı veri çeker"
            onClick={handleLiveFetch}
            disabled={loading}
          >
            Anlık Veri
          </button>

          <button
            className="logo-supplier-aging__button"
            title="Veriyi Excel’e aktarır"
            onClick={handleExportExcel}
            disabled={loading || data.length === 0}
          >
            Excel
          </button>
        </div>
      </div>

      {loading && (
        <div className="logo-supplier-aging__status">
          <p>Yükleniyor…</p>
        </div>
      )}

      {error && (
        <div className="logo-supplier-aging__status logo-supplier-aging__status--error">
          <p>{error}</p>
        </div>
      )}

      {!loading && data.length === 0 && (
        <div className="logo-supplier-aging__status">
          <p>Veri bulunamadı. Yukarıdaki butonlarla veri çekebilirsiniz.</p>
        </div>
      )}

      {data.length > 0 && (
        <LogoSupplierReceivablesAgingTable data={filteredData} />
      )}
    </div>
  );
};

export default LogoSupplierReceivablesAgingContainer;
