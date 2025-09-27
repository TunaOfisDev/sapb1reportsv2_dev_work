// frontend/src/components/RawMaterialWarehouseStock/utils/ItemGroupSelect.js
import React, { useState, useEffect } from 'react';
import Select from 'react-select';

const ItemGroupSelect = ({ onSelectionChange, isHammaddeSelected }) => {
  const [selectedOption, setSelectedOption] = useState(() => {
    return isHammaddeSelected !== null ? { value: isHammaddeSelected, label: isHammaddeSelected ? 'Evet' : 'Hayır' } : null;
  });

  useEffect(() => {
    if (isHammaddeSelected !== null) {
      setSelectedOption({ value: isHammaddeSelected, label: isHammaddeSelected ? 'Evet' : 'Hayır' });
    }
  }, [isHammaddeSelected]);

  const options = [
    { value: true, label: 'Evet' },
    { value: false, label: 'Hayır' },
  ];

  const handleChange = (selectedOption) => {
    setSelectedOption(selectedOption);
    onSelectionChange(selectedOption ? selectedOption.value : null);
  };

  return (
    <div className="item-group-select">
      <Select
        value={selectedOption}
        onChange={handleChange}
        options={options}
        placeholder="Hammadde seçiniz..."
        noOptionsMessage={() => "Seçenek bulunamadı"}
      />
    </div>
  );
};

export default ItemGroupSelect;
