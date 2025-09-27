/* eslint-disable react/jsx-key */
// frontend/src/components/TotalRisk/containers/TotalRiskTable.js
import React, { useMemo } from 'react';
import { useTable, useSortBy, useFilters, usePagination} from 'react-table';
import useTotalRisk from '../hooks/useTotalRisk'; 
import ColumnFilter from '../utils/ColumnFilter';
import useUpperTotal from '../utils/UpperTotal';
import Pagination from '../utils/Pagination';
import FormatNumber from '../utils/FormatNumber'; 
import useDynamicSubtotals from '../utils/DynamicSubTotal';
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
    { Header: 'Satici', accessor: 'satici', Filter: ColumnFilter },
    { Header: 'Grup', accessor: 'grup', Filter: ColumnFilter },
    { Header: 'Muhatap Kod', accessor: 'muhatap_kod', Filter: ColumnFilter,
     },
     {
        Header: 'Müşteri Adı',
        accessor: 'muhatap_ad',
        Filter: ColumnFilter,
        /* ✅ 30 karakter + tooltip + ellipsis */
        Cell: ({ value }) => {
          if (!value) return null;
          const truncated = value.length > 35
            ? `${value.slice(0, 35)}…`
            : value;
          return (
            <span
              /* tam metin */
              title={value}
              /* mevcut hücre stile ek olarak ellipsis sınıfı */
              className="total-risk-table__td--muhatap-ad total-risk-table__ellipsis"
            >
              {truncated}
            </span>
          );
        },
    },
    { 
      Header: () => <>Bakiye <FormatNumber value={uptotals.bakiye} /></>, 
      accessor: 'bakiye', 
      disableFilters: true, 
      Cell: ({ value }) => <div style={{ textAlign: 'right' }}><FormatNumber value={value} /></div>,
      sortType: 'numeric'
    },
    { 
      Header: () => <>Açık Teslimat <FormatNumber value={uptotals.acik_teslimat} /></>, 
      accessor: 'acik_teslimat', 
      disableFilters: true, 
      Cell: ({ value }) => <div style={{ textAlign: 'right' }}><FormatNumber value={value} /></div>,
      sortType: 'numeric'
    },
    { 
      Header: () => <>Açık Sipariş <FormatNumber value={uptotals.acik_siparis} /></>, 
      accessor: 'acik_siparis', 
      disableFilters: true, 
      Cell: ({ value }) => <div style={{ textAlign: 'right' }}><FormatNumber value={value} /></div>,
      sortType: 'numeric'
    },
    { 
      Header: () => <>Avans Bakiye <FormatNumber value={uptotals.avans_bakiye} /></>, 
      accessor: 'avans_bakiye', 
      disableFilters: true, 
      Cell: ({ value }) => <div style={{ textAlign: 'right' }}><FormatNumber value={value} /></div>,
      sortType: 'numeric'
    },
    { 
      Header: () => <>Toplam Risk <FormatNumber value={uptotals.toplam_risk} /></>, 
      accessor: 'toplam_risk', 
      disableFilters: true, 
      Cell: ({ value }) => <div style={{ textAlign: 'right' }}><FormatNumber value={value} /></div>,
      sortType: 'numeric'
    }
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
            id: 'bakiye', // Sıralamak istediğiniz sütunun accessor'ı
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
      <div>
      <div className="totalrisk-pagination__controls "> 
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
            <td className="footer-cell" colSpan={4}>Dinamik Alt Toplam: </td>
            <td className="footer-cell"><FormatNumber value={subtotals['bakiye']} /></td>
            <td className="footer-cell"><FormatNumber value={subtotals['acik_teslimat']} /></td>
            <td className="footer-cell"><FormatNumber value={subtotals['acik_siparis']} /></td>
            <td className="footer-cell"><FormatNumber value={subtotals['avans_bakiye']} /></td>
            <td className="footer-cell"><FormatNumber value={subtotals['toplam_risk']} /></td>
          </tr>
        </tfoot>
      </table>
    </>
  ); 
};

export default TotalRiskTable;



