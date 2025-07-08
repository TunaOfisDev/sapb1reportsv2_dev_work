// frontend/src/components/ProductConfig/hooks/usePCVariantTableConfig.js
import { useMemo } from 'react';
import { useSelector } from 'react-redux';
import { useTable, useSortBy, useFilters, usePagination, useGlobalFilter } from 'react-table';
import { formatPrice, formatDate } from '../utils/pcHelpers';
import { selectCurrency } from '../store/pcSettingsSlice';
import PCButton from '../common/PCButton';

/**
* Varyant tablosu için özel konfigürasyon hook'u
* @param {Array} variants - Tablo verileri
* @param {Function} onShowDetail - Detay gösterme handler'ı
* @returns {Object} Table instance ve konfigürasyon
*/
export const usePCVariantTableConfig = (variants, onShowDetail) => {
   // Currency konfigürasyonunu redux'tan al
   const currencyConfig = useSelector(selectCurrency);

   // Kolon tanımlamaları
   const columns = useMemo(
       () => [
           {
               Header: 'ID',
               accessor: 'id',
               Cell: ({ value }) => `#${value}`,
               sortType: 'number'
           },
           {
               Header: 'Proje Adı',
               accessor: 'project_name',
               Cell: ({ value }) => value || '-',
               sortType: 'alphanumeric',
               filter: 'includes'
           },
           {
               Header: 'Varyant Kodu',
               accessor: 'variant_code',
               Cell: ({ value }) => value || '-',
               sortType: 'alphanumeric',
               filter: 'includes'
           },
           {
               Header: 'Açıklama',
               accessor: 'variant_description',
               Cell: ({ value }) => value || '-',
               sortType: 'alphanumeric',
               filter: 'includes'
           },
           {
            Header: 'Eski Bileşen Kodları',
            accessor: 'old_component_codes',
            Cell: ({ value }) => {
                if (Array.isArray(value) && value.length > 0) {
                    return value.join(", "); // Kodları virgülle birleştir
                }
                return '-'; // Eğer boşsa "-" göster
            },
            sortType: 'alphanumeric',
            filter: 'includes'
            },
      
           {
               Header: 'Toplam Fiyat',
               accessor: 'total_price',
               Cell: ({ value }) => formatPrice(value || 0, currencyConfig), // currencyConfig eklendi
               sortType: 'number'
           },
           {
            Header: 'Oluşturulma Tarihi',
            accessor: 'created_at',
            Cell: ({ value }) => value ? formatDate(new Date(value)) : '-',
            sortType: (a, b) => new Date(a.values.created_at) - new Date(b.values.created_at)
           },
           {
               Header: 'İşlemler',
               id: 'actions',
               Cell: ({ row }) => (
                   <div className="flex space-x-2">
                       <PCButton 
                           onClick={() => onShowDetail(row.original)} 
                           variant="secondary"
                           size="small"
                       >
                           Detaylar
                       </PCButton>
                   </div>
               )
           }
       ],
       [onShowDetail, currencyConfig] // currencyConfig dependency'ye eklendi
   );

   // Tablo instance'ı oluştur
   const tableInstance = useTable(
       {
           columns,
           data: variants,
           initialState: { 
               pageIndex: 0, 
               pageSize: 10,
               sortBy: [{ id: 'created_at', desc: true }]
           }
       },
       useGlobalFilter,
       useFilters,
       useSortBy,
       usePagination
   );

   return {
       ...tableInstance,
       columns,
       initialState: tableInstance.state
   };
};