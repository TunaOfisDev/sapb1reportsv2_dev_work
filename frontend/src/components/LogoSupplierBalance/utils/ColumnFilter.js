// frontend/src/components/LogoSupplierBalance/utils/ColumnFilter.js
import React from 'react';
import '../css/ColumnFilter.css'; 

function DefaultColumnFilter({
  column: { filterValue, preFilteredRows, setFilter, id },
}) {

  const handleStopPropagation = (e) => {
    e.stopPropagation();
  };

  return (
    <div className="open-order-doc-sum__filter" onClick={handleStopPropagation}>
       <input
        value={filterValue || ''}
        onChange={e => setFilter(e.target.value)}
        placeholder={`Ara...`}
        style={{
          width: '90%', // Genişliği %100 yap
          fontSize: '0.80rem', // Font büyüklüğünü artır
          padding: '0.5rem', // Padding artır
          margin: '0', // Eğer gerekliyse
          border: '0', // Çerçeve kaldır
          outline: 'none' // Odaklanıldığında dış çizgiyi kaldır
        }}
      />

    </div>
  );
}

export default DefaultColumnFilter;



