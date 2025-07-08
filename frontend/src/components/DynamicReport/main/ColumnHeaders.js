// frontend/src/components/DynamicReport/main/ColumnHeaders.js
import React from 'react';
import PropTypes from 'prop-types';

const ColumnHeaders = ({ columns }) => {
  if (!columns || columns.length === 0) {
    return (
      <thead>
        <tr>
          <th>No Columns Available</th>
        </tr>
      </thead>
    );
  }

  return (
    <thead>
      <tr>
        {columns.map((column, index) => (
          <th key={index}>{column ? column : `Column ${index + 1}`}</th>
        ))}
      </tr>
    </thead>
  );
};

ColumnHeaders.propTypes = {
  columns: PropTypes.arrayOf(PropTypes.string).isRequired,
};

ColumnHeaders.defaultProps = {
  columns: [],
};

export default ColumnHeaders;
