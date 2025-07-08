// frontend/src/components/CrmBlog/utils/ColumnFilter.js

const ColumnFilter = ({ column }) => {
    const { filterValue, setFilter } = column;
    return (
      <span>
        <input
          value={filterValue || ''}
          onChange={e => setFilter(e.target.value)}
          placeholder={`Ara...`}
          style={{
            width: '90%', // Genişliği %100 yap
            fontSize: '0.85rem', // Font büyüklüğünü artır
            padding: '0.5rem', // Padding artır
            margin: '0', // Eğer gerekliyse
            border: '0', // Çerçeve kaldır
            outline: 'none' // Odaklanıldığında dış çizgiyi kaldır
          }}
        />
      </span>
    );
  };
  
  export default ColumnFilter;
  