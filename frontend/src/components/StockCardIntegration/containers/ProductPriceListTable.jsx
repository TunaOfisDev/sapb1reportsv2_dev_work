// path: frontend/src/components/StockCardIntegration/containers/ProductPriceListTable.jsx
import React, { useMemo } from 'react';
import { useTable, usePagination, useFilters, useSortBy } from 'react-table';   // ⬅️ useSortBy eklendi
import Pagination   from '../utils/Pagination';
import ColumnFilter from '../utils/ColumnFilter';
import { multiTermTextFilter } from '../utils/multiTermTextFilter';
import styles            from '../css/ProductPriceListTable.module.css';
import paginationStyles  from '../css/Pagination.module.css';

const ProductPriceListTable = ({ data }) => {
  /* --- 1. Kolon tanımları --- */
  const columns = useMemo(() => [
    {
      Header: 'Ürün Kodu',
      accessor: 'item_code',
      Filter: ColumnFilter,
      filter: 'multiTerms',
    },
    {
      Header: 'Ürün Adı',
      accessor: 'item_name',
      Filter: ColumnFilter,
      filter: 'multiTerms',
    },
    {
      Header: 'Fiyat',
      accessor: 'price',
      disableFilters: true,
      Cell: ({ value }) => {
        const num = parseFloat(value);
        return isNaN(num) ? '-' : num.toFixed(2);
      },
    },
    { Header: 'Döviz', accessor: 'currency', disableFilters: true },
    {
      Header: 'Eski Kod',
      accessor: 'old_component_code',
      Filter: ColumnFilter,
      filter: 'multiTerms',
      Cell: ({ value }) => value || '-',
    },
    {
      Header: 'Güncelleme',
      accessor: 'updated_at',
      disableFilters: true,
      Cell: ({ value }) => {
        const d = new Date(value);
        const pad = (n) => n.toString().padStart(2, '0');
        return (
          `${pad(d.getDate())}.${pad(d.getMonth() + 1)}.${pad(d.getFullYear() % 100)} ` +
          `${pad(d.getHours())}:${pad(d.getMinutes())}`
        );
      },
    },
  ], []);

  /* --- 2. React-Table instance --- */
  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    page,
    prepareRow,
    // pagination helpers
    state: { pageIndex, pageSize },
    setPageSize,
    canNextPage, canPreviousPage, pageCount,
    gotoPage, nextPage, previousPage,
  } = useTable(
    {
      columns,
      data,
      /** Varsayılan sıralama ► item_code ASC */
      initialState: {
        pageIndex: 0,
        pageSize: 100,
        sortBy: [{ id: 'item_code', desc: false }],
      },
      filterTypes: { multiTerms: multiTermTextFilter },
      defaultColumn: { Filter: () => null },
    },
    useFilters,
    useSortBy,        // ⬅️ sıralama hook’u
    usePagination,
  );

  if (!data?.length) return <p>🔎 Gösterilecek veri bulunamadı.</p>;

  /* --- 3. Render --- */
  return (
    <>
      {/* Pagination üstte */}
      <div className={paginationStyles['pagination-fixed-top']}>
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

      <table {...getTableProps()} className={styles['product-price-list__table']}>
        <thead>
          {headerGroups.map((hg) => (
            <React.Fragment key={hg.getHeaderGroupProps().key}>
              {/* Başlık + sıralama toggle */}
              <tr {...hg.getHeaderGroupProps()}>
                {hg.headers.map((col) => (
                  <th
                    key={col.id}
                    {...col.getHeaderProps(col.getSortByToggleProps())}  /* ⬅️ toggle props */
                    className={col.isSorted
                      ? col.isSortedDesc
                        ? styles['sort-desc']
                        : styles['sort-asc']
                      : ''}
                  >
                    {col.render('Header')}
                    {col.isSorted ? (col.isSortedDesc ? ' 🔽' : ' 🔼') : ''}
                  </th>
                ))}
              </tr>

              {/* Filtre satırı */}
              <tr>
                {hg.headers.map((col) => (
                  <th key={`${col.id}-filter`}>
                    {col.canFilter ? col.render('Filter') : null}
                  </th>
                ))}
              </tr>
            </React.Fragment>
          ))}
        </thead>

        <tbody {...getTableBodyProps()}>
          {page.map((row) => {
            prepareRow(row);
            return (
              <tr key={row.id} {...row.getRowProps()}>
                {row.cells.map((cell) => (
                  <td key={cell.column.id} {...cell.getCellProps()}>
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

export default ProductPriceListTable;
