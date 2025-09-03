// frontend/src/components/CustomerSalesV2/utils/DynamicSubTotal.js
import React, { useMemo } from 'react';
import PropTypes from 'prop-types';
import FormatNumber from './FormatNumber';

const DynamicSubTotal = ({ data, columnId }) => {
  const total = useMemo(() => {
    // Gelen 'data' tanımsızsa veya boşsa, reduce hatasını önle
    if (!data || data.length === 0) {
      return 0;
    }
    return data.reduce((sum, current) => {
      // current.values tanımsız olabilir, kontrol et
      const value = Number(current.values?.[columnId]) || 0;
      return sum + value;
    }, 0);
  }, [data, columnId]);

  return <FormatNumber value={total} />;
};

DynamicSubTotal.propTypes = {
    data: PropTypes.array,
    columnId: PropTypes.string.isRequired,
};

export default DynamicSubTotal;
