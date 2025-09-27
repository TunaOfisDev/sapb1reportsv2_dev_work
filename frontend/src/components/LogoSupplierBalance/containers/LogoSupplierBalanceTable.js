// frontend/src/components/LogoSupplierBalance/containers/LogoSupplierBalanceTable.js
import React, { useMemo } from 'react';
import { useTable, useSortBy, useFilters, usePagination } from 'react-table';
import ColumnFilter from '../utils/ColumnFilter';
import Pagination from '../utils/Pagination';
import FormatNumber from '../utils/FormatNumber';
import useDynamicSubtotals from '../utils/DynamicSubTotal';
import '../css/LogoSupplierBalanceTable.css';

const LogoSupplierBalanceTable = ({ data }) => {
  const defaultColumn = useMemo(() => ({
    Filter: ColumnFilter,
  }), []);

  const numericSort = (rowA, rowB, columnId) => {
    const valA = parseFloat(rowA.values[columnId]) || 0;
    const valB = parseFloat(rowB.values[columnId]) || 0;
    return valA - valB;
  };

  const columns = useMemo(() => [
    { Header: 'Cari Kodu', accessor: 'cari_kodu', Filter: ColumnFilter },
    { Header: 'Cari Açıklaması', accessor: 'cari_aciklamasi', Filter: ColumnFilter },
    { 
      Header: 'BakiyeBorc', 
      accessor: 'bakiye_borc', 
      disableFilters: true, 
      Cell: ({ value }) => <div style={{ textAlign: 'right' }}><FormatNumber value={value} /></div>,
      sortType: 'numeric'
    },
    { 
      Header: 'BakiyeAlacak', 
      accessor: 'bakiye_alacak', 
      disableFilters: true, 
      Cell: ({ value }) => <div style={{ textAlign: 'right' }}><FormatNumber value={value} /></div>,
      sortType: 'numeric'
    },
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
    rows,
  } = useTable(
    {
      columns,
      data,
      defaultColumn,
      initialState: {
        pageIndex: 0,
        pageSize: 20,
        sortBy: [
          {
            id: 'bakiye_alacak',
            desc: true,
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

  const subtotals = useDynamicSubtotals(rows, 'cari_kodu', ['bakiye_borc', 'bakiye_alacak']);

  return (
    <>
      <div className="logo-supplier-balance__pagination">
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
      <table {...getTableProps()} className="logo-supplier-balance__table">
        <thead className="logo-supplier-balance__thead">
          {headerGroups.map(headerGroup => (
            <tr {...headerGroup.getHeaderGroupProps()} className="logo-supplier-balance__row">
              {headerGroup.headers.map(column => (
                <th {...column.getHeaderProps()} className="logo-supplier-balance__th">
                  <div className="logo-supplier-balance__header-content">
                    <span {...(column.canSort ? column.getSortByToggleProps() : {})}>{column.render('Header')}</span>
                    {column.isSorted ? (column.isSortedDesc ? ' ↓' : ' ↑') : ''}
                  </div>
                  {column.canFilter ? <div className="logo-supplier-balance__filter-container">{column.render('Filter')}</div> : null}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody {...getTableBodyProps()} className="logo-supplier-balance__body">
          {page.map(row => {
            prepareRow(row);
            return (
              <tr {...row.getRowProps()} className="logo-supplier-balance__row">
                {row.cells.map(cell => (
                  <td {...cell.getCellProps()} className="logo-supplier-balance__td">
                    {cell.render('Cell')}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
        <tfoot>
          <tr>
            <td className="footer-cell" colSpan={2}>Dinamik Alt Toplam: </td>
            <td className="footer-cell"><FormatNumber value={subtotals['bakiye_borc']} /></td>
            <td className="footer-cell"><FormatNumber value={subtotals['bakiye_alacak']} /></td>
          </tr>
        </tfoot>
      </table>
    </>
  );
};

export default LogoSupplierBalanceTable;
