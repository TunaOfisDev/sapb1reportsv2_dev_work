// frontend/src/components/TunaInsSupplierAdvanceBalance/containers/TotalRiskTable.js
import React, { useMemo } from 'react';
import { useTable, useSortBy, useFilters, usePagination} from 'react-table';
import useTotalRisk from '../hooks/useTotalRisk'; 
import ColumnFilter from '../utils/ColumnFilter';
import useUpperTotal from '../utils/UpperTotal';
import Pagination from '../utils/Pagination';
import FormatNumber from '../utils/FormatNumber'; 
import useDynamicSubtotals from '../utils/DynamicSubTotal';
import DynamicButtonFilters from '../utils/DynamicButtonFilters';
import '../css/TotalRiskTable.css';
import '../css/Pagination.css';

const TotalRiskTable = () => {
  const { localData, hanaData, loading, error } = useTotalRisk();
  

  // combinedData değişkenini useMemo ile oluştur
  const combinedData = useMemo(() => {
    return [...(Array.isArray(localData) ? localData : []), ...(Array.isArray(hanaData) ? hanaData : [])];
  }, [localData, hanaData]);

  // combinedData ile useUpperTotal hook'unu kullan
  const uptotals = useUpperTotal(combinedData);

  const defaultColumn = useMemo(() => ({
    Filter: ColumnFilter
  }), []);

  const numericSort = (rowA, rowB, columnId) => {
    const valA = parseFloat(rowA.values[columnId]) || 0;
    const valB = parseFloat(rowB.values[columnId]) || 0;
    return valA - valB;
  };

  const columns = useMemo(() => [

    { Header: 'Tedarikci Kod', accessor: 'muhatap_kod', Filter: ColumnFilter,
     },
    {
      Header: 'Tedarikci Adı',
      accessor: 'muhatap_ad',
      Filter: ColumnFilter, 
      Cell: ({ value }) => (
        <span className="total-risk-table__td--muhatap-ad">
          {value}
        </span>
      ),

    },
    { 
      Header: () => <>Avans Bakiye <FormatNumber value={uptotals.avans_bakiye} /></>, 
      accessor: 'avans_bakiye', 
      disableFilters: true, 
      Cell: ({ value }) => <div style={{ textAlign: 'right' }}><FormatNumber value={value} /></div>,
      sortType: 'numeric'
    },

  ], [uptotals]);
  
  // TotalRiskTable.js içinde data değişkenini useMemo ile oluştur
  const data = useMemo(() => {
    const safeLocalData = Array.isArray(localData) ? localData : [];
    const safeHanaData = Array.isArray(hanaData) ? hanaData : [];
    return [...safeLocalData, ...safeHanaData];
  }, [localData, hanaData]);
 
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
    rows, // filtreden geçirilmiş ve ekranda gösterilen satırlar
    setFilter,
  } = useTable(
    {
      columns,
      data, // Burada combinedData yerine data değişkenini kullanıyoruz
      defaultColumn, // Filtre için varsayılan yapılandırmayı kullanın
      initialState: {
        pageIndex: 0,
        pageSize: 20,
        sortBy: [
          {
            id: 'avans_bakiye', // Sıralamak istediğiniz sütunun accessor'ı
            desc: true, // Azalan sıralama için true olarak ayarlayın
          },
        ],
      },
      sortTypes: {
        numeric: numericSort,
      }
    },
    useFilters,
    useSortBy,
    usePagination
  );
  

const subtotals = useDynamicSubtotals(rows, 'muhatap_kod', ['bakiye', 'acik_teslimat', 'acik_siparis','avans_bakiye', 'toplam_risk']);

   // Yükleme ve hata durumlarını kontrol et
   if (loading) return <div className="loading-message">Yükleniyor...</div>;
   if (error) return <div className="error-message">Hata: {error.message}</div>;

   return (
    <>

      <div className="totalrisk-controls-container">
        <div className="totalrisk-pagination__controls"> 
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
        </div>
        <div className="totalrisk-controls-right">
          <DynamicButtonFilters setFilter={setFilter} />
        </div>
      </div>

      <table {...getTableProps()} className="total-risk-table">
        <thead className="total-risk-table__head">
          {headerGroups.map(headerGroup => (
            <tr {...headerGroup.getHeaderGroupProps()} className="total-risk-table__row">
              {headerGroup.headers.map(column => (
                <th {...column.getHeaderProps()} className="total-risk-table__cell">
                  <div className="total-risk-table__header-content">
                    <span {...(column.canSort ? column.getSortByToggleProps() : {})}>
                      {column.render('Header')}
                    </span>
                    {column.isSorted ? (column.isSortedDesc ? ' ↓' : ' ↑') : ''}
                  </div>
                  {column.canFilter ? (
                    <div className="totalrisk-columnfilter-container">{column.render('Filter')}</div>
                  ) : null}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody {...getTableBodyProps()} className="total-risk-table__body">
          {page.map(row => {
            prepareRow(row);
            return (
              <tr {...row.getRowProps()} className="total-risk-table__row">
                {row.cells.map(cell => (
                  <td {...cell.getCellProps()} className="total-risk-table__cell">
                    {cell.render('Cell')}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
        <tfoot>
  <tr>
    <td className="footer-cell" colSpan={2}>Dinamik Alt Toplam:</td>
    <td className="footer-cell"><FormatNumber value={subtotals['avans_bakiye']} /></td>
  </tr>
</tfoot>

      </table>
    </>
  ); 
};

export default TotalRiskTable;



