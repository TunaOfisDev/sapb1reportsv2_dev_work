// frontend/src/components/BomCostManager/containers/BomCostTableContainer.js
import React, { useState, useMemo, useEffect } from 'react';
import { useTable } from 'react-table';
import useFetchBomCost from '../hooks/useFetchBomCost';
import { formatNumber } from '../utils/formatNumber';
import { calculateDetailCost } from '../utils/detailCalculateCost';
import { getMaxPositiveLevel } from '../utils/getMaxPositiveLevel';
import { getDailyRate, getAllRates } from '../utils/dailyRates';
import { executeMasterCostCalculation } from '../utils/masterCostButton';
import FactorControl from '../components/FactorControl';
import { getMainItemName } from '../utils/mainItemName';
import '../css/BomCostTableContainer.css';
import '../css/FactorControl.css';

const currencyOptions = ["TRY", "EUR", "USD", "GBP"];

// Editlenebilir hücre
const EditableCell = ({ value: initialValue, onUpdate }) => {
  // Başlangıçta formatlanmış değeri gösteriyoruz
  const [editValue, setEditValue] = useState(formatNumber(initialValue));

  const handleBlur = () => {
    // Girilen değerden bin ayıracı noktaları kaldırıp, ondalık ayıracı virgülü noktaya çeviriyoruz
    const numericValue = parseFloat(
      editValue.replace(/\./g, '').replace(',', '.')
    ) || 0;
    onUpdate(numericValue);
    // Geri dönüşte değeri formatlanmış şekilde güncelliyoruz
    setEditValue(formatNumber(numericValue));
  };

  return (
    <input
      className="bom-cost-table__input numeric-cell"
      type="text" // type "text" olarak ayarlandı, spinner oklar kaldırıldı
      value={editValue}
      onChange={(e) => setEditValue(e.target.value)}
      onBlur={handleBlur}
    />
  );
};

// Editlenebilir döviz seçimi
const EditableSelect = ({ value: initialValue, onUpdate }) => {
  const [selectedValue, setSelectedValue] = useState(initialValue);
  const handleChange = (e) => {
    const newValue = e.target.value;
    setSelectedValue(newValue);
    onUpdate(newValue);
  };
  return (
    <select className="bom-cost-table__select" value={selectedValue} onChange={handleChange}>
      {currencyOptions.map((currency) => (
        <option key={currency} value={currency}>
          {currency}
        </option>
      ))}
    </select>
  );
};

// Sadece sayısal alanları formatlayan bileşen
const ReadOnlyNumberCell = ({ value }) => <>{formatNumber(value)}</>;

