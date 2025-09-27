/* eslint-disable react/jsx-key */
// frontend/src/components/SalesOfferDocSum/containers/SalesOfferDocSumTable.js
import React, { useMemo, useState, useCallback } from 'react';
import { useTable, useSortBy, useFilters, usePagination } from 'react-table';
import Pagination from '../utils/Pagination';
import useSalesOfferDocSum from '../hooks/useSalesOfferDocSum';
import FormatNumber from '../utils/FormatNumber';
import formatDate from '../utils/DateFormat';
import ColumnFilter from '../utils/ColumnFilter';
import DateColumnFilter from '../utils/DateColumnFilter';
import useUpperTotal from '../utils/UpperTotal';
import useDynamicSubtotals from '../utils/DynamicSubTotal';
import ShowModalOfferDocDetail from '../utils/ShowModalOfferDocDetail';
import '../css/SalesOfferDocSumTable.css';

const SalesOfferDocSumTable = () => {
  const { documentSummaries, loading, error } = useSalesOfferDocSum();
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

  const uppertotals = useUpperTotal(documentSummaries);




  const columns = useMemo(() => [
    {
      Header: 'No',
      accessor: 'belge_no',
      Filter: ColumnFilter,
      Cell: ({ value }) => (
        <span
          className="sales-offer-doc-sum__td--belge-no"
          onClick={() => openModal(value)}
          style={{ cursor: 'pointer', color: 'blue' }}
        >
          {value}
        </span>
      )
    },
    { Header: 'Statu', accessor: 'belge_durum', Filter: ColumnFilter },
    { Header: 'Iptal', accessor: 'iptal_edilen', Filter: ColumnFilter },
    { Header: 'ElleKapama', accessor: 'elle_kapatilan', Filter: ColumnFilter },
    { Header: 'Siparis', accessor: 'siparise_aktarilan', Filter: ColumnFilter },
    {
      Header: 'Satıcı',
      accessor: 'satici',
      Filter: ColumnFilter
    },
    { 
      Header: 'BelgeTarihi', 
      accessor: 'belge_tarih', 
      Cell: ({ value }) => formatDate(value), 
      Filter: DateColumnFilter 
    },
    { 
      Header: 'TeslimTarihi', 
      accessor: 'teslim_tarih', 
      Cell: ({ value }) => formatDate(value), 
      Filter: DateColumnFilter 
    },
    {
      Header: 'MüşteriAdı',
      accessor: 'musteri_ad',
      Filter: ColumnFilter,
      /* ✅ 25 karakter + tooltip + ellipsis */
      Cell: ({ value }) => {
        if (!value) return null;
        const truncated = value.length > 25
          ? `${value.slice(0, 25)}…`
          : value;
        return (
          <span
            title={value}                                          /* tam metni tooltip olarak göster */
            className="sales-offer-doc-sum__td--musteri-ad sales-offer-doc-sum__ellipsis"
          >
            {truncated}
          </span>
        );
      },
    },

    { 
      Header: 'Tip', 
      accessor: 'satis_tipi', 
      Filter: ColumnFilter 
    },
    {
      Header: 'Isk',
      accessor: 'belge_iskonto_oran',
      Cell: ({ value }) => <FormatNumber value={value} className="sales-offer-doc-sum__td--numeric" />,
      disableFilters: true
    },
    {
      Header: 'BrutSPB',
      accessor: 'brut_tutar_spb',
      Cell: ({ value }) => <FormatNumber value={value} className="sales-offer-doc-sum__td--numeric" />,
      disableFilters: true
    },
    {
      Header: 'NetSPB',
      accessor: 'net_tutar_spb',
      Cell: ({ value }) => <FormatNumber value={value} className="sales-offer-doc-sum__td--numeric" />,
      disableFilters: true
    },
    {
      Header: 'BelgeAciklamasi',
      accessor: 'belge_aciklamasi',
      Filter: ColumnFilter
    }
  ], [openModal]);

  

  const tableInstance = useTable(
    {
      columns,
      data: documentSummaries || [],
      initialState: {
        pageIndex: 0,
        sortBy: [{ id: 'belge_no', desc: true }]
      },
      defaultColumn: { Filter: ColumnFilter }
    },
    useFilters,
    useSortBy,
    usePagination
  );

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
  } = tableInstance;

  const subtotals = useDynamicSubtotals(rows, 'musteri_kod', ['brut_tutar_spb', 'net_tutar_spb']);

  if (loading) return <div>Yükleniyor...</div>;
  if (error) return <div>Hata: {error.message}</div>;

  return (
    <div>
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
      <div className="sales-offer-doc-sum__table-container">
        <table {...getTableProps()} className="sales-offer-doc-sum__table">
          <thead>
            {headerGroups.map(headerGroup => (
              <tr {...headerGroup.getHeaderGroupProps()} className="sales-offer-doc-sum__thead--header">
                {headerGroup.headers.map(column => (
                  <th {...column.getHeaderProps(column.getSortByToggleProps())}>
                    <div className="sales-offer-doc-sum__th-content">
                      {column.render('Header')}
                      {column.id === 'brut_tutar_spb' && (
                        <div className="sales-offer-doc-sum__th-total">
                          <FormatNumber value={uppertotals.brut_tutar_spb} />
                        </div>
                      )}
                      {column.id === 'net_tutar_spb' && (
                        <div className="sales-offer-doc-sum__th-total">
                          <FormatNumber value={uppertotals.net_tutar_spb} />
                        </div>
                      )}
                    </div>
                    <div className="sales-offer-doc-sum__th-filter">
                      {column.canFilter ? column.render('Filter') : null}
                      <span className="sales-offer-doc-sum__sort-icon">
                        {column.isSorted ? (column.isSortedDesc ? ' ↓' : ' ↑') : ''}
                      </span>
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
                    <td 
                      {...cell.getCellProps()}
                      className={
                        cell.column.id === 'net_tutar_spb' || 
                        cell.column.id === 'brut_tutar_spb' || 
                        cell.column.id === 'belge_iskonto_oran'
                          ? 'sales-offer-doc-sum__td--numeric'
                          : ''
                      }
                    >
                      {cell.render('Cell')}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
          <tfoot>
            <tr>
              <td className="footer-cell" colSpan="11">Dinamik Alt Toplamlar</td>
              <td className="footer-cell">
                <FormatNumber value={subtotals.brut_tutar_spb} />
              </td>
              <td className="footer-cell">
                <FormatNumber value={subtotals.net_tutar_spb} />
              </td>
              <td></td>
            </tr>
          </tfoot>
        </table>
      </div>
      {modalBelgeNo && (
        <ShowModalOfferDocDetail
          masterBelgeGirisNo={modalBelgeNo}
          isOpen={isModalOpen}
          onRequestClose={closeModal}
        />
      )}
    </div>
  );
};

export default SalesOfferDocSumTable;