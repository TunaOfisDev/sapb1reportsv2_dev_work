// frontend/src/components/LogoCustomerCollection/containers/LogoCustomerCollectionTable.js
import { useMemo } from 'react';
import {
  useTable, useSortBy, useFilters, usePagination,
} from 'react-table';
import FormatNumber from '../utils/FormatNumber';
import ColumnFilter from '../utils/ColumnFilter';
import Pagination from '../utils/Pagination';
import { numberSort, absSort } from '../utils/SortNumber';
import useUpperTotal from '../utils/UpperTotal';
import useDynamicSubtotals from '../utils/DynamicSubTotal';
import '../css/LogoCustomerCollectionTable.css';

/** Yardımcı: satırdaki aylik_kalan_borc alanını nesneye çevirir */
const toObject = (monthly) => (
  Array.isArray(monthly)
    ? Object.fromEntries(monthly)
    : (monthly || {})
);

const LogoCustomerCollectionTable = ({ data = [] }) => {
  const uptotals = useUpperTotal(data);

  /** Tüm ay etiketlerini tek seferde çıkar */
  const allMonthKeys = useMemo(() => {
    const set = new Set();
    data.forEach((r) => { Object.keys(toObject(r.aylik_kalan_borc)).forEach((k) => set.add(k)); });
    return Array.from(set);
  }, [data]);

  /** Kolon tanımları */
  const columns = useMemo(() => {
    if (!data.length) return [];

    const base = [
      { Header: 'Cari Kod', accessor: 'cari_kod', Filter: ColumnFilter },
      {
        Header: 'Cari Ad',
        accessor: 'cari_ad',
        Filter: ColumnFilter,
        Cell: ({ value }) => (
          <div className="logo-customer-collection-table__cell-wrapper">
            <span className="logo-customer-collection-table__truncated-text">
              {value?.length > 30 ? `${value.slice(0, 30)}…` : value}
            </span>
            {value?.length > 30 && (
              <span className="logo-customer-collection-table__tooltip">{value}</span>
            )}
          </div>
        ),
      },
      {
        Header: () => (
          <div className="logo-customer-collection-table__header-content">
            <span>Güncel Bakiye</span>
            <span className="logo-customer-collection-table__header-total">
              <FormatNumber value={uptotals.guncel_bakiye} />
            </span>
          </div>
        ),
        accessor: (row) => parseFloat(row.guncel_bakiye) || 0,
        id: 'guncel_bakiye',
        Cell: ({ value }) => <div style={{ textAlign: 'right' }}><FormatNumber value={value} /></div>,
        disableFilters: true,
        sortType: absSort,
      },
    ];

    /** Dinamik ay kolonları */
    const months = allMonthKeys.map((key) => ({
      Header: () => (
        <div className="logo-customer-collection-table__header-content">
          <span>{key}</span>
          <span className="logo-customer-collection-table__header-total">
            <FormatNumber value={uptotals.aylik_kalan_borc[key] || 0} />
          </span>
        </div>
      ),
      accessor: (row) => toObject(row.aylik_kalan_borc)[key] || 0,
      id: key,
      Cell: ({ value }) => <div style={{ textAlign: 'right' }}><FormatNumber value={value} /></div>,
      disableFilters: true,
      sortType: numberSort,
    }));

    return [...base, ...months];
  }, [data, uptotals, allMonthKeys]);

  /* ----------- react-table setup ------------ */
  const defaultColumn = useMemo(() => ({ Filter: ColumnFilter }), []);
  const {
    getTableProps, getTableBodyProps, headerGroups, prepareRow, page,
    gotoPage, pageCount, canPreviousPage, canNextPage, nextPage, previousPage,
    setPageSize, state: { pageIndex, pageSize },
  } = useTable(
    {
      columns,
      data,
      defaultColumn,
      initialState: { pageIndex: 0, pageSize: 20, sortBy: [{ id: 'guncel_bakiye', desc: true }] },
    },
    useFilters,
    useSortBy,
    usePagination,
  );

  /* Dinamik alt toplamlar */
  const valueAccessors = useMemo(() => ['guncel_bakiye', ...allMonthKeys], [allMonthKeys]);
  const { formatted: formattedSubtotals } = useDynamicSubtotals(page, valueAccessors);

  if (!data.length) return <div>Tablo için veri bulunamadı.</div>;

  /* ----------- render ------------ */
  return (
    <div>
      <Pagination
        {...{
          canPreviousPage, canNextPage, nextPage, previousPage,
          pageIndex, pageSize, pageCount, gotoPage, setPageSize,
        }}
      />
      <div className="logo-customer-collection__table-wrapper">
        <table {...getTableProps()} className="logo-customer-collection-table">
          <thead className="logo-customer-collection-table__header">
            {headerGroups.map((hg) => (
              <tr {...hg.getHeaderGroupProps()}>
                {hg.headers.map((col) => (
                  <th {...col.getHeaderProps(col.getSortByToggleProps())} className="logo-customer-collection-table__header-cell">
                    <div className="logo-customer-collection-table__header-container">
                      {col.render('Header')}
                      <span className={`logo-customer-collection-table__sort-arrow ${col.isSorted ? 'logo-customer-collection-table__sort-arrow--active' : ''}`}>
                        {col.isSorted ? (col.isSortedDesc ? ' ↓' : ' ↑') : ''}
                      </span>
                    </div>
                    {col.canFilter && (
                      <div className="logo-customer-collection-table__filter-container">
                        {col.render('Filter')}
                      </div>
                    )}
                  </th>
                ))}
              </tr>
            ))}
          </thead>

          <tbody {...getTableBodyProps()}>
            {page.map((row) => {
              prepareRow(row);
              return (
                <tr {...row.getRowProps()} className="logo-customer-collection-table__body-row">
                  {row.cells.map((cell) => (
                    <td {...cell.getCellProps()} className="logo-customer-collection-table__body-cell">
                      {cell.render('Cell')}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>

          <tfoot>
            <tr>
              <td colSpan={2} className="logo-customer-collection-table__footer">Dinamik Alt Toplam:</td>
              {valueAccessors.map((k) => (
                <td key={k} className="logo-customer-collection-table__footer logo-customer-collection-table__numeric">
                  {formattedSubtotals[k]}
                </td>
              ))}
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );
};

export default LogoCustomerCollectionTable;
