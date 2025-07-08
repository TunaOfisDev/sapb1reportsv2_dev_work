// frontend/src/components/logo_supplier_receivables_aging/LogoSupplierReceivablesAgingTable.js
import { useMemo } from 'react';
import { useTable, useSortBy, useFilters, usePagination } from 'react-table';
import FormatNumber from '../utils/FormatNumber';
import ColumnFilter from '../utils/ColumnFilter';
import Pagination from '../utils/Pagination';
import { numberSort, absSort } from '../utils/SortNumber';
import useUpperTotal from '../utils/UpperTotal';
import useDynamicSubtotals from '../utils/DynamicSubTotal';
import '../css/LogoSupplierReceivablesAgingTable.css';

const LogoSupplierReceivablesAgingTable = ({ data }) => {
  const uptotals = useUpperTotal(data);

  const columns = useMemo(() => {
    if (!data || data.length === 0) {
      return [
        { Header: 'Cari Kod', accessor: 'cari_kod', Filter: ColumnFilter },
        {
          Header: 'Cari Ad',
          accessor: 'cari_ad',
          Filter: ColumnFilter,
          Cell: ({ value }) => (
            <div className="logo-supplier-aging-table__cell-wrapper">
              <span className="logo-supplier-aging-table__truncated-text">
                {value?.length > 30 ? `${value.substring(0, 30)}...` : value}
              </span>
              {value?.length > 30 && (
                <span className="logo-supplier-aging-table__tooltip">
                  {value}
                </span>
              )}
            </div>
          ),
        },
        {
          Header: () => (
            <div className="logo-supplier-aging-table__header-content">
              <span>Güncel Bakiye</span>
              <span className="logo-supplier-aging-table__header-total">
                <FormatNumber value={uptotals.guncel_bakiye || 0} />
              </span>
            </div>
          ),
          accessor: 'guncel_bakiye',
          Cell: ({ value }) => <div style={{ textAlign: 'right' }}><FormatNumber value={value} /></div>,
          disableFilters: true,
          sortType: absSort,
        },
      ];
    }

    const dynamicMonths = data[0]?.aylik_kalan_alacak || {};

    const baseColumns = [
      { Header: 'Cari Kod', accessor: 'cari_kod', Filter: ColumnFilter },
      {
        Header: 'Cari Ad',
        accessor: 'cari_ad',
        Filter: ColumnFilter,
        Cell: ({ value }) => (
          <div className="logo-supplier-aging-table__cell-wrapper">
            <span className="logo-supplier-aging-table__truncated-text">
              {value?.length > 30 ? `${value.substring(0, 30)}...` : value}
            </span>
            {value?.length > 30 && (
              <span className="logo-supplier-aging-table__tooltip">
                {value}
              </span>
            )}
          </div>
        ),
      },
      {
        Header: () => (
          <div className="logo-supplier-aging-table__header-content">
            <span>Güncel Bakiye</span>
            <span className="logo-supplier-aging-table__header-total">
              <FormatNumber value={uptotals.guncel_bakiye || 0} />
            </span>
          </div>
        ),
        accessor: 'guncel_bakiye',
        Cell: ({ value }) => <div style={{ textAlign: 'right' }}><FormatNumber value={value} /></div>,
        disableFilters: true,
        sortType: absSort,
      },
    ];

    const dynamicMonthColumns = Object.keys(dynamicMonths).map((key) => ({
      Header: () => (
        <div className="logo-supplier-aging-table__header-content">
          <span>{key}</span>
          <span className="logo-supplier-aging-table__header-total">
            <FormatNumber value={uptotals.aylik_kalan_alacak?.[key] || 0} />
          </span>
        </div>
      ),
      accessor: (row) => row.aylik_kalan_alacak?.[key] || 0,
      id: key,
      Cell: ({ value }) => <div style={{ textAlign: 'right' }}><FormatNumber value={value} /></div>,
      disableFilters: true,
      sortType: numberSort,
    }));

    return [...baseColumns, ...dynamicMonthColumns];
  }, [data, uptotals]);

  const valueAccessors = useMemo(() => {
    if (!data || data.length === 0) return [];
    const months = Object.keys(data[0]?.aylik_kalan_alacak || {});
    return ['guncel_bakiye', ...months];
  }, [data]);

  

  const defaultColumn = useMemo(() => ({
    Filter: ColumnFilter,
  }), []);

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    prepareRow,
    page,
    footerGroups,
    gotoPage,
    pageCount,
    canPreviousPage,
    canNextPage,
    nextPage,
    previousPage,
    setPageSize,
    state: { pageIndex, pageSize },
  } = useTable(
    {
      columns,
      data: data || [],
      defaultColumn,
      initialState: {
        pageIndex: 0,
        pageSize: 20,
        sortBy: [
          {
            id: 'guncel_bakiye',
            desc: true,
          },
        ],
      },
    },
    useFilters,
    useSortBy,
    usePagination
  );

  const { formatted: formattedSubtotals } = useDynamicSubtotals(page, valueAccessors);

  if (!data || data.length === 0) {
    return <div>Tablo için veri yok.</div>;
  }

  return (
    <div>
      <Pagination
        canPreviousPage={canPreviousPage}
        canNextPage={canNextPage}
        nextPage={nextPage}
        previousPage={previousPage}
        pageIndex={pageIndex}
        pageSize={pageSize}
        pageCount={pageCount}
        gotoPage={gotoPage}
        setPageSize={setPageSize}
      />
      <div className="logo-supplier-aging__table-wrapper">
        <table {...getTableProps()} className="logo-supplier-aging-table">
          <thead className="logo-supplier-aging-table__header">
            {headerGroups.map((headerGroup) => (
              <>
                <tr {...headerGroup.getHeaderGroupProps()}>
                  {headerGroup.headers.map((column) => (
                    <th
                      {...column.getHeaderProps(column.getSortByToggleProps())}
                      className="logo-supplier-aging-table__header-cell"
                    >
                      <div className="logo-supplier-aging-table__header-container">
                        {column.render('Header')}
                        <span
                          className={`logo-supplier-aging-table__sort-arrow ${
                            column.isSorted ? 'logo-supplier-aging-table__sort-arrow--active' : ''
                          }`}
                        >
                          {column.isSorted ? (column.isSortedDesc ? ' ↓' : ' ↑') : ''}
                        </span>
                      </div>
                      {column.canFilter && (
                        <div className="logo-supplier-aging-table__filter-container">
                          {column.render('Filter')}
                        </div>
                      )}
                    </th>
                  ))}
                </tr>
              </>
            ))}
          </thead>
          <tbody {...getTableBodyProps()}>
            {page.map((row) => {
              prepareRow(row);
              return (
                <tr {...row.getRowProps()} className="logo-supplier-aging-table__body-row">
                  {row.cells.map((cell) => (
                    <td {...cell.getCellProps()} className="logo-supplier-aging-table__body-cell">
                      {cell.render('Cell')}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
          <tfoot>
            <tr>
              <td colSpan={2} className="logo-supplier-aging-table__footer">
                Dinamik Alt Toplam:
              </td>
              {valueAccessors.map((key, idx) => (
                <td
                  key={idx}
                  className="logo-supplier-aging-table__footer logo-supplier-aging-table__numeric"
                >
                  {formattedSubtotals[key]}
                </td>
              ))}
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );
};

export default LogoSupplierReceivablesAgingTable;