const BomCostTableContainer = () => {
  const { bomComponents, loading, error } = useFetchBomCost();

  // Master faktörler
  const [laborMultiplier, setLaborMultiplier] = useState(1);
  const [overheadMultiplier, setOverheadMultiplier] = useState(1);
  const [licenseMultiplier, setLicenseMultiplier] = useState(1);
  const [commissionMultiplier, setCommissionMultiplier] = useState(1);

  // Master maliyet hesaplaması sonucu
  const [updatedMasterCost, setUpdatedMasterCost] = useState(0);

  // Günlük kurlar state (dinamik olarak API'den alınacak)
  const [dailyRatesMapping, setDailyRatesMapping] = useState({ TRY: 1 });
  const [ratesLoading, setRatesLoading] = useState(true);
  const [ratesError, setRatesError] = useState(null);
  
  // BOM verisi için state
  const [defaultedData, setDefaultedData] = useState([]);

  // Dinamik günlük kurların çekilmesi (ilk yüklemede)
  useEffect(() => {
    async function fetchRates() {
      try {
        setRatesLoading(true);
        
        // Tüm kurları tek seferde al (performans için)
        const allRates = await getAllRates();
        
        if (allRates) {
          setDailyRatesMapping(allRates);
          console.log("Döviz kurları yüklendi:", allRates);
        } else {
          setRatesError("Döviz kurları alınamadı. Varsayılan değerler kullanılıyor.");
        }
      } catch (error) {
        console.error("Döviz kurları alınırken hata:", error);
        setRatesError("Döviz kurları alınamadı: " + error.message);
      } finally {
        setRatesLoading(false);
      }
    }
    
    fetchRates();
  }, []);

  // En büyük BOM seviyesi
  const maxLevel = useMemo(() => getMaxPositiveLevel(bomComponents), [bomComponents]);
  
  // BOM verisi değiştiğinde defaultedData'yı güncelle
  useEffect(() => {
    if (bomComponents && bomComponents.length > 0) {
      const initializedData = bomComponents.map(comp => {
        // Burada dönüşüm yapmıyoruz, direk orijinal değerleri kullanıyoruz
        const newPrice = comp.new_last_purchase_price || comp.last_purchase_price;
        const newCurrency = comp.new_currency || comp.currency || 'TRY';
        return {
          ...comp,
          new_last_purchase_price: newPrice,
          new_currency: newCurrency
        };
      });
      setDefaultedData(initializedData);
    }
  }, [bomComponents]);

  // Tabloda override yapıldığında güncelleme
  const handleUpdate = async (index, key, value) => {
    // Önce mevcut veriyi kopyala
    const updatedData = [...defaultedData];
    
    // Değeri doğrudan kaydet
    updatedData[index][key] = value;
    
    // Eğer "new_currency" alanı güncellenirse, kur değerini kontrol et
    if (key === "new_currency") {
      // Eğer bu para birimi için kur henüz yoksa, al
      if (!dailyRatesMapping[value]) {
        try {
          const rate = await getDailyRate(value);
          if (rate) {
            setDailyRatesMapping(prev => ({ ...prev, [value]: rate }));
          }
        } catch (error) {
          console.error(`${value} için kur alınırken hata:`, error);
        }
      }
    }
    
    // Güncellenmiş veriyi state'e kaydet
    setDefaultedData(updatedData);
    
    console.log(`Satır ${index} güncellendi, ${key}: ${value}, Döviz: ${updatedData[index].new_currency}`);
  };

  // Master maliyet hesaplaması için faktörler
  const masterFactors = {
    laborMultiplier,
    overheadMultiplier,
    licenseMultiplier,
    commissionMultiplier
  };

  // Butona basıldığında çalışacak fonksiyon
  const handleMasterCalculate = () => {
    // executeMasterCostCalculation fonksiyonunu çağır
    const result = executeMasterCostCalculation(
      defaultedData, 
      dailyRatesMapping, 
      masterFactors,
      (value) => setUpdatedMasterCost(Number(value).toFixed(2))
    );
    
    console.log("Hesaplama sonucu:", result);
  };

  // Kurlar yüklenirken bilgi göster
  const ratesInfo = ratesLoading ? (
    <div className="rates-loading">Günlük kurlar yükleniyor...</div>
  ) : ratesError ? (
    <div className="rates-error">{ratesError}</div>
  ) : (
    <div className="rates-success">
      <strong>Günlük Kurlar:</strong> USD: {formatNumber(dailyRatesMapping.USD)}, 
      EUR: {formatNumber(dailyRatesMapping.EUR)}, 
      GBP: {formatNumber(dailyRatesMapping.GBP)} TRY
    </div>
  );

  // Master alan için ana ürün kodu ve ana ürün adı
  const masterItemCode = defaultedData.length > 0 ? defaultedData[0].main_item : "Yükleniyor...";
  const mainName = getMainItemName(bomComponents);



  /**
   * Master alanı:
   *  1) Ana Ürün Bilgileri (3/6)
   *  2) Satış Bilgileri (1/6)
   *  3) Maliyet Hesaplama (2/6)
   */
  const masterFields = (
    <div className="bom-master-container">
      {/* 1. Bölüm (3/6): Ana Ürün Bilgileri */}
      <div className="bom-master__main-item">
        <div className="bom-master__section-header">Ana Ürün Bilgileri</div>
        <div className="bom-master__info-row">
          <label>Ana Ürün Kodu:</label>
          <span>{masterItemCode}</span>
        </div>
        <div className="bom-master__info-row">
          <label>Ana Ürün Adı:</label>
          <span>{mainName}</span>
        </div>
      </div>

      {/* 2. Bölüm (1/6): Satış Bilgileri */}
      <div className="bom-master__sales">
        <div className="bom-master__section-header">Satış Bilgileri</div>
        {defaultedData.length > 0 && (
          <>
            <div className="bom-master__info-row">
              <label>Satış Fiyatı:</label>
              <span>{formatNumber(defaultedData[0].sales_price)}</span>
            </div>
            <div className="bom-master__info-row">
              <label>Satış Para Birimi:</label>
              <span>{defaultedData[0].sales_currency}</span>
            </div>
            <div className="bom-master__info-row">
              <label>Fiyat Listesi:</label>
              <span>{defaultedData[0].price_list_name || "YOK"}</span>
            </div>
          </>
        )}
        <div className="bom-master__info-row">
          {ratesInfo}
        </div>
      </div>

      {/* 3. Bölüm (2/6): Maliyet Hesaplama */}
      <div className="bom-master__cost">
        <div className="bom-master__section-header">Maliyet Hesaplama</div>
        <div className="bom-master__factor-controls">
          <FactorControl 
            label="İşçilik Çarpanı"
            value={laborMultiplier}
            onChange={setLaborMultiplier}
          />
          <FactorControl 
            label="Genel Üretim Çarpanı"
            value={overheadMultiplier}
            onChange={setOverheadMultiplier}
          />
          <FactorControl 
            label="Lisans Çarpanı"
            value={licenseMultiplier}
            onChange={setLicenseMultiplier}
          />
          <FactorControl 
            label="Komisyon Çarpanı"
            value={commissionMultiplier}
            onChange={setCommissionMultiplier}
          />
        </div>
        <button 
          className="bom-master__calculate-button"
          onClick={handleMasterCalculate}
        >
          Maliyeti Hesapla
        </button>
        <div className="bom-master__total-cost">
          Toplam Güncellenmiş Maliyet: {formatNumber(updatedMasterCost)} TRY
        </div>
      </div>
    </div>
  );
    

  const columns = useMemo(() => [
    { Header: 'Alt Ürün', accessor: 'sub_item', className: 'col-sub-item text-left' },
    { Header: 'Bileşen Kodu', accessor: 'component_item_code', className: 'col-code text-left' },
    { Header: 'Miktar', accessor: 'quantity', Cell: ReadOnlyNumberCell, className: 'col-quantity' },
    { Header: 'Son Satın Alma', accessor: 'last_purchase_price', Cell: ReadOnlyNumberCell, className: 'col-last-purchase-price' },
    { Header: 'Para Birimi', accessor: 'currency', className: 'col-currency' },
    { Header: 'Döviz Kuru', accessor: 'rate', Cell: ReadOnlyNumberCell, className: 'col-rate' },
    
    { Header: 'Belge Tarihi', accessor: 'doc_date', className: 'col-doc-date' },
    { Header: 'Bileşen Maliyeti UPB', accessor: 'component_cost_upb', Cell: ReadOnlyNumberCell, className: 'col-component-cost-upb' },
 
    {
      Header: 'Yeni Fiyat',
      accessor: 'new_last_purchase_price',
      Cell: ({ row, value }) => {
        if (Number(row.original.level) < maxLevel) {
          return <span>{formatNumber(value)}</span>;
        }
        return (
          <EditableCell
            value={value}
            onUpdate={(val) => handleUpdate(row.index, 'new_last_purchase_price', val)}
          />
        );
      },
      className: 'col-new-last-purchase-price'
    },
    {
      Header: 'Yeni Döviz',
      accessor: 'new_currency',
      Cell: ({ row, value }) => {
        if (Number(row.original.level) < maxLevel) {
          return <span>{value}</span>;
        }
        return (
          <EditableSelect
            value={value}
            onUpdate={(val) => handleUpdate(row.index, 'new_currency', val)}
          />
        );
      },
      className: 'col-new-currency'
    },
    {
      Header: 'Günlük Kur',
      id: 'daily_rate',
      Cell: ({ row }) => {
        const currency = row.original.new_currency || row.original.currency || 'TRY';
        const rate = dailyRatesMapping[currency] || 1;
        return <ReadOnlyNumberCell value={rate} />;
      },
      className: 'col-daily-rate'
    },
    {
      Header: 'Güncel Maliyet',
      id: 'current_cost',
      Cell: ({ row }) => {
        const currentCost = calculateDetailCost(row.original, maxLevel, dailyRatesMapping);
        return <ReadOnlyNumberCell value={currentCost} />;
      },
      className: 'col-current-cost'
    },
    
    { Header: 'Fiyat Kaynağı', accessor: 'price_source', className: 'col-price-source' },
    { Header: 'Ürün Grubu', accessor: 'item_group_name', className: 'col-item-group-name' },
    { Header: 'BOM Seviyesi', accessor: 'level', Cell: ReadOnlyNumberCell, className: 'col-level text-left' },
  ], [defaultedData, maxLevel, dailyRatesMapping]);

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    rows,
    prepareRow
  } = useTable({ columns, data: defaultedData });

  if (loading) return <p>Yükleniyor...</p>;
  if (error) return <p>Hata: {error}</p>;

  return (
    <div className="bom-cost-table-container">
      {/* Başlık */}
      <h2 className="bom-cost-table-container__header">BOM Maliyet Tablosu</h2>
  
      {/* Master Alanlar */}
      {masterFields}
  
      {/* Tablo */}
      <table className="bom-cost-table" {...getTableProps()}>
        {/* Tablo Başlıkları */}
        <thead>
          {headerGroups.map(headerGroup => (
            <tr
              {...headerGroup.getHeaderGroupProps()}
              className="bom-cost-table__header-row"
            >
              {headerGroup.headers.map(column => (
                <th
                  {...column.getHeaderProps()}
                  className={`bom-cost-table__header-cell ${column.className || ''}`}
                >
                  {column.render('Header')}
                </th>
              ))}
            </tr>
          ))}
        </thead>
  
        {/* Tablo İçeriği */}
        <tbody {...getTableBodyProps()}>
          {rows.map(row => {
            prepareRow(row);
            return (
              <tr
                {...row.getRowProps()}
                className="bom-cost-table__row"
              >
                {row.cells.map(cell => (
                  <td
                    {...cell.getCellProps()}
                    className={`bom-cost-table__cell ${cell.column.className || ''}`}
                  >
                    {cell.render('Cell')}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default BomCostTableContainer;