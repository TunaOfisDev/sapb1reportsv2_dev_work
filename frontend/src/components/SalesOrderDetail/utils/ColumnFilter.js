// frontend/src/components/SalesOrderDetail/utils/ColumnFilter.js
import '../css/SalesOrderDetailTable.css';

const ColumnFilter = ({ column }) => {
  const { filterValue, setFilter } = column;

  const handleChange = (e) => {
      // Kullanıcının girdiği metni al
      let value = e.target.value;

      // Türkçe karakterleri ve diğer harfleri büyük harfe dönüştür
      value = value.replace(/i/g, 'İ')
                   .replace(/ı/g, 'I')
                   .replace(/ü/g, 'Ü')
                   .replace(/ö/g, 'Ö')
                   .replace(/ğ/g, 'Ğ')
                   .replace(/ç/g, 'Ç')
                   .toUpperCase();
      
      // Dönüştürülmüş metni setFilter ile güncelle
      setFilter(value);
  };

  return (
    <span className="column-filter-wrapper">
      <input
        className="column-filter-input"
        value={filterValue || ''}
        onChange={handleChange}
        placeholder={`Ara...`}
      />
    </span>
  );
};

export default ColumnFilter;

  