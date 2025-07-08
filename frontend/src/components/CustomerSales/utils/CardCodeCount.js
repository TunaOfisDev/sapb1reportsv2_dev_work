// frontend/src/components/CustomerSales/utils/CardCodeCount.js
import React, { useMemo } from 'react';
import useCustomerSales from '../hooks/useCustomerSales';
import '../css/CardCodeCount.css'; // CSS dosyasını import edin

const CardCodeCount = () => {
  const { customerSalesOrders, loading, error } = useCustomerSales();

  const uniqueCardCodes = useMemo(() => {
    const codes = new Set();
    customerSalesOrders.forEach(order => {
      codes.add(order.musteri_kod);
    });
    return codes.size;
  }, [customerSalesOrders]);

  if (loading) return <div>Yükleniyor...</div>;
  if (error) return <div>Hata: {error.message}</div>;

  return (
    <div className="card-code-count">
   
      <p className="card-code-count__number">{`Müşteri Sayısı: ${uniqueCardCodes}`}</p>
    </div>
  );
};

export default CardCodeCount;
