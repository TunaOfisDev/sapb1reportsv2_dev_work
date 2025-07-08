// frontend/src/components/ProductConfig/common/PCHanaData.js
import React, { useEffect, useState } from 'react';
import pcHanaService from '../../../api/pcHanaService';
import tokenService from '../../../auth/tokenService'; // Token servisi
import '../css/PCHanaData.css';

const PCHanaData = () => {
    const [sapData, setSapData] = useState(null); // SAP verileri için state
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Token ve VariantId
    const token = tokenService.getLocalAccessToken();
    const variantId = localStorage.getItem('variant_id'); // VariantId'yi localStorage'dan alıyoruz

    useEffect(() => {
        const loadSapData = async () => {
            try {
                setLoading(true);
                setError(null);

                if (!variantId || !token) {
                    setError("Variant ID veya token bulunamadı.");
                    return;
                }

                // `update-hana-data` çağrısı
                const updateResponse = await pcHanaService.updateHanaData(variantId, token);
                if (!updateResponse.success) {
                    setError("HANA verileri güncellenemedi.");
                    return;
                }

                // Backend'den gelen güncellenmiş veriyi ayarlayın
                setSapData(updateResponse.data); // Gelen veriler set ediliyor
            } catch (err) {
                console.error("SAP verisi güncellenirken hata oluştu:", err);
                setError("HANA verisi güncellenirken bir hata oluştu.");
            } finally {
                setLoading(false);
            }
        };

        loadSapData();
    }, [variantId, token]);

    if (loading) {
        return (
            <div className="pc-hana-data">
                <div className="pc-hana-data__loading">
                    <span>SAP verileri yükleniyor...</span>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="pc-hana-data">
                <div className="pc-hana-data__error">
                    {error}
                </div>
            </div>
        );
    }

    if (!sapData) {
        return (
            <div className="pc-hana-data">
                <span>SAP verisi bulunamadı.</span>
            </div>
        );
    }

    return (
        <div className="pc-hana-data">
            <h3 className="pc-hana-data__title">SAP Bileşen Kodları</h3>
            <div className="pc-hana-data__table-container">
                <table className="pc-hana-data__table">
                    <thead>
                        <tr>
                            <th>Eski Bileşen Kodları</th>
                            <th>SAP Kalem Kodu</th>
                            <th>SAP Kalem Tanımı</th>
                            <th>Fiyat</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>{sapData.sap_U_eski_bilesen_kod || '-'}</td>
                            <td>{sapData.sap_item_code || '-'}</td>
                            <td>{sapData.sap_item_description || '-'}</td>
                            <td className="pc-hana-data__price">
                                {sapData.sap_price ? `${sapData.sap_price} ${sapData.sap_currency}` : '-'}
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default PCHanaData;
