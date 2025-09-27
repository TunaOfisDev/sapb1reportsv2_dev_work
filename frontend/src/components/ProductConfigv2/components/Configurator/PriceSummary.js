// frontend/src/components/ProductConfigv2/components/Configurator/PriceSummary.js

import React from 'react';
import PropTypes from 'prop-types';
import { getFormattedTotalPrice } from '../../utils/configHelpers';
import { mapSelectedFeaturesToOptions } from '../../utils/mappingHelpers'; // bunu ekliyoruz
import '../../styles/PriceSummary.css';

const PriceSummary = ({ basePrice, specificationTypes, selections, currency }) => {
  const selectedOptions = mapSelectedFeaturesToOptions(specificationTypes, selections); // bu satırı ekliyoruz
  const formattedPrice = getFormattedTotalPrice(basePrice, selectedOptions, currency);

  return (
    <div className="price-summary">
      <h2 className="price-summary__title">Toplam Fiyat</h2>
      <p className="price-summary__value">{formattedPrice}</p>
    </div>
  );
};

PriceSummary.propTypes = {
  basePrice: PropTypes.oneOfType([PropTypes.number, PropTypes.string]).isRequired,
  specificationTypes: PropTypes.array.isRequired,
  selections: PropTypes.object.isRequired,
  currency: PropTypes.string,
};

PriceSummary.defaultProps = {
  currency: 'EUR',
};

export default React.memo(PriceSummary);
