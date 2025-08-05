// path: frontend/src/components/formforgeapi/components/reusable/DataTable.jsx
import React, { useMemo } from "react";
import { useTable } from "react-table";

/**
 * Reusable aptal tablo.
 * @param {array|*}  columns   react-table column defs (her ihtimale karşı dizi kontrolü yapılır)
 * @param {array|*}  data      row data (her ihtimale karşı dizi kontrolü yapılır)
 * @param {string}   className (opsiyonel) tabloya eklenecek CSS sınıfı
 *
 * Not: react-table, columns parametresinde `forEach` çağırır; bu yüzden
 * mutlaka dizi olduğundan emin oluyoruz. Aksi hâlde “t.forEach is not a function”
 * hatası fırlatılır.
 */
const DataTable = ({ columns, data, className = "" }) => {
  /* Güvenli dönüştürmeler */
  const safeColumns = useMemo(
    () => (Array.isArray(columns) ? columns : []),
    [columns]
  );

  const safeData = useMemo(
    () => (Array.isArray(data) ? data : []),
    [data]
  );

  /* react-table */
  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    rows,
    prepareRow,
  } = useTable({ columns: safeColumns, data: safeData });

  return (
    <table {...getTableProps()} className={className}>
      <thead>
        {headerGroups.map((headerGroup) => (
          <tr {...headerGroup.getHeaderGroupProps()}>
            {headerGroup.headers.map((column) => (
              <th {...column.getHeaderProps()}>
                {column.render("Header")}
              </th>
            ))}
          </tr>
        ))}
      </thead>

      <tbody {...getTableBodyProps()}>
        {rows.map((row) => {
          prepareRow(row);
          return (
            <tr {...row.getRowProps()}>
              {row.cells.map((cell) => (
                <td {...cell.getCellProps()}>
                  {cell.render("Cell")}
                </td>
              ))}
            </tr>
          );
        })}
      </tbody>
    </table>
  );
};

export default DataTable;
