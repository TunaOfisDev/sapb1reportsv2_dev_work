// frontend/src/components/OpenOrderDocSum/utils/HeatMap.js
import React from 'react';

// Renk hesaplama fonksiyonu, yüksek değerler için daha koyu yeşil, düşük değerler için gri tonları
const calculateColor = (value, maxValue) => {
  const percentage = value / maxValue;
  if (percentage > 0.75) {
    // Daha koyu yeşil tonları (daha yüksek değerler için)
    return `hsl(120, 100%, 30%)`; // Daha koyu yeşil
  } else if (percentage > 0.5) {
    // Orta yeşil
    return `hsl(120, 100%, 40%)`; // Orta yeşil
  } else if (percentage > 0.25) {
    // Gri-yeşil tonları
    return `hsl(60, 10%, 50%)`; // Gri-yeşil karışımı
  } else {
    // Düşük değerler için gri tonları
    return `hsl(0, 0%, 70%)`; // Açık gri
  }
};

const HeatMap = ({ value, maxValue, children }) => {
  const colorStyle = {
    backgroundColor: calculateColor(value, maxValue),
    color: 'white', // Tüm değerler için yazı rengi beyaz, daha yüksek kontrast için
    padding: '5px',  // Gerekirse padding ayarlayabilirsiniz.
    display: 'block' // İçerik düzgün görünsün diye
  };

  return (
    <div style={colorStyle}>
      {children}
    </div>
  );
};

export default HeatMap;

/*
 // maxValues'ı hesaplama
    const maxValues = useMemo(() => {
      return {
        acik_net_tutar_ypb: Math.max(...documentSummaries.map(item => item.acik_net_tutar_ypb)),
        // Diğer kolonlar için de benzer şekilde max değerleri eklenebilir
      };
    }, [documentSummaries]);  // documentSummaries değiştiğinde maxValues tekrar hesaplanır



{
  Header: 'Açık Net Tutar YPB', 
  accessor: 'acik_net_tutar_ypb',
  Cell: ({ value }) => (
    <HeatMap value={value} maxValue={maxValues.acik_net_tutar_ypb}>
      <FormatNumber value={value} className='open-order-doc-sum__td--numeric' />
    </HeatMap>
  ),
  disableFilters: true
},



*/