// frontend/src/components/RawMaterialWarehouseStock/utils/ZeroStockVisibilityToggle.js
import React from 'react';
import Select from 'react-select';

const options = [
  { value: false, label: 'Tüm Satırları Göster' },
  { value: true, label: 'Sıfır Stoklu Satırları Gizle' }
];

const ZeroStockVisibilitySelect = ({ onToggle, hideZeroStock }) => {
  const handleChange = (selectedOption) => {
    onToggle(selectedOption.value);
  };

  return (
    <div className="zero-stock-visibility-select">
      <Select
        options={options}
        onChange={handleChange}
        value={options.find(option => option.value === hideZeroStock)}
        placeholder="Stok Görünürlüğü"
      />
    </div>
  );
};

export default ZeroStockVisibilitySelect;
