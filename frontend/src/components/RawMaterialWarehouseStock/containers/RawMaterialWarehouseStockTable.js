// frontend/src/components/RawMaterialWarehouseStock/containers/RawMaterialWarehouseStockTable.js
import React, { useMemo, useState } from 'react';
import { useTable, useFilters, useSortBy, usePagination } from 'react-table';
import ColumnFilter from '../utils/ColumnFilter';
import Pagination from '../utils/Pagination';
import FormatNumber from '../utils/FormatNumber';
import ShowModalPurchaseOrders from '../utils/ShowModalPurchaseOrders';
import '../css/RawMaterialWarehouseStockTable.css';

const RawMaterialWarehouseStockTable = ({ 
    data, 
    isHammaddeSelected, 
    hideZeroStock, 
    handleExportFiltered,
  }) => {
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedPurchaseOrders, setSelectedPurchaseOrders] = useState('');
  const [selectedItemCode, setSelectedItemCode] = useState('');
  const [selectedItemName, setSelectedItemName] = useState('');
  const [selectedStockQuantity, setSelectedStockQuantity] = useState('');
  const [selectedOrderQuantity, setSelectedOrderQuantity] = useState(''); 
  
  const filteredData = useMemo(() => {
    let filtered = data;
    if (isHammaddeSelected !== null) {
      filtered = filtered.filter(item => item.kalem_grup_ad === "HAMMADDE" === isHammaddeSelected);
    }
    if (hideZeroStock) {
      filtered = filtered.filter(item => item.depo_stok > 0 || item.siparis_edilen_miktar > 0);
    }
    return filtered;
  }, [data, isHammaddeSelected, hideZeroStock]);

  const defaultColumn = useMemo(() => ({
    Filter: ColumnFilter
  }), []);

  const columns = useMemo(() => [
    { Header: 'KalemGrup', accessor: 'kalem_grup_ad', Filter: ColumnFilter },
    { Header: 'Kalem Kod', accessor: 'kalem_kod', Filter: ColumnFilter,
      Cell: ({ value }) => (
        <span className="raw-material-warehouse-stock-table__td--kalem-kod">
          {value}
        </span>
      ),
    },
    { Header: 'Kalem Tanım', accessor: 'kalem_tanim', Filter: ColumnFilter,
      Cell: ({ value }) => (
        <span className="raw-material-warehouse-stock-table__td--kalem-tanim">
          {value}
        </span>
      ),
    },
    { Header: 'ÖlçüBirim', accessor: 'stok_olcu_birim', Filter: ColumnFilter },
    { Header: 'DepoStok', accessor: 'depo_stok', Filter: ColumnFilter, 
      Cell: ({ value }) => <div style={{ textAlign: 'right' }}><FormatNumber value={parseFloat(value)} /></div>,
    },
    { Header: 'SiparişMiktar', accessor: 'siparis_edilen_miktar', Filter: ColumnFilter,
      Cell: ({ value, row }) => (
        <div style={{ textAlign: 'right' }}>
          <span 
            onClick={() => {
              setSelectedPurchaseOrders(row.original.verilen_siparisler);
              setSelectedItemCode(row.original.kalem_kod);
              setSelectedItemName(row.original.kalem_tanim);
              setSelectedStockQuantity(row.original.depo_stok);
              setSelectedOrderQuantity(value); 
              setModalOpen(true);
            }}
            style={{ cursor: 'pointer', textDecoration: 'underline', color: 'blue' }}
          >
            <FormatNumber value={parseFloat(value)} />
          </span>
        </div>
      ),
    },
    { Header: 'SonFiyat', accessor: 'son_satinalma_fiyat', disableFilters: true,
      Cell: ({ value }) => <div style={{ textAlign: 'right' }}><FormatNumber value={parseFloat(value)} /></div>,
    },
    { Header: 'SonFatura', accessor: 'son_satinalma_fatura_tarih', disableFilters: true, },
  ], []);

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    prepareRow,
    page,
    canPreviousPage,
    canNextPage,
    nextPage,
    previousPage,
    gotoPage,
    pageCount,
    setPageSize,
    state: { pageIndex, pageSize },
  } = useTable(
    {
      columns,
      data: filteredData,
      defaultColumn,
      initialState: {
        pageIndex: 0,
        pageSize: 50,
      },
    },
    useFilters,
    useSortBy,
    usePagination
  );

  const handleFilteredExport = () => {
    const filters = {};
    headerGroups.forEach(headerGroup => {
      headerGroup.headers.forEach(column => {
        if (column.filterValue) {
          filters[column.id] = column.filterValue;
        }
      });
    });
    handleExportFiltered(filters);
  };

  return (
    <>
     <ShowModalPurchaseOrders 
        isOpen={modalOpen} 
        onRequestClose={() => setModalOpen(false)} 
        purchaseOrders={selectedPurchaseOrders}
        itemCode={selectedItemCode}
        itemName={selectedItemName}
        stockQuantity={selectedStockQuantity}
        orderQuantity={selectedOrderQuantity} 
      />
      <div>
        <div className="rawmaterial-pagination__controls"> 
          <Pagination
            canNextPage={canNextPage}
            canPreviousPage={canPreviousPage}
            pageCount={pageCount}
            pageIndex={pageIndex}
            gotoPage={gotoPage}
            nextPage={nextPage}
            previousPage={previousPage}
            pageSize={pageSize}
            setPageSize={setPageSize}
          />
         <div className="raw-material-warehouse-stock-table__export-buttons">
           <button onClick={handleFilteredExport} className="export-button">
            Excel'e Aktar
           </button>
         </div>
      </div>
    </div>
    <table {...getTableProps()} className="raw-material-warehouse-stock-table">
        <thead className="raw-material-warehouse-stock-table__head">
          {headerGroups.map(headerGroup => (
            <tr {...headerGroup.getHeaderGroupProps()} className="raw-material-warehouse-stock-table__row">
              {headerGroup.headers.map(column => (
                <th {...column.getHeaderProps(column.getSortByToggleProps())} className="raw-material-warehouse-stock-table__cell">
                  <div className="raw-material-warehouse-stock-table__header-content">
                    <span>
                      {column.render('Header')}
                      {column.isSorted ? (column.isSortedDesc ? ' ↓' : ' ↑') : ''}
                    </span>
                  </div>
                  {column.canFilter ? (
                    <div className="rawmaterial-columnfilter-container">{column.render('Filter')}</div>
                  ) : null}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody {...getTableBodyProps()} className="raw-material-warehouse-stock-table__body">
          {page.map(row => {
            prepareRow(row);
            return (
              <tr {...row.getRowProps()} className="raw-material-warehouse-stock-table__row">
                {row.cells.map(cell => (
                 <td {...cell.getCellProps()} className="raw-material-warehouse-stock-table__cell" data-header={cell.column.Header}>
                 {cell.render('Cell')}
               </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </>
  );
};

export default RawMaterialWarehouseStockTable;
