// frontend/src/components/SalesBudgetv2/containers/SalesBudgetContainerv2.js
import React, { useEffect, useState } from 'react';
import { Button, Spinner } from 'react-bootstrap';
import { useDispatch, useSelector } from 'react-redux';
import useSalesBudget from '../hooks/useSalesBudget';
import { fetchLocalSalesBudgetsv2 } from '../../../redux/actions/salesbudgetv2/localSalesBudgetActionsv2';
import { fetchHanaSalesBudgetsv2 } from '../../../redux/actions/salesbudgetv2/hanaSalesBudgetActionsv2';
import SalesBudgetTable from './SalesBudgetTable';
import ErrorMessage from '../utils/ErrorMessage';
import { formatDateTime } from '../utils/DateTimeFormat';
import '../css/SalesBudgetContainer.css';

const SalesBudgetContainerv2 = () => {
  const dispatch = useDispatch();
  // state.salesBudgetv2 kullanıyoruz (önceki state.salesBudget yerine)
  const { salesBudgets, loading: reduxLoading, error: reduxError } = useSelector(state => state.salesBudgetv2);
  const [lastUpdated, setLastUpdated] = useState('Bilinmiyor');
  const { exportSalesBudgetToXLSX, loading: hookLoading, error: hookError } = useSalesBudget();

  useEffect(() => {
    dispatch(fetchLocalSalesBudgetsv2());
  }, [dispatch]);

  const handleFetchLocalData = () => {
    dispatch(fetchLocalSalesBudgetsv2());
  };

  const handleFetchHanaData = () => {
    dispatch(fetchHanaSalesBudgetsv2())
      .then(() => {
        // HANA verilerini çektikten sonra yerel verileri tekrar çekmek için
        setTimeout(() => {
          dispatch(fetchLocalSalesBudgetsv2());
        }, 1000);
      })
      .catch(error => {
        console.error("HANA veri çekme hatası:", error);
      });
  };

  const handleExportToXLSX = () => {
    exportSalesBudgetToXLSX()
      .catch(error => {
        console.error("Excel'e aktarma hatası:", error);
      });
  };

  // Veri çekildikçe en son güncellenme tarihini güncelle
  useEffect(() => {
    if (salesBudgets && salesBudgets.length > 0 && salesBudgets[0].updated_at) {
      const updatedTime = formatDateTime(salesBudgets[0].updated_at);
      setLastUpdated(updatedTime);
    }
  }, [salesBudgets]);

  const overallLoading = reduxLoading || hookLoading;
  const overallError = reduxError || hookError;

  return (
    <div className="sales-budget-container">
      <div className="sales-budget-container__header">
        <h1>Satış Bütçesi 2025 (TL)</h1>
        <div className="sales-budget-container__last-updated">
          Son Güncelleme: {lastUpdated}
        </div>
        <div className="sales-budget-container__button-wrapper">
          <Button onClick={handleFetchLocalData} disabled={overallLoading} className="sales-budget-container__button">
            {overallLoading ? 'Yükleniyor...' : 'Yerel Veri Çek'}
          </Button>
          <Button onClick={handleFetchHanaData} disabled={overallLoading} className="sales-budget-container__button">
            {overallLoading ? 'Yükleniyor...' : 'HANA Verilerini Çek'}
          </Button>
          <Button onClick={handleExportToXLSX} disabled={overallLoading || !salesBudgets || salesBudgets.length === 0} className="sales-budget-container__button">
            {overallLoading || !salesBudgets || salesBudgets.length === 0 ? 'Veri Yok' : "Excel'e Aktar"}
          </Button>
        </div>
      </div>
      {overallLoading && (
        <div className="text-center">
          <Spinner animation="border" role="status">
            <span className="sr-only">Yükleniyor...</span>
          </Spinner>
        </div>
      )}
      {overallError && <ErrorMessage message={`Hata: ${overallError}`} />}
      {!overallLoading && salesBudgets && salesBudgets.length > 0 ? (
        <SalesBudgetTable
          salesBudgets={salesBudgets}
          loading={overallLoading}
          error={overallError}
        />
      ) : (
        !overallLoading && (
          <p className="text-center mt-3">Veri bulunamadı. Veri çekmek için yukarıdaki butonlara basınız.</p>
        )
      )}
    </div>
  );
};

export default SalesBudgetContainerv2;