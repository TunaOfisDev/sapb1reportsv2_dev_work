// frontend/src/components/RawMaterialWarehouseStock/containers/RawMaterialWarehouseStockContainer.js
import React from 'react';
import useRawMaterialWarehouseStock from '../hooks/useRawMaterialWarehouseStock';
import RawMaterialWarehouseStockTable from './RawMaterialWarehouseStockTable';
import ItemGroupSelect from '../utils/ItemGroupSelect';
import ZeroStockVisibilitySelect from '../utils/ZeroStockVisibilityToggle';
import CeleryTaskStatusInfo from '../utils/CeleryTaskStatusInfo';
import useAuth from '../../../auth/useAuth';
import '../css/RawMaterialWarehouseStockContainer.css';

const RawMaterialWarehouseStockContainer = () => {
  const { isAuthenticated } = useAuth();
  
  const {
    data,
    loading,
    error,
    taskStatus,
    handleSelectionChange,
    isHammaddeSelected,
    hideZeroStock,
    handleZeroStockVisibilityChange,
    setPurchaseOrders,
    handleExportFiltered,
  } = useRawMaterialWarehouseStock();

  if (loading) return <div className="loading-message">Yükleniyor...</div>;
  if (error) return <div className="error-message">Hata: {error.message}</div>;
  if (!isAuthenticated) {
    return <div>Lütfen erişim için giriş yapın.</div>;
  }

  return (
    <div className="raw-material-warehouse-stock-container">
      <div className="raw-material-warehouse-stock-container__header">
        <h1 className="raw-material-warehouse-stock-container__title">
          Hammadde Depo Stok Durumu
        </h1>
        <div className="raw-material-warehouse-stock-container__controls">
          <ItemGroupSelect onSelectionChange={handleSelectionChange} isHammaddeSelected={isHammaddeSelected} />
          <ZeroStockVisibilitySelect onToggle={handleZeroStockVisibilityChange} hideZeroStock={hideZeroStock} />
          <div className="task-status">
            {taskStatus && <CeleryTaskStatusInfo status={taskStatus} />}
          </div>
        </div>
      </div>
      <RawMaterialWarehouseStockTable 
        data={data} 
        isHammaddeSelected={isHammaddeSelected} 
        hideZeroStock={hideZeroStock}
        setPurchaseOrders={setPurchaseOrders}
        handleExportFiltered={handleExportFiltered}
      />
    </div>
  );
};

export default RawMaterialWarehouseStockContainer;