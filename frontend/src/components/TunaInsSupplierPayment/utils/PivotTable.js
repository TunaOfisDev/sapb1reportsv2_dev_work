// frontend/src/components/TunaInsSupplierPayment/utils/PivotTable.js
import React from 'react';
import FormatNumber from './FormatNumber';
import '../css/PivotTable.css'; // CSS dosyasını import edin

function PivotTable({ data }) {
    // 'muhata_kod' değeri '120' ile başlayan verileri filtrele
    const filteredData = data.filter(item => item.muhatap_kod && item.muhatap_kod.startsWith('120'));

    // Filtrelenen veri üzerinden toplam_riskPositive ve toplam_riskNegative değerlerini hesapla
    const toplam_riskPositive = filteredData.reduce(
        (acc, cur) => parseFloat(cur.toplam_risk) > 0 ? acc + parseFloat(cur.toplam_risk) : acc, 0
    );
    const toplam_riskNegative = filteredData.reduce(
        (acc, cur) => parseFloat(cur.toplam_risk) < 0 ? acc + parseFloat(cur.toplam_risk) : acc, 0
    );
    
    return (
        <div className="pivot-table">
            <div className="pivot-table__row">
                <span className="pivot-table__label">Toplam Risk Pozitif:</span>
                <FormatNumber className="pivot-table__value" value={toplam_riskPositive} />
            </div> <td></td>
            <div className="pivot-table__row">
                <span className="pivot-table__label">Toplam Risk Negatif:</span>
                <FormatNumber className="pivot-table__value" value={toplam_riskNegative} />
            </div>
        </div>
    );
}

export default PivotTable;


