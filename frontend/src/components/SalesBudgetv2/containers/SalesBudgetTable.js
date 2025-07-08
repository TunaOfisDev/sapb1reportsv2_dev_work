// frontend/src/components/SalesBudgetv2/containers/SalesBudgetTable.js
import React, { useMemo, useState } from 'react';
import { useTable, useSortBy, useFilters } from 'react-table';
import FormatNumber from '../utils/FormatNumber';
import ColumnFilter from '../utils/ColumnFilter';
import useUpperTotal from '../utils/UpperTotal';
import '../css/SalesBudgetTable.css';

const SalesBudgetTable = ({ salesBudgets, loading, error }) => {
  const [showQ1Details, setShowQ1Details] = useState(false);
  const [showQ2Details, setShowQ2Details] = useState(false);
  const [showQ3Details, setShowQ3Details] = useState(false);
  const [showQ4Details, setShowQ4Details] = useState(false);
  const upperTotals = useUpperTotal(salesBudgets);

  // Kümülatif oranı hesaplayın
  const cumulativeRate = upperTotals.toplam_gercek && upperTotals.toplam_hedef
    ? (upperTotals.toplam_gercek / upperTotals.toplam_hedef * 100).toFixed(2)
    : 0;  // Eğer toplam_hedef 0 ise, bölme hatası oluşmasını önleyin

  const defaultColumn = useMemo(() => ({
    Filter: ColumnFilter,
  }), []);

  const columns = useMemo(() => [
    {
      Header: 'Genel Toplam 2025',
      columns: [
        {
          Header: 'Satıcı',
          accessor: 'satici',
          Filter: ColumnFilter,
          headerClassName: 'sales-budget__thead--header',
        },
        {
          Header: () => <>Toplam Gerçek <FormatNumber value={upperTotals.toplam_gercek} /></>,
          accessor: 'toplam_gercek',
          Cell: ({ value }) => <FormatNumber value={value} />,
          disableFilters: true,
          headerClassName: 'sales-budget__thead--numeric-header',
          className: 'sales-budget__td--numeric',
        },
        {
          Header: () => <>Toplam Hedef <FormatNumber value={upperTotals.toplam_hedef} /></>,
          accessor: 'toplam_hedef',
          Cell: ({ value }) => <FormatNumber value={value} />,
          disableFilters: true,
          headerClassName: 'sales-budget__thead--numeric-header',
          className: 'sales-budget__td--numeric',
        },
        {
          Header: () => <>Oran <span>{cumulativeRate}%</span></>,
          accessor: 'yuzde_oran',
          Cell: ({ value }) => `${value.toFixed(2)}%`, // Hesaplanan yüzde oranını yuvarla
          disableFilters: true,
          headerClassName: 'sales-budget__thead--numeric-header',
          className: 'sales-budget__td--numeric',
        }
      ]
    },
    ...showQ1Details ? [
      {
        Header: '1. Çeyrek Gerçek & Hedef',
        columns: [
          {
            Header: () => <>Oca Gerçek <FormatNumber value={upperTotals.oca_gercek} /></>,
            accessor: 'oca_gercek',
            Cell: ({ value }) => <FormatNumber value={value} />,
            disableFilters: true,
            headerClassName: 'sales-budget__thead--numeric-header',
            className: 'sales-budget__td--numeric',
          },
          {
            Header: () => <>Oca Hedef <FormatNumber value={upperTotals.oca_hedef} /></>,
            accessor: 'oca_hedef',
            Cell: ({ value }) => <FormatNumber value={value} />,
            disableFilters: true,
            headerClassName: 'sales-budget__thead--numeric-header',
            className: 'sales-budget__td--numeric',
          },
          {
            Header: () => <>Sub Gerçek <FormatNumber value={upperTotals.sub_gercek} /></>,
            accessor: 'sub_gercek',
            Cell: ({ value }) => <FormatNumber value={value} />,
            disableFilters: true,
            headerClassName: 'sales-budget__thead--numeric-header',
            className: 'sales-budget__td--numeric',
          },
          {
            Header: () => <>Sub Hedef <FormatNumber value={upperTotals.sub_hedef} /></>,
            accessor: 'sub_hedef',
            Cell: ({ value }) => <FormatNumber value={value} />,
            disableFilters: true,
            headerClassName: 'sales-budget__thead--numeric-header',
            className: 'sales-budget__td--numeric',
          },
          {
            Header: () => <>Mar Gerçek <FormatNumber value={upperTotals.mar_gercek} /></>,
            accessor: 'mar_gercek',
            Cell: ({ value }) => <FormatNumber value={value} />,
            disableFilters: true,
            headerClassName: 'sales-budget__thead--numeric-header',
            className: 'sales-budget__td--numeric',
          },
          {
            Header: () => <>Mar Hedef <FormatNumber value={upperTotals.mar_hedef} /></>,
            accessor: 'mar_hedef',
            Cell: ({ value }) => <FormatNumber value={value} />,
            disableFilters: true,
            headerClassName: 'sales-budget__thead--numeric-header',
            className: 'sales-budget__td--numeric',
          }
        ]
      }
    ] : [],
    ...showQ2Details ? [
      {
        Header: '2. Çeyrek Gerçek & Hedef',
        columns: [
          {
            Header: () => <>Nis Gerçek <FormatNumber value={upperTotals.nis_gercek} /></>,
            accessor: 'nis_gercek',
            Cell: ({ value }) => <FormatNumber value={value} />,
            disableFilters: true,
            headerClassName: 'sales-budget__thead--numeric-header',
            className: 'sales-budget__td--numeric',
          },
          {
            Header: () => <>Nis Hedef <FormatNumber value={upperTotals.nis_hedef} /></>,
            accessor: 'nis_hedef',
            Cell: ({ value }) => <FormatNumber value={value} />,
            disableFilters: true,
            headerClassName: 'sales-budget__thead--numeric-header',
            className: 'sales-budget__td--numeric',
          },
          {
            Header: () => <>May Gerçek <FormatNumber value={upperTotals.may_gercek} /></>,
            accessor: 'may_gercek',
            Cell: ({ value }) => <FormatNumber value={value} />,
            disableFilters: true,
            headerClassName: 'sales-budget__thead--numeric-header',
            className: 'sales-budget__td--numeric',
          },
          {
            Header: () => <>May Hedef <FormatNumber value={upperTotals.may_hedef} /></>,
            accessor: 'may_hedef',
            Cell: ({ value }) => <FormatNumber value={value} />,
            disableFilters: true,
            headerClassName: 'sales-budget__thead--numeric-header',
            className: 'sales-budget__td--numeric',
          },
          {
            Header: () => <>Haz Gerçek <FormatNumber value={upperTotals.haz_gercek} /></>,
            accessor: 'haz_gercek',
            Cell: ({ value }) => <FormatNumber value={value} />,
            disableFilters: true,
            headerClassName: 'sales-budget__thead--numeric-header',
            className: 'sales-budget__td--numeric',
          },
          {
            Header: () => <>Haz Hedef <FormatNumber value={upperTotals.haz_hedef} /></>,
            accessor: 'haz_hedef',
            Cell: ({ value }) => <FormatNumber value={value} />,
            disableFilters: true,
            headerClassName: 'sales-budget__thead--numeric-header',
            className: 'sales-budget__td--numeric',
          }
        ]
      }
    ] : [],
    
    ...showQ3Details ? [
      {
        Header: '3. Çeyrek Gerçek & Hedef',
        columns: [
          {
            Header: () => <>Tem Gerçek <FormatNumber value={upperTotals.tem_gercek} /></>,
            accessor: 'tem_gercek',
            Cell: ({ value }) => <FormatNumber value={value} />,
            disableFilters: true,
            headerClassName: 'sales-budget__thead--numeric-header',
            className: 'sales-budget__td--numeric',
          },
          {
            Header: () => <>Tem Hedef <FormatNumber value={upperTotals.tem_hedef} /></>,
            accessor: 'tem_hedef',
            Cell: ({ value }) => <FormatNumber value={value} />,
            disableFilters: true,
            headerClassName: 'sales-budget__thead--numeric-header',
            className: 'sales-budget__td--numeric',
          },
          {
            Header: () => <>Agu Gerçek <FormatNumber value={upperTotals.agu_gercek} /></>,
            accessor: 'agu_gercek',
            Cell: ({ value }) => <FormatNumber value={value} />,
            disableFilters: true,
            headerClassName: 'sales-budget__thead--numeric-header',
            className: 'sales-budget__td--numeric',
          },
          {
            Header: () => <>Agu Hedef <FormatNumber value={upperTotals.agu_hedef} /></>,
            accessor: 'agu_hedef',
            Cell: ({ value }) => <FormatNumber value={value} />,
            disableFilters: true,
            headerClassName: 'sales-budget__thead--numeric-header',
            className: 'sales-budget__td--numeric',
          },
          {
            Header: () => <>Eyl Gerçek <FormatNumber value={upperTotals.eyl_gercek} /></>,
            accessor: 'eyl_gercek',
            Cell: ({ value }) => <FormatNumber value={value} />,
            disableFilters: true,
            headerClassName: 'sales-budget__thead--numeric-header',
            className: 'sales-budget__td--numeric',
          },
          {
            Header: () => <>Eyl Hedef <FormatNumber value={upperTotals.eyl_hedef} /></>,
            accessor: 'eyl_hedef',
            Cell: ({ value }) => <FormatNumber value={value} />,
            disableFilters: true,
            headerClassName: 'sales-budget__thead--numeric-header',
            className: 'sales-budget__td--numeric',
          }
        ]
      }
    ] : [],
    
    ...showQ4Details ? [
      {
        Header: '4. Çeyrek Gerçek & Hedef',
        columns: [
          {
            Header: () => <>Eki Gerçek <FormatNumber value={upperTotals.eki_gercek} /></>,
            accessor: 'eki_gercek',
            Cell: ({ value }) => <FormatNumber value={value} />,
            disableFilters: true,
            headerClassName: 'sales-budget__thead--numeric-header',
            className: 'sales-budget__td--numeric',
          },
          {
            Header: () => <>Eki Hedef <FormatNumber value={upperTotals.eki_hedef} /></>,
            accessor: 'eki_hedef',
            Cell: ({ value }) => <FormatNumber value={value} />,
            disableFilters: true,
            headerClassName: 'sales-budget__thead--numeric-header',
            className: 'sales-budget__td--numeric',
          },
          {
            Header: () => <>Kas Gerçek <FormatNumber value={upperTotals.kas_gercek} /></>,
            accessor: 'kas_gercek',
            Cell: ({ value }) => <FormatNumber value={value} />,
            disableFilters: true,
            headerClassName: 'sales-budget__thead--numeric-header',
            className: 'sales-budget__td--numeric',
          },
          {
            Header: () => <>Kas Hedef <FormatNumber value={upperTotals.kas_hedef} /></>,
            accessor: 'kas_hedef',
            Cell: ({ value }) => <FormatNumber value={value} />,
            disableFilters: true,
            headerClassName: 'sales-budget__thead--numeric-header',
            className: 'sales-budget__td--numeric',
          },
          {
            Header: () => <>Ara Gerçek <FormatNumber value={upperTotals.ara_gercek} /></>,
            accessor: 'ara_gercek',
            Cell: ({ value }) => <FormatNumber value={value} />,
            disableFilters: true,
            headerClassName: 'sales-budget__thead--numeric-header',
            className: 'sales-budget__td--numeric',
          },
          {
            Header: () => <>Ara Hedef <FormatNumber value={upperTotals.ara_hedef} /></>,
            accessor: 'ara_hedef',
            Cell: ({ value }) => <FormatNumber value={value} />,
            disableFilters: true,
            headerClassName: 'sales-budget__thead--numeric-header',
            className: 'sales-budget__td--numeric',
          }
        ]
      }
    ] : [],
    
  ], [cumulativeRate, showQ1Details, showQ2Details, showQ3Details, showQ4Details, upperTotals.agu_gercek, upperTotals.agu_hedef, upperTotals.ara_gercek, upperTotals.ara_hedef, upperTotals.eki_gercek, upperTotals.eki_hedef, upperTotals.eyl_gercek, upperTotals.eyl_hedef, upperTotals.haz_gercek, upperTotals.haz_hedef, upperTotals.kas_gercek, upperTotals.kas_hedef, upperTotals.mar_gercek, upperTotals.mar_hedef, upperTotals.may_gercek, upperTotals.may_hedef, upperTotals.nis_gercek, upperTotals.nis_hedef, upperTotals.oca_gercek, upperTotals.oca_hedef, upperTotals.sub_gercek, upperTotals.sub_hedef, upperTotals.tem_gercek, upperTotals.tem_hedef, upperTotals.toplam_gercek, upperTotals.toplam_hedef]);

  const data = useMemo(() => salesBudgets || [], [salesBudgets]);

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
      initialState: {
        sortBy: [
          {
            id: 'toplam_gercek',
            desc: true
          }
        ]
      }
    },
    useFilters,
    useSortBy,
  );

  if (loading) return <div>Yükleniyor...</div>;
  if (error) return <div>Hata: {error.message}</div>;

  return (
    <>
      <div className="sales-budget-container__button-wrapper">
        <button
          onClick={() => setShowQ1Details(!showQ1Details)}
          className={`sales-budget__button ${showQ1Details ? 'sales-budget__button--active' : ''}`}
        >
          {showQ1Details ? '1. Çeyrek Gizle' : '1. Çeyrek Göster'}
        </button>
        <button
          onClick={() => setShowQ2Details(!showQ2Details)}
          className={`sales-budget__button ${showQ2Details ? 'sales-budget__button--active' : ''}`}
        >
          {showQ2Details ? '2. Çeyrek Gizle' : '2. Çeyrek Göster'}
        </button>
        <button
          onClick={() => setShowQ3Details(!showQ3Details)}
          className={`sales-budget__button ${showQ3Details ? 'sales-budget__button--active' : ''}`}
        >
          {showQ3Details ? '3. Çeyrek Gizle' : '3. Çeyrek Göster'}
        </button>
        <button
          onClick={() => setShowQ4Details(!showQ4Details)}
          className={`sales-budget__button ${showQ4Details ? 'sales-budget__button--active' : ''}`}
        >
          {showQ4Details ? '4. Çeyrek Gizle' : '4. Çeyrek Göster'}
        </button>
      </div>

      <table {...getTableProps()} className="sales-budget__table">
        <thead>
          {headerGroups.map(headerGroup => (
            <tr {...headerGroup.getHeaderGroupProps()}>
              {headerGroup.headers.map(column => (
                <th {...column.getHeaderProps()} className={`sales-budget__thead--header ${column.headerClassName || ''}`}>
                  <div {...(column.canSort ? column.getSortByToggleProps() : {})}>
                    {column.render('Header')}
                    {column.isSorted ? (column.isSortedDesc ? ' ↓' : ' ↑') : ''}
                  </div>
                  {column.canFilter ? <div className="filter-container">{column.render('Filter')}</div> : null}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody {...getTableBodyProps()}>
          {rows.map(row => {
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
      </table>
    </>
  );
};

export default SalesBudgetTable;
