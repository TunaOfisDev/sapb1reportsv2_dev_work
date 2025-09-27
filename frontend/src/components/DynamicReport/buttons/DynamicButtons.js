// frontend/src/components/DynamicReport/buttons/DynamicButtons.js
import React from 'react';

const DynamicButtons = ({ buttons }) => {
  if (!buttons || buttons.length === 0) {
    return <div>Düğmeler yok veya eksik</div>; // Eğer buttons tanımsızsa veya boşsa hata mesajı göster
  }

  // Dizi içindeki her öğeyi döngü ile işleyerek düğmeleri oluşturun
  const renderButtons = () => {
    return buttons.map((button, index) => (
      <button key={index} onClick={() => handleButtonClick(button.sqlQuery)}>
        {button.buttonText}
      </button>
    ));
  };

  // Düğme tıklandığında SQL sorgusunu çalıştıracak işlev
  const handleButtonClick = (sqlQuery) => {
    // SQL sorgusu çalıştırma işlemi burada gerçekleştirilir
    console.log(`Çalıştırılan SQL Sorgusu: ${sqlQuery}`);
  };

  return (
    <div>
      <h2>Dinamik Butonlar</h2>
      {renderButtons()}
    </div>
  );
};

export default DynamicButtons;