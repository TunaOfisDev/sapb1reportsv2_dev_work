// frontend/src/components/SalesBudget/containers/SalesBudgetContainer.js
import React, { useEffect, useState, useCallback } from 'react';
import { Button, Spinner } from 'react-bootstrap';
import { useDispatch, useSelector } from 'react-redux';
import useSalesBudget from '../hooks/useSalesBudget';
import {
  fetchLocalSalesBudgets,
  
} from '../../../redux/actions/salesbudget/localSalesBudgetActions';

import {
  fetchHanaSalesBudgets
} from '../../../redux/actions/salesbudget/hanaSalesBudgetActions';
import SalesBudgetTable from './SalesBudgetTable';
import ErrorMessage from '../utils/ErrorMessage';
import { formatDateTime } from '../utils/DateTimeFormat';
import '../css/SalesBudgetContainer.css';

const SalesBudgetContainer = () => {
  const dispatch = useDispatch();

  /* ---------- Redux store ---------- */
  const { salesBudgets, loading: reduxLoading, error: reduxError } =
    useSelector((state) => state.salesBudget);

  /* ---------- Yerel state ---------- */
  const [lastUpdated, setLastUpdated] = useState('Bilinmiyor');

  /* ---------- Hook for export ---------- */
  const {
    exportSalesBudgetToXLSX,
    loading: hookLoading,
    error: hookError
  } = useSalesBudget();

  /* ---------- İlk yükleme ---------- */
  useEffect(() => {
    dispatch(fetchLocalSalesBudgets());
  }, [dispatch]);

  /* ---------- Son güncelleme zamanını hesapla ---------- */
  useEffect(() => {
    if (salesBudgets.length) {
      const ts = salesBudgets[0]?.updated_at;
      setLastUpdated(ts ? formatDateTime(ts) : 'Bilinmiyor');
    }
  }, [salesBudgets]);

  /* ---------- Handlers ---------- */
  const handleFetchLocalData = () => dispatch(fetchLocalSalesBudgets());

  const handleFetchHanaData = () => dispatch(fetchHanaSalesBudgets());

  const handleExportToXLSX = () => exportSalesBudgetToXLSX();

  /* ---------- Birleşik durum ---------- */
  const overallLoading = reduxLoading || hookLoading;
  const overallError   = reduxError   || hookError;

  /* ---------- Render ---------- */
  return (
    <div className="sales-budget-container">
      {/* Üst bar */}
      <div className="sales-budget-container__header">
        <h1 className="sales-budget-container__title">Satış Bütçesi 2024</h1>

        <div className="sales-budget-container__last-updated">
          Son Güncelleme:&nbsp;{lastUpdated}
        </div>

        <div className="sales-budget-container__button-wrapper">
          <Button
            onClick={handleFetchLocalData}
            disabled={overallLoading}
            className="sales-budget-container__button"
          >
            {overallLoading ? 'Yükleniyor...' : 'Yerel Veri Çek'}
          </Button>

          <Button
            onClick={handleFetchHanaData}
            disabled={overallLoading}
            className="sales-budget-container__button"
          >
            {overallLoading ? 'Yükleniyor...' : 'HANA Verilerini Çek'}
          </Button>

          <Button
            onClick={handleExportToXLSX}
            disabled={overallLoading || !salesBudgets.length}
            className="sales-budget-container__button"
          >
            {!salesBudgets.length ? 'Veri Yok' : "Excel'e Aktar"}
          </Button>
        </div>
      </div>

      {/* İçerik */}
      {overallLoading && (
        <Spinner animation="border" role="status" className="mt-3" />
      )}

      {overallError && <ErrorMessage message={`Hata: ${overallError}`} />}

      {!overallLoading && salesBudgets.length > 0 && (
        <SalesBudgetTable
          salesBudgets={salesBudgets}
          loading={overallLoading}
          error={overallError}
        />
      )}

      {!overallLoading && !salesBudgets.length && (
        <p className="mt-3">
          Veri bulunamadı. Veri çekmek için yukarıdaki butonlara basınız.
        </p>
      )}
    </div>
  );
};

export default SalesBudgetContainer;

