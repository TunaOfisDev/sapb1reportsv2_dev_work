// frontend/src/components/CustomerCollection/containers/CustomerCollectionTable.js
import React, { useMemo } from 'react';
import { useTable, useSortBy, useFilters, usePagination } from 'react-table';
import FormatNumber from '../utils/FormatNumber';
import ColumnFilter from '../utils/ColumnFilter';
import Pagination from '../utils/Pagination';
import useCustomerCollection from '../hooks/useCustomerCollection';
import useUpperTotal from '../utils/UpperTotal';
import '../css/CustomerCollectionTable.css';

const CustomerCollectionTable = () => {
  const { localDbCustomerCollections } = useCustomerCollection();
  const subtotals = useUpperTotal(localDbCustomerCollections);

  const columns = useMemo(
  () => [
    {
      Header: 'Satıcı',
      accessor: 'satici',
      Filter: ColumnFilter,
      disableFilters: false,
      HeaderClassName: 'customer-collection__thead--string-header'
    },
    {
      Header: 'Grup',
      accessor: 'grup',
      Filter: ColumnFilter,
      disableFilters: false,
      HeaderClassName: 'customer-collection__thead--string-header'
    },
    {
      Header: 'Cari Kod',
      accessor: 'cari_kod',
      Filter: ColumnFilter,
      disableFilters: false,
      HeaderClassName: 'customer-collection__thead--string-header'
    },
    {
      Header: 'Cari Ad',
      accessor: 'cari_ad',
      Filter: ColumnFilter,
      disableFilters: false,
      HeaderClassName: 'customer-collection__thead--string-header'
    },

      {
        Header: () => (
          <div className="customer-collection__thead--numeric-header">
            Güncel Bakiye
            <div>
              <FormatNumber value={subtotals.current_balance} />
            </div>
          </div>
        ),
        accessor: 'current_balance',
        Cell: ({ value }) => <FormatNumber value={value} />,
        Footer: ({ rows }) => {
          const total = rows.reduce(
            (sum, row) => sum + parseFloat(row.values.current_balance || 0),
            0
          );
          return <FormatNumber value={total} />;
        },
        className: 'customer-collection__td--numeric',
        disableFilters: true,
      },
    ],
    [subtotals]
  );

  const dynamicMonthColumns = useMemo(() => {
    const monthColumns =
      localDbCustomerCollections.length > 0
        ? Object.keys(localDbCustomerCollections[0].monthly_balances)
        : [];

    return monthColumns.map((month) => ({
      Header: () => (
        <div className="customer-collection__thead--numeric-header">
          {month}
          <div>
            <FormatNumber value={subtotals.monthly_balances[month]} />
          </div>
        </div>
      ),
      accessor: `monthly_balances.${month}`,
      Cell: ({ value }) => <FormatNumber value={value} />,
      Footer: ({ rows }) => {
        const total = rows.reduce(
          (sum, row) => sum + parseFloat(row.values[`monthly_balances.${month}`] || 0),
          0
        );
        return <FormatNumber value={total} />;
      },
      className: 'customer-collection__td--numeric',
      disableFilters: true,
    }));
  }, [localDbCustomerCollections, subtotals]);

  const allColumns = useMemo(() => [...columns, ...dynamicMonthColumns], [columns, dynamicMonthColumns]);

  const defaultColumn = useMemo(() => ({
    Filter: ColumnFilter,
  }), []);

  const tableInstance = useTable(
    {
      columns: allColumns,
      data: localDbCustomerCollections,
      defaultColumn,
      initialState: { 
        pageIndex: 0, 
        pageSize: 20,
        sortBy: [{ id: 'current_balance', desc: true }] 
      },
    },
    useFilters,
    useSortBy,
    usePagination
  );

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    footerGroups,
    prepareRow,
    page,
    gotoPage,
    pageCount,
    canPreviousPage,
    canNextPage,
    nextPage,
    previousPage,
    setPageSize,
    state: { pageIndex, pageSize },
  } = tableInstance;

  return (
    <div>
      {/* Sayfalama Bileşeni */}
      <Pagination
        canPreviousPage={canPreviousPage}
        canNextPage={canNextPage}
        nextPage={nextPage}
        previousPage={previousPage}
        setPageSize={setPageSize}
        pageIndex={pageIndex}
        pageSize={pageSize}
        gotoPage={gotoPage}
        pageCount={pageCount}
      />
  

      <table {...getTableProps()} className="customer-collection__table">
     
        <thead className="customer-collection__thead--header">
  {headerGroups.map((headerGroup) => (
    <tr {...headerGroup.getHeaderGroupProps()}>
      {headerGroup.headers.map((column) => (
        <th
          {...column.getHeaderProps()}
          className={column.HeaderClassName || 'default-header-class'} // Doğru CSS sınıfını ekliyoruz
        >
          <div {...column.getSortByToggleProps()}>
            {column.render('Header')}
            <span>
              {column.isSorted ? (column.isSortedDesc ? ' ↓' : ' ↑') : ''}
            </span>
          </div>
          {column.canFilter && <div>{column.render('Filter')}</div>}
        </th>
      ))}
    </tr>
  ))}
</thead>

  
        {/* Tablo Gövdesi */}
        <tbody {...getTableBodyProps()}>
          {page.map((row) => {
            prepareRow(row);
            return (
              <tr {...row.getRowProps()}>
                {row.cells.map((cell) => (
                  <td
                    {...cell.getCellProps()}
                    className={cell.column.className}
                  >
                    {cell.render('Cell')}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
  
        {/* Tablo Alt Bilgisi */}
        <tfoot className="customer-collection__tfoot">
          {footerGroups.map((footerGroup) => (
            <tr {...footerGroup.getFooterGroupProps()}>
              <td
                colSpan={4}
                className="customer-collection__tfoot--dynamic-subtotal customer-collection__td--footer-bold"
              >
                Dinamik Alt Toplam:
              </td>
              {footerGroup.headers.slice(4).map((column) => (
                <td
                  {...column.getFooterProps()}
                  className={`${column.className} customer-collection__td--footer-bold`}
                >
                  {column.render('Footer')}
                </td>
              ))}
            </tr>
          ))}
        </tfoot>
      </table>
    </div>
  );
  
};

export default CustomerCollectionTable;
