// frontend/src/components/LogoSupplierBalance/containers/LogoSupplierBalanceContainer.js
import React from 'react';
import useLogoSupplierBalance from '../hooks/useLogoSupplierBalance';
import LogoSupplierBalanceTable from './LogoSupplierBalanceTable';
import '../css/LogoSupplierBalanceContainer.css';

const LogoSupplierBalanceContainer = () => {
  const { balances, loading, error, updateBalances, updateLoading } = useLogoSupplierBalance();

  const handleUpdateBalances = async () => {
    await updateBalances();
    window.location.reload(); // Sayfayı otomatik olarak yenile
  };

  if (loading) return <div className="loading-message">Yükleniyor...</div>;
  if (error) return <div className="error-message">Hata: {error.message}</div>;

  return (
    <div className="logo-supplier-balance-container">
      <div className="logo-supplier-balance-container__header">
        <h3 className="logo-supplier-balance-container__title">Tedarikci Bakiye Listesi</h3>
        <div className="logo-supplier-balance-container__button-wrapper">
          <button onClick={handleUpdateBalances} className="logo-supplier-balance-container__button" disabled={updateLoading}>
            {updateLoading ? 'Güncelleniyor...' : 'Canlı Verileri Çek'}
          </button>
        </div>
      </div>
      <LogoSupplierBalanceTable data={balances} />
    </div>
  );
};

export default LogoSupplierBalanceContainer;
