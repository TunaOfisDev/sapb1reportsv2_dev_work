// frontend/src/components/SupplierPayment/containers/SupplierPaymentTable.js
import React, { useMemo } from 'react';
import { useTable, useSortBy, useFilters, usePagination } from 'react-table';
import Pagination from '../utils/Pagination';
import ColumnFilter from '../utils/ColumnFilter';
import FormatNumber from '../utils/FormatNumber';
import useSupplierPayment from '../hooks/useSupplierPayment';
import useUpperTotal from '../utils/UpperTotal';
import DynamicButtonFilters from '../utils/DynamicButtonFilters';
import absSort from '../utils/SortNumber'; // Import the custom sort
import '../css/SupplierPaymentTable.css';
import '../css/DynamicButtonFilters.css';

const monthNames = {
  "01": "Ocak",
  "02": "Şubat",
  "03": "Mart",
  "04": "Nisan",
  "05": "Mayıs",
  "06": "Haziran",
  "07": "Temmuz",
  "08": "Ağustos",
  "09": "Eylül",
  "10": "Ekim",
  "11": "Kasım",
  "12": "Aralık"
};

const calculateFooterTotal = (rows, columnId) => {
  return rows.reduce((sum, row) => {
    const value = row.values[columnId];
    return sum + (parseFloat(value) || 0);
  }, 0);
};

const formatMonthHeader = (yearMonth) => {
  if (!yearMonth || yearMonth === 'oncesi') return 'Öncesi';
  const [year, month] = yearMonth.split('-');
  return `${monthNames[month]} ${year}`;
};


const SupplierPaymentTable = () => {
  const { localDbSupplierPayments } = useSupplierPayment();
  const subtotals = useUpperTotal(localDbSupplierPayments);

  // Define custom sort types
  const sortTypes = useMemo(() => ({
    absSort: absSort
  }), []);

  const dynamicMonthColumns = useMemo(() => {
    if (!localDbSupplierPayments.length) return [];

    const monthColumns = Object.keys(localDbSupplierPayments[0]?.monthly_balances || {})
      .filter(month => month !== 'oncesi')
      .sort((a, b) => {
        const [yearA, monthA] = a.split('-');
        const [yearB, monthB] = b.split('-');
        if (yearA === yearB) {
          return monthA.localeCompare(monthB);
        }
        return yearA.localeCompare(yearB);
      });

    return monthColumns.map((month) => ({
      Header: () => (
        <div style={{ textAlign: 'right' }}>
          {formatMonthHeader(month)}
          <div>
            <FormatNumber value={subtotals.monthly_balances?.[month]} />
          </div>
        </div>
      ),
      accessor: `monthly_balances.${month}`,
      Cell: ({ value }) => <FormatNumber value={value} />,
      Footer: ({ rows }) => {
        const total = calculateFooterTotal(rows, `monthly_balances.${month}`);
        return <FormatNumber value={total} />;
      },
      className: 'supplier-payment__td--numeric',
      HeaderClassName: 'supplier-payment__thead--numeric-header',
      disableFilters: true,
      sortType: 'absSort' // Assign the custom sort type
    }));
  }, [localDbSupplierPayments, subtotals.monthly_balances]);

  const baseColumns = useMemo(() => [
    {
      Header: 'Cari Kod',
      accessor: 'cari_kod',
      Filter: ColumnFilter,
      disableFilters: false
    },
    {
      Header: 'Cari Ad',
      accessor: 'cari_ad',
      Filter: ColumnFilter,
      disableFilters: false
    },
    {
      Header: () => (
        <div style={{ textAlign: 'right' }}>
          Güncel Bakiye
          <div>
            <FormatNumber value={subtotals.current_balance} />
          </div>
        </div>
      ),
      accessor: 'current_balance',
      Cell: ({ value }) => <FormatNumber value={value} />,
      Footer: ({ rows }) => {
        const total = calculateFooterTotal(rows, 'current_balance');
        return <FormatNumber value={total} />;
      },
      className: 'supplier-payment__td--numeric',
      HeaderClassName: 'supplier-payment__thead--numeric-header',
      disableFilters: true,
      sortType: 'absSort' // Assign the custom sort type
    },
    {
      Header: () => (
        <div style={{ textAlign: 'right' }}>
          Öncesi
          <div>
            <FormatNumber value={subtotals.monthly_balances?.oncesi} />
          </div>
        </div>
      ),
      accessor: 'monthly_balances.oncesi',
      Cell: ({ value }) => <FormatNumber value={value} />,
      Footer: ({ rows }) => {
        const total = calculateFooterTotal(rows, 'monthly_balances.oncesi');
        return <FormatNumber value={total} />;
      },
      className: 'supplier-payment__td--numeric',
      HeaderClassName: 'supplier-payment__thead--numeric-header',
      disableFilters: true,
      sortType: 'absSort' // Assign the custom sort type
    }
  ], [subtotals]);

  const columns = useMemo(() => [...baseColumns, ...dynamicMonthColumns], 
    [baseColumns, dynamicMonthColumns]
  );

  const defaultColumn = useMemo(() => ({
    Filter: ColumnFilter,
  }), []);

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
    setFilter,
    state: { pageIndex, pageSize }
  } = useTable(
    {
      columns,
      data: localDbSupplierPayments,
      defaultColumn,
      sortTypes, // Add the custom sort types to the table
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

  return (
    <div>
      <div className="supplier-payment__controls-wrapper">
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
        <DynamicButtonFilters setFilter={setFilter} />
      </div>
      <div className="supplier-payment__table-container">
        <table {...getTableProps()} className="supplier-payment__table">
          <thead className="supplier-payment__thead--header">
            {headerGroups.map(headerGroup => (
              <tr {...headerGroup.getHeaderGroupProps()}>
                {headerGroup.headers.map(column => (
                  <th 
                    {...column.getHeaderProps(column.getSortByToggleProps())} 
                    className={`${column.className} ${column.HeaderClassName || ''}`}
                  >
                    <div>
                      {column.render('Header')}
                      <span>
                        {column.isSorted ? (column.isSortedDesc ? ' ↓' : ' ↑') : ''}
                      </span>
                    </div>
                    {column.canFilter ? column.render('Filter') : null}
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
                    <td {...cell.getCellProps()} className={cell.column.className}>
                      {cell.render('Cell')}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
          <tfoot>
            {footerGroups.map(group => (
              <tr {...group.getFooterGroupProps()}>
                <td colSpan={2} className="supplier-payment__tfoot--dynamic-subtotal">
                  <div style={{ textAlign: 'right', fontWeight: 'bold' }}>
                    Dinamik Alt Toplam:
                  </div>
                </td>
                {group.headers.slice(2).map((column) => (
                  <td 
                    {...column.getFooterProps()} 
                    className={`${column.className} supplier-payment__td--footer-bold`}
                  >
                    {column.render('Footer')}
                  </td>
                ))}
              </tr>
            ))}
          </tfoot>
        </table>
      </div>
    </div>
  );
};

export default SupplierPaymentTable;