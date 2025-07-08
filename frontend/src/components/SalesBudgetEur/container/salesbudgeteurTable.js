// frontend/src/components/SalesBudgetEur/container/salesbudgeteurTable.js

import React, { useMemo, useState } from "react";
import { useTable, useSortBy, useFilters } from "react-table";
import FormatNumber from "../utils/FormatNumber";
import ColumnFilter from "../utils/ColumnFilter";
import useUpperTotal from "../utils/UpperTotal";
import "../css/salesbudgeteurTable.css";

const SalesBudgetEURTable = ({ salesBudgets = [], loading, error }) => {
  const [showQ1, setShowQ1] = useState(false);
  const [showQ2, setShowQ2] = useState(false);
  const [showQ3, setShowQ3] = useState(false);
  const [showQ4, setShowQ4] = useState(false);
  const [showExtraCols, setShowExtraCols] = useState(false);

  const totals = useUpperTotal(salesBudgets);
  const cumulativeRate = totals.toplam_gercek && totals.toplam_hedef
    ? ((totals.toplam_gercek / totals.toplam_hedef) * 100).toFixed(2)
    : "0";

  const defaultColumn = useMemo(() => ({ Filter: ColumnFilter }), []);

  const columns = useMemo(() => {
    const baseCols = [
      {
        Header: "Genel Toplam 2025",
        columns: [
          {
            Header: "Satıcı",
            accessor: "satici",
            Filter: ColumnFilter,
          },
          {
            Header: () => <>Toplam Gerçek <FormatNumber value={totals.toplam_gercek} /></>,
            accessor: "toplam_gercek",
            Cell: ({ value }) => <FormatNumber value={value} />,
            disableFilters: true,
          },
          {
            Header: () => <>Toplam Hedef <FormatNumber value={totals.toplam_hedef} /></>,
            accessor: "toplam_hedef",
            Cell: ({ value }) => <FormatNumber value={value} />,
            disableFilters: true,
          },
          {
            Header: () => <>Oran {cumulativeRate}%</>,
            accessor: "yuzde_oran",
            Cell: ({ value }) => `${parseFloat(value || 0).toFixed(2)}%`,
            disableFilters: true,
          },
        ],
      },
    ];

    if (showExtraCols) {
      baseCols[0].columns.push(
        {
          Header: () => <>Toplam İptal (EUR)</>,
          accessor: "toplam_iptal_eur",
          Cell: ({ value }) => <FormatNumber value={value} />,
          disableFilters: true,
        },
        {
          Header: () => <>Elle Kapanan (EUR)</>,
          accessor: "toplam_elle_kapanan_eur",
          Cell: ({ value }) => <FormatNumber value={value} />,
          disableFilters: true,
        },
        {
          Header: "İptal/Elle Kapanan Siparişler",
          accessor: "kapali_sip_list",
          Cell: ({ value }) => (
            <div className="sales-budgeteur__td--json" title={value}>
              {value || "-"}
            </div>
          ),
          disableFilters: true,
        }
      );
    }

    const quarterCols = (label, m1, m2, m3) => ({
      Header: label,
      columns: [m1, m2, m3].flatMap(({ label, key }) => [
        {
          Header: () => <>{label} <FormatNumber value={totals[key]} /></>,
          accessor: key,
          Cell: ({ value }) => <FormatNumber value={value} />,
          disableFilters: true,
        },
        {
          Header: () => <>{label.replace("Gerçek", "Hedef")} <FormatNumber value={totals[key.replace("gercek", "hedef")]} /></>,
          accessor: key.replace("gercek", "hedef"),
          Cell: ({ value }) => <FormatNumber value={value} />,
          disableFilters: true,
        }
      ])
    });

    if (showQ1) baseCols.push(quarterCols("1. Çeyrek", { label: "Oca Gerçek", key: "oca_gercek" }, { label: "Sub Gerçek", key: "sub_gercek" }, { label: "Mar Gerçek", key: "mar_gercek" }));
    if (showQ2) baseCols.push(quarterCols("2. Çeyrek", { label: "Nis Gerçek", key: "nis_gercek" }, { label: "May Gerçek", key: "may_gercek" }, { label: "Haz Gerçek", key: "haz_gercek" }));
    if (showQ3) baseCols.push(quarterCols("3. Çeyrek", { label: "Tem Gerçek", key: "tem_gercek" }, { label: "Agu Gerçek", key: "agu_gercek" }, { label: "Eyl Gerçek", key: "eyl_gercek" }));
    if (showQ4) baseCols.push(quarterCols("4. Çeyrek", { label: "Eki Gerçek", key: "eki_gercek" }, { label: "Kas Gerçek", key: "kas_gercek" }, { label: "Ara Gerçek", key: "ara_gercek" }));

    return baseCols;
  }, [totals, cumulativeRate, showQ1, showQ2, showQ3, showQ4, showExtraCols]);

  const data = useMemo(() => salesBudgets, [salesBudgets]);

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    prepareRow,
    rows,
  } = useTable(
    {
      columns,
      data,
      defaultColumn,
      initialState: { sortBy: [{ id: "toplam_gercek", desc: true }] },
    },
    useFilters,
    useSortBy,
  );

  if (loading) return <div>Yükleniyor...</div>;
  if (error) return <div>Hata: {error.message}</div>;

  return (
    <div className="sales-budgeteur__table-wrapper">
      <div className="sales-budgeteur__toggle-actions">
        <button
          onClick={() => setShowQ1(!showQ1)}
          className={`sales-budgeteur__button ${showQ1 ? "sales-budgeteur__button--active" : ""}`}
        >
          {showQ1 ? "1. Çeyrek Gizle" : "1. Çeyrek Göster"}
        </button>
        <button
          onClick={() => setShowQ2(!showQ2)}
          className={`sales-budgeteur__button ${showQ2 ? "sales-budgeteur__button--active" : ""}`}
        >
          {showQ2 ? "2. Çeyrek Gizle" : "2. Çeyrek Göster"}
        </button>
        <button
          onClick={() => setShowQ3(!showQ3)}
          className={`sales-budgeteur__button ${showQ3 ? "sales-budgeteur__button--active" : ""}`}
        >
          {showQ3 ? "3. Çeyrek Gizle" : "3. Çeyrek Göster"}
        </button>
        <button
          onClick={() => setShowQ4(!showQ4)}
          className={`sales-budgeteur__button ${showQ4 ? "sales-budgeteur__button--active" : ""}`}
        >
          {showQ4 ? "4. Çeyrek Gizle" : "4. Çeyrek Göster"}
        </button>
        <button
          onClick={() => setShowExtraCols(!showExtraCols)}
          className={`sales-budgeteur__button sales-budgeteur__button--secondary ${showExtraCols ? "sales-budgeteur__button--active" : ""}`}
        >
          {showExtraCols ? "İptalleri Gizle" : "İptalleri Göster"}
        </button>
      </div>

      <table {...getTableProps()} className="sales-budgeteur__table">
        <thead className="sales-budgeteur__thead--header">
          {headerGroups.map(headerGroup => (
            <tr {...headerGroup.getHeaderGroupProps()} key={headerGroup.id}>
              {headerGroup.headers.map(column => (
                <th {...column.getHeaderProps(column.getSortByToggleProps())} key={column.id} className="sales-budgeteur__thead--numeric-header">
                  {column.render("Header")}
                  {column.isSorted ? (column.isSortedDesc ? " ↓" : " ↑") : ""}
                  {column.canFilter && (
                    <div className="filter-container">
                      {column.render("Filter")}
                    </div>
                  )}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody {...getTableBodyProps()}>
          {rows.map(row => {
            prepareRow(row);
            return (
              <tr {...row.getRowProps()} key={row.id} className="sales-budgeteur__row">
                {row.cells.map(cell => (
                  <td
                    {...cell.getCellProps()}
                    key={cell.column.id}
                    className={`sales-budgeteur__td--numeric`}
                  >
                    {cell.render("Cell")}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default SalesBudgetEURTable;
