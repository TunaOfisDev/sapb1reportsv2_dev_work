// frontend/src/components/LogoCustomerCollection/utils/DynamicSubTotal.js
import { useMemo } from 'react';
import styled from 'styled-components';

// Styled component ile alt toplam stilini oluşturalım
export const DynamicSubtotalCell = styled.div`
  font-weight: bold;
  text-align: right;
  color: #2C4E6C; /* SAP mavisi - kurumsal görünüm için */
  padding: 8px;
  border-top: 2px solid #ddd;
  font-size: 1.1em;
`;

const useDynamicSubtotals = (rows, valueAccessors) => {
  const subtotals = useMemo(() => {
    if (!Array.isArray(valueAccessors)) {
      console.error('valueAccessors should be an array');
      return {};
    }

    const initSubtotals = valueAccessors.reduce((acc, valueAccessor) => {
      acc[valueAccessor] = 0;
      return acc;
    }, {});

    // Alt toplamları hesapla
    rows.forEach(row => {
      valueAccessors.forEach(valueAccessor => {
        const rawValue = row.values[valueAccessor];
        const value = rawValue !== undefined ? parseFloat(rawValue) : 0;
        if (!isNaN(value)) {
          initSubtotals[valueAccessor] += value;
        }
      });
    });

    // Formatlanmış ve orijinal değerleri döndür
    return {
      values: initSubtotals,
      formatted: Object.entries(initSubtotals).reduce((acc, [key, value]) => {
        acc[key] = new Intl.NumberFormat('tr-TR', {
          minimumFractionDigits: 0,
          maximumFractionDigits: 0
        }).format(value);
        return acc;
      }, {})
    };

  }, [rows, valueAccessors]);

  return subtotals;
};

export default useDynamicSubtotals;