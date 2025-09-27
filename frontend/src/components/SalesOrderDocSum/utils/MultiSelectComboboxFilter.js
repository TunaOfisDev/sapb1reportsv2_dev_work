// frontend/src/components/SalesOrderDocSum/utils/MultiSelectComboboxFilter.js
import React, { useState, useEffect } from 'react';
import Select from 'react-select';
import makeAnimated from 'react-select/animated';
import { useAsyncDebounce } from 'react-table';
import '../css/MultiSelectComboboxFilter.css';

const animatedComponents = makeAnimated();

const MultiSelectComboboxFilter = ({ column: { setFilter, preFilteredRows, id } }) => {
  const [selectedOptions, setSelectedOptions] = useState([]);

  // Preprocess options for the dropdown
  const options = React.useMemo(() => {
    const optionsSet = new Set();
    preFilteredRows.forEach(row => {
      optionsSet.add(row.values[id]);
    });
    return [...optionsSet.values()].map(option => ({
      value: option,
      label: option,
    }));
  }, [id, preFilteredRows]);

  const onChange = useAsyncDebounce(selectedOptions => {
    const filterValues = selectedOptions ? selectedOptions.map(option => option.value) : [];
    setFilter(filterValues.length ? filterValues : undefined);
  }, 200);

  useEffect(() => {
    onChange(selectedOptions);
  }, [selectedOptions, onChange]);

  return (
    <Select
      closeMenuOnSelect={false}
      components={animatedComponents}
      isMulti
      options={options}
      value={selectedOptions}
      onChange={setSelectedOptions}
      placeholder="Satıcı Seçin..."
      classNamePrefix="react-select"
      className="multi-select-combobox"
    />
  );
};

export default MultiSelectComboboxFilter;








