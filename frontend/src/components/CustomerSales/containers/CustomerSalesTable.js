// frontend/src/components/CustomerSales/containers/CustomerSalesTable.js
import React, { useMemo, useEffect, useState } from 'react';
import { useTable, useSortBy, useFilters, usePagination } from 'react-table';
import Pagination from '../utils/Pagination';
import FormatNumber from '../utils/FormatNumber';
import ColumnFilter from '../utils/ColumnFilter';
import DynamicSubTotal from '../utils/DynamicSubTotal';
import CardCodeCount from '../utils/CardCodeCount'; 
import RatioToTotalSales from '../utils/RatioToTotalSales';
import '../css/CustomerSalesTable.css';

const CustomerSalesTable = ({ customerSales, loading, error }) => {
  const defaultColumn = useMemo(() => ({
    Filter: ColumnFilter,
  }), []);

  const [totals, setTotals] = useState({});
  const [filteredColumns, setFilteredColumns] = useState([]);

  useEffect(() => {
    const initialTotals = {
      yillik_toplam: 0,
      ocak: 0,
      subat: 0,
      mart: 0,
      nisan: 0,
      mayis: 0,
      haziran: 0,
      temmuz: 0,
      agustos: 0,
      eylul: 0,
      ekim: 0,
      kasim: 0,
      aralik: 0,
    };

    customerSales.forEach(sale => {
      Object.keys(initialTotals).forEach(month => {
        initialTotals[month] += parseFloat(sale[month]) || 0;
      });
    });

    setTotals(initialTotals);

    // Ayları filtreleme ve sıralama
    const months = [
      { name: 'ocak', label: 'Ocak' },
      { name: 'subat', label: 'Şubat' },
      { name: 'mart', label: 'Mart' },
      { name: 'nisan', label: 'Nisan' },
      { name: 'mayis', label: 'Mayıs' },
      { name: 'haziran', label: 'Haziran' },
      { name: 'temmuz', label: 'Temmuz' },
      { name: 'agustos', label: 'Ağustos' },
      { name: 'eylul', label: 'Eylül' },
      { name: 'ekim', label: 'Ekim' },
      { name: 'kasim', label: 'Kasım' },
      { name: 'aralik', label: 'Aralık' }
    ];

    const nonEmptyMonths = months.filter(month => initialTotals[month.name] > 0).reverse();
    setFilteredColumns(nonEmptyMonths);
  }, [customerSales]);

  const columns = useMemo(
    () => [
      {
        Header: 'Grup',
        accessor: 'grup',
        Filter: ColumnFilter,
        headerClassName: 'customer-sales__thead--musteri-kodu',
      },
      {
        Header: 'Müşteri Kodu',
        accessor: 'musteri_kod',
        Filter: ColumnFilter,
        headerClassName: 'customer-sales__thead--musteri-kodu',
      },
      {
        Header: 'Müşteri Adı',
        accessor: 'musteri_ad',
        Filter: ColumnFilter,
        className: 'customer-sales__td--musteri-ad customer-sales__th--musteri-ad',
        headerClassName: 'customer-sales__thead--musteri-kodu',
        Footer: info => (
          <div style={{ textAlign: 'right' }}><strong>Dinamik Toplam: </strong></div>
        )
      },
      {
        Header: () => <>Yıl2025 <FormatNumber value={totals.yillik_toplam} /></>,
        accessor: 'yillik_toplam',
        Cell: ({ value }) => <FormatNumber value={value} />,
        className: 'customer-sales__td--numeric customer-sales__td--yillik-toplam',
        headerClassName: 'customer-sales__thead--numeric-header',
        disableFilters: true,
        Footer: info => <DynamicSubTotal data={info.rows} columnId="yillik_toplam" />
      },
      {
        Header: 'Oran%',
        accessor: 'oran',
        Cell: ({ row }) => <RatioToTotalSales value={row.values.yillik_toplam} total={totals.yillik_toplam} />,
        className: 'customer-sales__td--numeric',
        headerClassName: 'customer-sales__thead--numeric-header',
        disableFilters: true
      },
      ...filteredColumns.map(month => ({
        Header: () => <>{month.label} <FormatNumber value={totals[month.name]} /></>,
        accessor: month.name,
        Cell: ({ value }) => <FormatNumber value={value} />,
        className: 'customer-sales__td--numeric',
        headerClassName: 'customer-sales__thead--numeric-header',
        disableFilters: true,
        Footer: info => <DynamicSubTotal data={info.rows} columnId={month.name} />
      })),
    ],
    [totals, filteredColumns]
  );

  const data = useMemo(() => customerSales || [], [customerSales]);

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
    footerGroups,
  } = useTable(
    {
      columns,
      data,
      defaultColumn,
      initialState: { pageIndex: 0, pageSize: 20, sortBy: [{ id: 'yillik_toplam', desc: true }] },
    },
    useFilters,
    useSortBy,
    usePagination
  );

  if (loading) return <div>Yükleniyor...</div>;
  if (error) return <div>Hata: {error.message}</div>;

  return (
    <>
      <div className="customer-sales-container__header">
        <div className="pagination-wrapper">
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
        <div className="card-code-count-wrapper">
          <CardCodeCount />
        </div>
      </div>
      <table {...getTableProps()} className="customer-sales__table">
      <thead>
        {headerGroups.map(headerGroup => (
          <tr {...headerGroup.getHeaderGroupProps()}>
            {headerGroup.headers.map(column => (
              <th {...column.getHeaderProps()} className={`customer-sales__thead--header ${column.headerClassName || ''}`}>
                <div className="header-title" {...(column.canSort ? column.getSortByToggleProps() : {})}>
                  {column.render('Header')}
                  {column.isSorted ? (column.isSortedDesc ? ' 🔽' : ' 🔼') : ''}
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
        <tfoot>
              {footerGroups.map(group => (
                <tr {...group.getFooterGroupProps()}>
                  {group.headers.map(column => (
                    <td {...column.getFooterProps()}>{column.render('Footer')}</td>
                  ))}
                </tr>
              ))}
        </tfoot>
      </table>
    </>
  );
};

export default CustomerSalesTable;

