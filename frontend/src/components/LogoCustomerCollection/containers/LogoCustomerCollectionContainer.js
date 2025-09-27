// frontend/src/components/LogoCustomerCollection/containers/LogoCustomerCollectionContainer.js
import { useCallback, useMemo } from 'react';
import useLogoCustomerCollection from '../hooks/useLogoCustomerCollection';
import LogoCustomerCollectionTable from './LogoCustomerCollectionTable';
import { formatDateTime } from '../utils/DateTimeFormat';
import XLSXExport from '../utils/XLSXExport';
import '../css/LogoCustomerCollectionContainer.css';

const LogoCustomerCollectionContainer = () => {
  const {
    data, filteredData, loading, error,
    lastUpdated,
    fetchLocalSummary,   // Yerel Veri
    fetchLiveSummary,    // Anlık Veri
  } = useLogoCustomerCollection();

  /* ------------ butonlar ------------ */
  const handleExportExcel = useCallback(() => {
    const exportData = filteredData.length ? filteredData : data;
    if (!exportData.length) { alert('Aktarılacak veri yok.'); return; }
    XLSXExport.exportToExcel(exportData, 'Musteri_Yaslandirma_Ozeti');
  }, [data, filteredData]);

  const displayData = useMemo(
    () => (filteredData.length ? filteredData : data),
    [filteredData, data],
  );

  /* ------------ render ------------ */
  return (
    <div className="logo-customer-collection">
      {/* ÜST BAR */}
      <div className="logo-customer-collection__header">
        <h1 className="logo-customer-collection__title">Müşteri Yaşlandırma Özeti</h1>

        <span className="logo-customer-collection__last-updated">
          {loading && !lastUpdated
            ? 'Yükleniyor...'
            : lastUpdated
              ? `Son Güncelleme: ${formatDateTime(lastUpdated)}`
              : 'Tarih bilgisi yok'}
        </span>

        <div className="logo-customer-collection__controls">
          <button
            className="logo-customer-collection__button"
            onClick={fetchLocalSummary}
            disabled={loading}
          >
            Yerel Veri
          </button>

          <button
            className="logo-customer-collection__button"
            onClick={fetchLiveSummary}
            disabled={loading}
          >
            Anlık Veri
          </button>

          <button
            className="logo-customer-collection__button"
            onClick={handleExportExcel}
            disabled={loading || !displayData.length}
          >
            Excel
          </button>
        </div>
      </div>

      {/* DURUM / HATA */}
      {loading && <div className="logo-customer-collection__status"><p>Yükleniyor…</p></div>}
      {error   && <div className="logo-customer-collection__status logo-customer-collection__status--error"><p>{error}</p></div>}

      {/* TABLO / “Veri yok” */}
      {!loading && displayData.length === 0 ? (
        <div className="logo-customer-collection__status">
          <p>Veri bulunamadı. Yukarıdaki butonlarla veri çekebilirsiniz.</p>
        </div>
      ) : (
        <LogoCustomerCollectionTable data={displayData} />
      )}
    </div>
  );
};

export default LogoCustomerCollectionContainer;
