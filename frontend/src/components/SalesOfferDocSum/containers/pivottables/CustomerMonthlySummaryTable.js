// frontend/src/components/SalesOfferDocSum/containers/pivottables/CustomerMonthlySummaryTable.js
import React, { useMemo } from 'react';
import { useTable, useSortBy, useFilters, usePagination } from 'react-table';
import Pagination from '../../utils/Pagination';
import FormatNumber from '../../utils/FormatNumber';
import ColumnFilter from '../../utils/ColumnFilter';
import calculateSubTotals from '../../utils/PivotCMSTSubTotal';
import '../../css/CustomerMonthlySummaryTable.css'; 

const CustomerMonthlySummaryTable = ({ data }) => {
  const calculatedSubtotals = useMemo(() => calculateSubTotals(data, ['total_net_tutar_ypb', 'total_net_tutar_spb', 'total_brut_tutar_spb']), [data]);

  const columns = useMemo(() => [
    {
      Header: 'Müşteri Kodu',
      accessor: 'musteri_kod',
      Filter: ColumnFilter,
    },
    {
      Header: 'Müşteri Adı',
      accessor: 'musteri_ad',
      Filter: ColumnFilter,
      Cell: ({ value }) => <div>{value}</div>,
    },
    {
      Header: () => (
        <div className="customer-monthly-summary-table__header-cell--numeric">
          Net YPB
          <div>
            <small><FormatNumber value={calculatedSubtotals.total_net_tutar_ypb} /></small>
          </div>
        </div>
      ),
      accessor: 'total_net_tutar_ypb',
      Cell: ({ value }) => (
        <div className="customer-monthly-summary-table__cell--numeric">
          <FormatNumber value={value} />
        </div>
      ),
      disableFilters: true,
    },
    {
      Header: () => (
        <div className="customer-monthly-summary-table__header-cell--numeric">
          Net SPB
          <div>
            <small><FormatNumber value={calculatedSubtotals.total_net_tutar_spb} /></small>
          </div>
        </div>
      ),
      accessor: 'total_net_tutar_spb',
      Cell: ({ value }) => (
        <div className="customer-monthly-summary-table__cell--numeric">
          <FormatNumber value={value} />
        </div>
      ),
      disableFilters: true,
    },
    {
      Header: () => (
        <div className="customer-monthly-summary-table__header-cell--numeric">
          Brüt SPB
          <div>
            <small><FormatNumber value={calculatedSubtotals.total_brut_tutar_spb} /></small>
          </div>
        </div>
      ),
      accessor: 'total_brut_tutar_spb',
      Cell: ({ value }) => (
        <div className="customer-monthly-summary-table__cell--numeric">
          <FormatNumber value={value} />
        </div>
      ),
      disableFilters: true,
    },
  ], [calculatedSubtotals]);

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    prepareRow,
    page,
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
      initialState: { pageIndex: 0, pageSize: 100 },
    },
    useFilters,
    useSortBy,
    usePagination,
  );

  return (
    <div className="customer-monthly-summary-table__container">
      <h2>Müşteri Bazlı Yillik Özet</h2>
      <table {...getTableProps()} className="customer-monthly-summary-table">
        <thead>
          {headerGroups.map(headerGroup => (
            <tr {...headerGroup.getHeaderGroupProps()} className="customer-monthly-summary-table__header">
              {headerGroup.headers.map(column => (
                <th {...column.getHeaderProps(column.getSortByToggleProps())} className="customer-monthly-summary-table__header-cell">
                  {column.render('Header')}
                  {column.isSorted ? (column.isSortedDesc ? ' ↓' : ' ↑') : ''}
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
              <tr {...row.getRowProps()} className="customer-monthly-summary-table__row">
                {row.cells.map(cell => (
                  <td {...cell.getCellProps()} className="customer-monthly-summary-table__cell">
                    {cell.render('Cell')}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
        <tfoot>
          <tr>
            <td colSpan={2}>Sayfa Alt Toplamı</td>
            <td className="customer-monthly-summary-table__cell--numeric"><FormatNumber value={calculatedSubtotals.total_net_tutar_ypb} /></td>
            <td className="customer-monthly-summary-table__cell--numeric"><FormatNumber value={calculatedSubtotals.total_net_tutar_spb} /></td>
            <td className="customer-monthly-summary-table__cell--numeric"><FormatNumber value={calculatedSubtotals.total_brut_tutar_spb} /></td>
          </tr>
        </tfoot>
      </table>
      <div className="customer-monthly-summary-table__pagination">
        <Pagination
          gotoPage={gotoPage}
          canPreviousPage={canPreviousPage}
          canNextPage={canNextPage}
          pageCount={pageCount}
          nextPage={nextPage}
          previousPage={previousPage}
          setPageSize={setPageSize}
          pageIndex={pageIndex}
          pageOptions={pageOptions}
          pageSize={pageSize}
        />
      </div>
    </div>
  );
};

export default CustomerMonthlySummaryTable;
