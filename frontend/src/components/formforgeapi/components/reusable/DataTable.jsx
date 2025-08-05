// path: frontend/src/components/formforgeapi/components/reusable/DataTable.jsx
// NOT: Bu dosya react-table v7 SÖZDİZİMİ ile yeniden yazılmıştır.

import React from "react";
import { useTable, useSortBy, usePagination } from "react-table";
import styles from "../../css/DataTable.module.css";

/**
 * DataTable Component (react-table v7 versiyonu)
 * ----------------------------------------------------------------
 * Yeniden kullanılabilir, "aptal" bir tablo bileşeni.
 * - react-table v7 hook'larını ve sözdizimini kullanır.
 * - Sıralama (useSortBy) ve sayfalama (usePagination) eklentilerini içerir.
 *
 * @param {Array} columns - react-table v7 formatında sütun tanımları.
 * @param {Array} data - Tabloda gösterilecek veri dizisi.
 */
const DataTable = ({ columns, data }) => {
  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    prepareRow,
    page, // `rows` yerine `page` kullanılır, çünkü sadece mevcut sayfadaki satırları içerir.
    canPreviousPage,
    canNextPage,
    pageOptions,
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
      initialState: { pageIndex: 0, pageSize: 10 },
    },
    useSortBy,
    usePagination
  );

  return (
    <div className={styles.dataTable}>
      <table {...getTableProps()} className={styles.dataTable__table}>
        <thead>
          {headerGroups.map(headerGroup => (
            <tr {...headerGroup.getHeaderGroupProps()}>
              {headerGroup.headers.map(column => (
                <th {...column.getHeaderProps(column.getSortByToggleProps())} className={styles.dataTable__th}>
                  {column.render("Header")}
                  <span className={styles["dataTable__th--sorted"]}>
                    {column.isSorted
                      ? column.isSortedDesc
                        ? " ▼"
                        : " ▲"
                      : ""}
                  </span>
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody {...getTableBodyProps()}>
          {page.length > 0 ? (
            page.map(row => {
              prepareRow(row); // v7'de her satır render edilmeden önce bu fonksiyon çağrılmalıdır!
              return (
                <tr {...row.getRowProps()} className={styles.dataTable__tr}>
                  {row.cells.map(cell => {
                    return (
                      <td {...cell.getCellProps()} className={styles.dataTable__td}>
                        {cell.render("Cell")}
                      </td>
                    );
                  })}
                </tr>
              );
            })
          ) : (
            <tr>
              <td colSpan={columns.length} className={styles.dataTable__empty}>
                Görüntülenecek veri bulunamadı.
              </td>
            </tr>
          )}
        </tbody>
      </table>

      {pageCount > 1 && (
         <div className={styles.dataTable__pagination}>
          <button onClick={() => gotoPage(0)} disabled={!canPreviousPage}>
            {"<<"}
          </button>
          <button onClick={() => previousPage()} disabled={!canPreviousPage}>
            {"<"}
          </button>
          <span>
            Sayfa{" "}
            <strong>
              {pageIndex + 1} / {pageOptions.length}
            </strong>
          </span>
          <button onClick={() => nextPage()} disabled={!canNextPage}>
            {">"}
          </button>
          <button onClick={() => gotoPage(pageCount - 1)} disabled={!canNextPage}>
            {">>"}
          </button>
        </div>
      )}
    </div>
  );
};

export default DataTable;