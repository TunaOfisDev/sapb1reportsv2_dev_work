// frontend/src/components/SalesOrderDetail/Container/SalesOrderDetailTable.js
import React, { useMemo } from 'react';
import { useTable, useSortBy, useFilters, usePagination } from 'react-table';
import Pagination from '../utils/Pagination';
import FormatNumber from '../utils/FormatNumber';
import ColumnFilter from '../utils/ColumnFilter';
import ShowDetail from '../utils/ShowDetail';
import '../css/SalesOrderDetailTable.css';

const SalesOrderDetailTable = ({ salesOrderMasters, loading, error }) => {
  const defaultColumn = useMemo(() => ({
    Filter: ColumnFilter,
  }), []);

  const columns = useMemo(
    () => [
      {
        Header: 'Detay',
        id: 'detail',
        accessor: 'master_belge_giris_no', // Assuming 'master_belge_giris_no' is the correct identifier for your details
        Cell: ({ value }) => <ShowDetail masterBelgeGirisNo={value} />,
        disableSortBy: true, // Disables sorting for the detail button column
        disableFilters: true, // Disables filtering for the detail button column
        canFilter: false, // Disables filtering for the detail button column
      },
      {
        Header: 'Satici',
        accessor: 'satici',
        Filter: ColumnFilter,
      },
      {
        Header: 'Müşteri Adı',
        accessor: 'musteri_ad',
        Filter: ColumnFilter,
      },
      {
        Header: 'SipNo',
        accessor: (row) => `${row.sip_no} - ${row.belge_tur}`,
        Filter: ColumnFilter,
      },
      
      {
        Header: 'Belge Tarihi',
        accessor: 'belge_tarihi',
        Filter: ColumnFilter,
      },
      {
        Header: 'Teslim Tarihi',
        accessor: 'teslim_tarihi',
        Filter: ColumnFilter,
      },
      {
        Header: 'NetTutar(YPB)',
        accessor: 'totals.total_net_tutar_ypb',
        disableFilters: true,
        Cell: ({ value }) => <FormatNumber value={value} />,
        className: 'sales-order-detail__td--numeric',
      },
      // Diğer master alanları buraya eklenebilir
    ],
    []
  );

  const data = useMemo(() => salesOrderMasters || [], [salesOrderMasters]);

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    prepareRow,
    page,
    canPreviousPage,
    canNextPage,
    pageCount,
    gotoPage,
    nextPage,
    previousPage,
    setPageSize,
    state: { pageIndex, pageSize },
  } = useTable(
    {
      columns,
      data,
      defaultColumn,
      initialState: { pageIndex: 0, pageSize: 20 },
    },
    useFilters,
    useSortBy,
    usePagination
  );

  if (loading) return <div>Yükleniyor...</div>;
  if (error) return <div>Hata: {error.message}</div>;

  return (
    <>
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
      <table {...getTableProps()} className="sales-order-detail__table">
        <thead>
          {headerGroups.map(headerGroup => (
            <tr {...headerGroup.getHeaderGroupProps()}>
              {headerGroup.headers.map(column => (
                <th {...column.getHeaderProps()} className={`sales-order-detail__thead--header ${column.headerClassName || ''}`}>
                  <div className="header-title" {...(column.canSort ? column.getSortByToggleProps() : {})}>
                    {column.render('Header')}
                    {column.isSorted ? (column.isSortedDesc ? ' ↓' : ' ↑') : ''}
                  </div>
                  {column.canFilter ? <div className="filter-container">{column.render('Filter')}</div> : null}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody {...getTableBodyProps()}>
          {page.map(row => {
            prepareRow(row);
            return (
              <tr {...row.getRowProps()}>
                {row.cells.map(cell => (
                  <td {...cell.getCellProps()} className={cell.column.className || ''}>
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

export default SalesOrderDetailTable;

