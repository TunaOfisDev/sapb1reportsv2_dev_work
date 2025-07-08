// frontend/src/components/BomCostManager/views/BomCostView.js

import React, { useEffect } from 'react';
import useFetchBomCost from '../hooks/useFetchBomCost';
import '../css/BomCostView.css';

const BomCostView = () => {
    const { bomComponents, loading, error } = useFetchBomCost();

    useEffect(() => {
        console.log("BOM Components Data:", bomComponents);
    }, [bomComponents]);

    if (loading) {
        console.log("BOM Cost View: Veriler yükleniyor...");
        return <p className="bom-cost-view__loading">Yükleniyor...</p>;
    }
    if (error) {
        console.error("BOM Cost View Hatası:", error);
        return <p className="bom-cost-view__error">Hata: {error}</p>;
    }

    return (
        <div className="bom-cost-view">
            <h2 className="bom-cost-view__header">BOM Maliyet Analizi</h2>
            <div className="bom-cost-view__container">
                <table className="bom-cost-view__table">
                    <thead>
                        <tr className="bom-cost-view__table-header">
                            <th>Bileşen Kodu</th>
                            <th>Bileşen Adı</th>
                            <th>Miktar</th>
                            <th>Son Fiyat</th>
                            <th>Güncellenmiş Maliyet</th>
                        </tr>
                    </thead>
                    <tbody>
                        {bomComponents.map((component, index) => (
                            <tr key={index} className="bom-cost-view__table-row" onClick={() => console.log("Seçilen Bileşen:", component)}>
                                <td>{component.component_item_code}</td>
                                <td>{component.component_item_name}</td>
                                <td>{component.quantity}</td>
                                <td>{component.last_purchase_price}</td>
                                <td>{component.updated_cost}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default BomCostView;
