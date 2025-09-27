// frontend/src/components/LogoCustomerBalance/containers/LogoCustomerBalanceContainer.js
import React from 'react';
import useLogoCustomerBalance from '../hooks/useLogoCustomerBalance';
import LogoCustomerBalanceTable from './LogoCustomerBalanceTable';
import '../css/LogoCustomerBalanceContainer.css';

const LogoCustomerBalanceContainer = () => {
  const { balances, loading, error, updateBalances, updateLoading } = useLogoCustomerBalance();

  const handleUpdateBalances = async () => {
    await updateBalances();
    window.location.reload(); // Sayfayı otomatik olarak yenile
  };

  if (loading) return <div className="loading-message">Yükleniyor...</div>;
  if (error) return <div className="error-message">Hata: {error.message}</div>;

  return (
    <div className="logo-customer-balance-container">
      <div className="logo-customer-balance-container__header">
        <h3 className="logo-customer-balance-container__title">Müşteri Bakiye Listesi</h3>
        <div className="logo-customer-balance-container__button-wrapper">
          <button onClick={handleUpdateBalances} className="logo-customer-balance-container__button" disabled={updateLoading}>
            {updateLoading ? 'Güncelleniyor...' : 'Canlı Verileri Çek'}
          </button>
        </div>
      </div>
      <LogoCustomerBalanceTable data={balances} />
    </div>
  );
};

export default LogoCustomerBalanceContainer;
