// frontend/src/components/CustomerCollection/utils/ColumnFilter.js

const ColumnFilter = ({ column }) => {
  const { filterValue, setFilter } = column;
  return (
    <span className="filter-container">
      <input
        value={filterValue || ''}
        onChange={e => setFilter(e.target.value)}
        placeholder={`Ara...`}
      />
    </span>
  );
};

export default ColumnFilter;

