// frontend/src/components/SalesOrderDocSum/containers/SalesOrderDocSumTable.js
import React, { useMemo, useState, useCallback } from 'react';
import { useTable, useFilters, useSortBy, usePagination } from 'react-table';
import formatDate from '../utils/DateFormat';
import DateRangeColumnFilter from '../utils/DateRangeColumnFilter';
import ColumnFilter, { turkishToUpperCase } from '../utils/ColumnFilter';
import FormatNumber from '../utils/FormatNumber';
import useUpperTotal from '../utils/UpperTotal';
import useDynamicSubtotals from '../utils/DynamicSubTotal';
import ShowModalOrderDocDetail from '../utils/ShowModalOrderDocDetail';
import Pagination from '../utils/Pagination';
import '../css/SalesOrderDocSumTable.css';
import '../css/DateRangeColumnFilter.css';

const SalesOrderDocSumTable = React.forwardRef(({ documentSummaries }, ref) => {
  const [modalBelgeNo, setModalBelgeNo] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  const openModal = useCallback((belgeNo) => {
    setModalBelgeNo(belgeNo);
    setIsModalOpen(true);
  }, []);

  const closeModal = useCallback(() => {
    setIsModalOpen(false);
    setModalBelgeNo(null);
  }, []);

  const uppertotals = useUpperTotal(documentSummaries || []);

  const sortDateValues = useCallback((rowA, rowB, columnId) => {
    const a = rowA.values[columnId] ? new Date(rowA.values[columnId]) : null;
    const b = rowB.values[columnId] ? new Date(rowB.values[columnId]) : null;
    
    if (a === null) return 1;
    if (b === null) return -1;
    if (a === b) return 0;
    
    return a > b ? 1 : -1;
  }, []);


  // Export için gerekli metodları tanımla
  React.useImperativeHandle(ref, () => ({
    getFilteredRows: () => rows,
    getTotals: () => subtotals
  }));

  const columns = useMemo(() => [
    {
      Header: 'BelgeNo',
      accessor: 'belge_no',
      Filter: ColumnFilter,
      Cell: ({ value }) => (
        <span
          className="sales-order-doc-sum-table__td--belge-no sales-order-doc-sum-table__th--belge-no"
          onClick={() => openModal(value)}
          style={{ cursor: 'pointer', color: 'blue' }}
        >
          {value}
        </span>
      ),
      filterClassName: 'sales-order-doc-sum-table__filter sales-order-doc-sum-table__filter input',
    },
    { Header: 'Statu', accessor: 'belge_durum', Filter: ColumnFilter },
    {
      Header: 'Satıcı',
      accessor: 'satici',
      Cell: ({ value }) => <span className="sales-order-doc-sum-table__td--satici sales-order-doc-sum-table__th--satici">{value}</span>,
      Filter: ColumnFilter,
      filterClassName: 'sales-order-doc-sum-table__filter'
    },
    {
      Header: 'Belge Tarihi',
      accessor: 'belge_tarih',
      Cell: ({ value }) => formatDate(value),
      Filter: props => (
        <div onClick={e => e.stopPropagation()}>
          <DateRangeColumnFilter {...props} />
        </div>
      ),
      filter: 'betweenDates',
      sortType: sortDateValues,
      width: 90,
      className: 'sales-order-doc-sum-table__td--date',
    },
    {
      Header: 'Teslim Tarihi',
      accessor: 'teslim_tarih',
      Cell: ({ value }) => formatDate(value),
      Filter: props => (
        <div onClick={e => e.stopPropagation()}>
          <DateRangeColumnFilter {...props} />
        </div>
      ),
      filter: 'betweenDates',
      sortType: sortDateValues,
      width: 90,
      className: 'sales-order-doc-sum-table__td--date',
    },
    { Header: 'Müşteri Kodu', accessor: 'musteri_kod', Filter: ColumnFilter },
    {
  Header: 'Müşteri Adı',
  accessor: 'musteri_ad',
  /* ✅ 25 karakter + tooltip + ellipsis */
  Cell: ({ value }) => {
    if (!value) return null;
    const truncated = value.length > 25
      ? `${value.slice(0, 25)}…`
      : value;
    return (
      <span
        title={value}
        className="sales-order-doc-sum-table__td--musteri-ad sales-order-doc-sum__ellipsis"
      >
        {truncated}
      </span>
    );
  },
      Filter: ({ column: { filterValue, setFilter } }) => (
        <div className="sales-order-doc-sum-table__filter--musteri-ad">
          <input
            value={filterValue || ''}
            onChange={e => setFilter(turkishToUpperCase(e.target.value))}
            onClick={e => e.stopPropagation()}
            placeholder="Ara..."
            className="sales-order-doc-sum-table__filter--sap-yellow"
          />
        </div>
      )
    },
    { 
      Header: 'Satış Tipi', 
      accessor: 'satis_tipi', 
      Filter: ColumnFilter, 
      filterClassName: 'sales-order-doc-sum-table__filter sales-order-doc-sum-table__filter input' 
    },
    {
      Header: 'Iskonto',
      accessor: 'belge_iskonto_oran',
      Cell: ({ value }) => <FormatNumber value={value} className='sales-order-doc-sum-table__td--numeric' />,
      disableFilters: true
    },
    {
      Header: () => (
        <div style={{ textAlign: 'right' }}>
          NetTutarYPB
          <div>
            <FormatNumber value={uppertotals.net_tutar_ypb} />
          </div>
        </div>
      ),
      accessor: 'net_tutar_ypb',
      Cell: ({ value }) => <FormatNumber value={value} className='sales-order-doc-sum-table__td--numeric' />,
      disableFilters: true
    },
    {
      Header: () => (
        <div style={{ textAlign: 'right' }}>
          NetTutarSPB
          <div>
            <FormatNumber value={uppertotals.net_tutar_spb} />
          </div>
        </div>
      ),
      accessor: 'net_tutar_spb',
      Cell: ({ value }) => <FormatNumber value={value} className='sales-order-doc-sum-table__td--numeric' />,
      disableFilters: true
    },
    {
      Header: () => (
        <div style={{ textAlign: 'right' }}>
          AcikNetYPB
          <div>
            <FormatNumber value={uppertotals.acik_net_tutar_ypb} />
          </div>
        </div>
      ),
      accessor: 'acik_net_tutar_ypb',
      Cell: ({ value }) => <FormatNumber value={value} className='sales-order-doc-sum-table__td--numeric' />,
      disableFilters: true
    },
    {
      Header: () => (
        <div style={{ textAlign: 'right' }}>
          AcikNetSPB
          <div>
            <FormatNumber value={uppertotals.acik_net_tutar_spb} />
          </div>
        </div>
      ),
      accessor: 'acik_net_tutar_spb',
      Cell: ({ value }) => <FormatNumber value={value} className='sales-order-doc-sum-table__td--numeric' />,
      disableFilters: true
    },
    {
      Header: 'Belge Açıklaması',
      accessor: 'belge_aciklamasi',
      Cell: ({ value }) => (
        <span className="sales-order-doc-sum-table__td--belge-aciklamasi">
          {value}
        </span>
      ),
      Filter: ({ column: { filterValue, setFilter } }) => (
        <div className="sales-order-doc-sum-table__filter--belge-aciklamasi">
          <input
            value={filterValue || ''}
            onChange={e => setFilter(turkishToUpperCase(e.target.value))}
            onClick={e => e.stopPropagation()}
            placeholder="Ara..."
            className="sales-order-doc-sum-table__filter--sap-yellow"
            style={{ width: '100%' }}
          />
        </div>
      )
    },
  ], [uppertotals, openModal, sortDateValues])


  const filterTypes = useMemo(() => ({
    betweenDates: (rows, id, filterValue) => {
      const [start, end] = filterValue;
      if (!start && !end) return rows;

      const resetTime = (date) => {
        return date ? new Date(date.setHours(0, 0, 0, 0)) : null;
      };

      const startDate = resetTime(start);
      const endDate = resetTime(end);

      return rows.filter(row => {
        const rowDate = resetTime(new Date(row.values[id]));

        if (startDate && endDate) {
          return rowDate >= startDate && rowDate <= endDate;
        } else if (startDate) {
          return rowDate >= startDate;
        } else if (endDate) {
          return rowDate <= endDate;
        }
        return true;
      });
    },
  }), []);

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    prepareRow,
    rows,
    page,
    canPreviousPage,
    canNextPage,
    pageCount,
    gotoPage,
    nextPage,
    previousPage,
    setPageSize,
    state: { pageIndex, pageSize }
  } = useTable(
    {
      columns,
      data: documentSummaries || [],
      filterTypes,
      initialState: {
        pageIndex: 0,
        pageSize: 10,
        sortBy: [{ id: 'belge_tarih', desc: true }]
      },
      defaultColumn: { Filter: ColumnFilter },
      autoResetPage: false,
      autoResetFilters: false,
      autoResetSortBy: false
    },
    useFilters,
    useSortBy,
    usePagination
  );

  const subtotals = useDynamicSubtotals(rows, 'musteri_kod', [
    'net_tutar_ypb',
    'net_tutar_spb',
    'acik_net_tutar_ypb',
    'acik_net_tutar_spb'
  ]);

  if (!documentSummaries) {
    return null;
  }

  return (
    <div className="sales-order-doc-sum-table-wrapper">
      <Pagination
        canPreviousPage={canPreviousPage}
        canNextPage={canNextPage}
        nextPage={nextPage}
        previousPage={previousPage}
        setPageSize={setPageSize}
        pageIndex={pageIndex}
        pageSize={pageSize}
        gotoPage={gotoPage}
        pageCount={pageCount}
      />

      <table {...getTableProps()} className="sales-order-doc-sum-table table table-sm table-striped table-hover">
        <thead>
          {headerGroups.map(headerGroup => (
            <tr {...headerGroup.getHeaderGroupProps()} className="sales-order-doc-sum-table__thead--header">
              {headerGroup.headers.map(column => (
                <th {...column.getHeaderProps(column.getSortByToggleProps())} className="text-left">
                  {column.render('Header')}
                  <span>
                    {column.isSorted ? (column.isSortedDesc ? ' ↓' : ' ↑') : ''}
                  </span>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    {column.canFilter ? column.render('Filter') : null}
                  </div>
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
                  <td {...cell.getCellProps()} className={cell.column.id.includes('net_tutar_ypb') ? 'sales-order-doc-sum-table__td--numeric' : ''}>
                    {cell.render('Cell')}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
        <tfoot>
          <tr>
            <td className="footer-cell" colSpan="9">Dinamik Alt Toplamlar</td>
            <td className="footer-cell"><FormatNumber value={subtotals.net_tutar_ypb} /></td>
            <td className="footer-cell"><FormatNumber value={subtotals.net_tutar_spb} /></td>
            <td className="footer-cell"><FormatNumber value={subtotals.acik_net_tutar_ypb} /></td>
            <td className="footer-cell"><FormatNumber value={subtotals.acik_net_tutar_spb} /></td>
          </tr>
        </tfoot>
      </table>

      {modalBelgeNo && (
        <ShowModalOrderDocDetail
          masterBelgeGirisNo={modalBelgeNo}
          isOpen={isModalOpen}
          onRequestClose={closeModal}
        />
      )}
    </div>
  );
}, (prevProps, nextProps) => {
  // Sadece documentSummaries değiştiğinde render et
  return prevProps.documentSummaries === nextProps.documentSummaries;
});

export default React.memo(SalesOrderDocSumTable);
