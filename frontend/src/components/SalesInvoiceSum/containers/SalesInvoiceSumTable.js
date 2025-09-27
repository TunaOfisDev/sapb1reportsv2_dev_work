// frontend/src/components/SalesInvoiceSum/containers/SalesInvoiceSumTable.js
import React, { useMemo } from 'react';
import { useTable, useSortBy, useFilters, usePagination } from 'react-table';
import FormatNumber from '../utils/FormatNumber';
import Pagination from '../utils/Pagination';
import ColumnFilter from '../utils/ColumnFilter';
import useUpperTotal from '../utils/UpperTotal';
import useDynamicSubtotals from '../utils/DynamicSubTotal';
import SortNumber from '../utils/SortNumber';
import '../css/SalesInvoiceSumTable.css';

const SalesInvoiceSumTable = ({ data, columnNames }) => {
  const upperTotals = useUpperTotal(data);
  
  const defaultColumn = useMemo(() => ({
    Filter: ColumnFilter
  }), []);

  const numericColumnStyle = 'sales-invoice-sum__cell sales-invoice-sum__cell--numeric';

  const columns = useMemo(() => [
    { 
      Header: 'Temsilci',
      accessor: 'representative',
      Filter: ColumnFilter,
      className: 'sales-invoice-sum__cell sales-invoice-sum__cell--representative',
      width: 50
    },
    { 
      Header: 'Grup',
      accessor: 'customer_group',
      Filter: ColumnFilter,
      className: 'sales-invoice-sum__cell sales-invoice-sum__cell--group',
      width: 50
    },
    {
      Header: 'Cari Kod',
      accessor: 'customer_code',
      Filter: ColumnFilter,
      /* 👉 hem hücre hem başlık aynı sınıf */
      className: 'sales-invoice-sum__cell sales-invoice-sum__code',
      headerClassName: 'sales-invoice-sum__code',
      /* React-Table’a da bildir */
      width: 110, minWidth: 110, maxWidth: 110,
      Cell: ({ value }) => (
        <span title={value}>
          {value?.length > 20 ? value.slice(0, 20) + '…' : value}
        </span>
      )
    },
    {
      Header: 'Cari Adı',
      accessor: 'customer_name',
      Filter: ColumnFilter,
      className: 'sales-invoice-sum__cell sales-invoice-sum__cname',
      headerClassName: 'sales-invoice-sum__cname',
      width: 150, minWidth: 150, maxWidth: 150,
      Cell: ({ value }) => (
        <span title={value}>
          {value?.length > 15 ? value.slice(0, 15) + '…' : value}
        </span>
      )
    },




    { 
      Header: () => <>Borç<FormatNumber value={upperTotals.debt_balance} /></>,
      accessor: 'debt_balance',
      Cell: ({ value }) => <FormatNumber value={value} />,
      disableFilters: true,
      className: numericColumnStyle
    },
    { 
      Header: () => <>Avans<FormatNumber value={upperTotals.advance_balance} /></>,
      accessor: 'advance_balance',
      Cell: ({ value }) => <FormatNumber value={value} />,
      disableFilters: true,
      sortType: SortNumber(true), 
      className: numericColumnStyle
    },
    { 
      Header: () => <>{columnNames.today} <FormatNumber value={upperTotals.today_total} /></>,
      accessor: 'today_total',
      Cell: ({ value }) => <FormatNumber value={value} />,
      disableFilters: true,
      className: numericColumnStyle
    },
    { 
      Header: () => <>{columnNames.yesterday} <FormatNumber value={upperTotals.yesterday_total} /></>,
      accessor: 'yesterday_total',
      Cell: ({ value }) => <FormatNumber value={value} />,
      disableFilters: true,
      className: numericColumnStyle
    },
    {
      Header: () => <>{columnNames?.dayBeforeYesterday || 'İki Gün Önce'} <FormatNumber value={upperTotals.two_days_ago_total} /></>,
      accessor: 'two_days_ago_total',
      Cell: ({ value }) => <FormatNumber value={value} />,
      disableFilters: true,
      className: numericColumnStyle
    },
    {
      Header: () => <>{columnNames?.threeDaysAgo || 'Üç Gün Önce'} <FormatNumber value={upperTotals.three_days_ago_total} /></>,
      accessor: 'three_days_ago_total',
      Cell: ({ value }) => <FormatNumber value={value} />,
      disableFilters: true,
      className: numericColumnStyle
    },
    {
      Header: () => <>{columnNames?.fourDaysAgo || 'Dört Gün Önce'} <FormatNumber value={upperTotals.four_days_ago_total} /></>,
      accessor: 'four_days_ago_total',
      Cell: ({ value }) => <FormatNumber value={value} />,
      disableFilters: true,
      className: numericColumnStyle
    },
    { 
      Header: () => <>Hafta<FormatNumber value={upperTotals.weekly_total} /></>,
      accessor: 'weekly_total',
      Cell: ({ value }) => <FormatNumber value={value} />,
      disableFilters: true,
      className: numericColumnStyle
    },
    { 
      Header: () => <>Bu Ay<FormatNumber value={upperTotals.monthly_total} /></>,
      accessor: 'monthly_total',
      Cell: ({ value }) => <FormatNumber value={value} />,
      disableFilters: true,
      className: numericColumnStyle
    },
    { 
      Header: () => <>Geçen Ay<FormatNumber value={upperTotals.last_month_total} /></>,
      accessor: 'last_month_total',
      Cell: ({ value }) => <FormatNumber value={value} />,
      disableFilters: true,
      className: numericColumnStyle
    },
    { 
      Header: () => <>{columnNames.thisYear} <FormatNumber value={upperTotals.yearly_total} /></>,
      accessor: 'yearly_total',
      Cell: ({ value }) => <FormatNumber value={value} />,
      disableFilters: true,
      className: numericColumnStyle
    },
    { 
      Header: () => <>AçıkSipariş<FormatNumber value={upperTotals.open_orders_total} /></>,
      accessor: 'open_orders_total',
      Cell: ({ value }) => <FormatNumber value={value} />,
      disableFilters: true,
      className: numericColumnStyle
    },
    { 
      Header: () => <>AçıkSevkiyat<FormatNumber value={upperTotals.open_shipments_total} /></>,
      accessor: 'open_shipments_total',
      Cell: ({ value }) => <FormatNumber value={value} />,
      disableFilters: true,
      className: numericColumnStyle
    },
  /*  { 
      Header: () => <>Fatura Sayısı <FormatNumber value={upperTotals.invoice_count} /></>,
      accessor: 'invoice_count',
      Cell: ({ value }) => value,
      disableFilters: true,
      className: numericColumnStyle
    },*/
  ], [upperTotals, columnNames, numericColumnStyle]);

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
    rows
  } = useTable(
    {
      columns,
      data,
      defaultColumn,
      initialState: { 
        pageIndex: 0, 
        pageSize: 20,
        sortBy: [{ id: 'yearly_total', desc: true }]
      }
    },
    useFilters,
    useSortBy,
    usePagination
  );

  const subtotals = useDynamicSubtotals(rows, [
    'debt_balance',
    'advance_balance',
    'today_total',
    'yesterday_total',
    'two_days_ago_total',
    'three_days_ago_total',
    'four_days_ago_total',
    'weekly_total',
    'monthly_total',
    'last_month_total',
    'yearly_total',
    'open_orders_total',
    'open_shipments_total',
    'invoice_count'
  ]);

  return (
    <div className="sales-invoice-sum">
      <div className="sales-invoice-sum__pagination">
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
      
      <div className="sales-invoice-sum__table-container">
        <table {...getTableProps()} className="sales-invoice-sum__table">
          <thead className="sales-invoice-sum__header">
            {headerGroups.map(headerGroup => (
              <tr {...headerGroup.getHeaderGroupProps()} className="sales-invoice-sum__row">
                {headerGroup.headers.map(column => (
                 <th
                    {...column.getHeaderProps(column.getSortByToggleProps())}
                    className={`sales-invoice-sum__header-cell ${column.headerClassName || ''}`}
                  >
                      <div className="sales-invoice-sum__header-content">
                      <span className="sales-invoice-sum__header-text">
                        {column.render('Header')}
                        {column.isSorted && (
                          <span className="sales-invoice-sum__sort-indicator">
                            {column.isSortedDesc ? ' ↓' : ' ↑'}
                          </span>
                        )}
                      </span>
                    </div>
                    {column.canFilter && (
                      <div className="sales-invoice-sum__filter">
                        {column.render('Filter')}
                      </div>
                    )}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          
          <tbody {...getTableBodyProps()} className="sales-invoice-sum__body">
            {page.map(row => {
              prepareRow(row);
              return (
                <tr {...row.getRowProps()} className="sales-invoice-sum__row">
                  {row.cells.map(cell => (
                    <td 
                      {...cell.getCellProps()}
                      className={`sales-invoice-sum__cell ${cell.column.className || ''}`}
                    >
                      {cell.render('Cell')}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
          
          <tfoot className="sales-invoice-sum__footer">
            <tr className="sales-invoice-sum__row">
              <td 
                colSpan={4}
                className="sales-invoice-sum__footer-cell sales-invoice-sum__footer-cell--label"
              >
                Dinamik Alt Toplam:
              </td>
              {Object.entries(subtotals).map(([key, value]) => (
                <td
                  key={key}
                  className="sales-invoice-sum__footer-cell sales-invoice-sum__footer-cell--numeric"
                >
                  <FormatNumber value={value} />
                </td>
              ))}
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );
};

export default SalesInvoiceSumTable;