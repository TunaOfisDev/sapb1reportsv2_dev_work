/* eslint-disable react/jsx-key */
// frontend/src/components/DeliveryDocSumV2/containers/DeliveryDocSumTable.js
import React, { useState, useMemo } from 'react';
import { useTable, useSortBy, useFilters, usePagination } from 'react-table';
import FormatNumber from '../utils/FormatNumber';
import Pagination from '../utils/Pagination';
import ColumnFilter from '../utils/ColumnFilter';
import ShowModalOrderNumbers from '../utils/ShowModalOrderNumbers';
import ShowModalOpenDelivery from '../utils/ShowModalOpenDelivery';
import useDynamicSubtotals from '../utils/DynamicSubTotal';
import '../css/DeliveryDocSumTable.css';

const DeliveryDocSumTable = ({ data, columnNames }) => { // columnNames prop olarak alınıyor

  const columns = useMemo(() => [
    {
      Header: 'Temsilci',
      accessor: 'temsilci',
      Filter: ColumnFilter,
      headerClassName: 'delivery-doc-sum__table-header',
      className: 'delivery-doc-sum__table-cell',
    },
    {
      Header: 'Grup',
      accessor: 'cari_grup',
      Filter: ColumnFilter,
      headerClassName: 'delivery-doc-sum__table-header',
      className: 'delivery-doc-sum__table-cell',
    },
    {
      Header: 'Cari Kod',
      accessor: 'cari_kod',
      Filter: ColumnFilter,
      headerClassName: 'delivery-doc-sum__table-header',
      className: 'delivery-doc-sum__table-cell',
    },
    
    {
      Header: 'Cari Adı',
      accessor: 'cari_adi',
      Filter: ColumnFilter,
      headerClassName: 'delivery-doc-sum__table-header',
      className: 'delivery-doc-sum__table-cell',
      // ✅ metni kısalt + tooltip
      Cell: ({ value }) => {
        if (!value) return null;                     // boş güvenliği
        const truncated = value.length > 15
          ? `${value.slice(0, 15)}…`
          : value;
        return (
          <span title={value} className="ellipsis-cell">
            {truncated}
          </span>
        );
      },
    },
    
    {
      Header: columnNames.today, // Dinamik kolon isimleri
      accessor: 'bugun',
      Cell: ({ row }) => (
        <div style={{ textAlign: 'right', cursor: 'pointer', color: '#007bff', fontWeight: 'bold' }} onClick={() => handleOpenOrderModal(row.original.bugun_ilgili_siparis_numaralari, row.original.cari_kod, row.original.cari_adi)}>
          <FormatNumber value={row.values.bugun} />
        </div>
      ),
      disableFilters: true,
      headerClassName: 'delivery-doc-sum__table-header delivery-doc-sum__table-header--right',
      className: 'delivery-doc-sum__table-cell delivery-doc-sum__table-cell--numeric',
    },
    {
      Header: columnNames.yesterday, // Dinamik kolon isimleri
      accessor: 'bugun_minus_1',
      Cell: ({ row }) => (
        <div style={{ textAlign: 'right', cursor: 'pointer', color: '#007bff', fontWeight: 'bold' }} onClick={() => handleOpenOrderModal(row.original.bugun_minus_1_ilgili_siparis_numaralari, row.original.cari_kod, row.original.cari_adi)}>
          <FormatNumber value={row.values.bugun_minus_1} />
        </div>
      ),
      disableFilters: true,
      headerClassName: 'delivery-doc-sum__table-header delivery-doc-sum__table-header--right',
      className: 'delivery-doc-sum__table-cell delivery-doc-sum__table-cell--numeric',
    },
    {
      Header: columnNames.dayBeforeYesterday,
      accessor: 'bugun_minus_2',
      Cell: ({ row }) => (
        <div style={{ textAlign: 'right', cursor: 'pointer', color: '#007bff', fontWeight: 'bold' }} onClick={() => handleOpenOrderModal(row.original.bugun_minus_2_ilgili_siparis_numaralari, row.original.cari_kod, row.original.cari_adi)}>
          <FormatNumber value={row.values.bugun_minus_2} />
        </div>
      ),
      disableFilters: true,
      headerClassName: 'delivery-doc-sum__table-header delivery-doc-sum__table-header--right',
      className: 'delivery-doc-sum__table-cell delivery-doc-sum__table-cell--numeric',
    },
    {
      Header: columnNames.threeDaysAgo,
      accessor: 'bugun_minus_3',
      Cell: ({ row }) => (
        <div style={{ textAlign: 'right', cursor: 'pointer', color: '#007bff', fontWeight: 'bold' }} onClick={() => handleOpenOrderModal(row.original.bugun_minus_3_ilgili_siparis_numaralari, row.original.cari_kod, row.original.cari_adi)}>
          <FormatNumber value={row.values.bugun_minus_3} />
        </div>
      ),
      disableFilters: true,
      headerClassName: 'delivery-doc-sum__table-header delivery-doc-sum__table-header--right',
      className: 'delivery-doc-sum__table-cell delivery-doc-sum__table-cell--numeric',
    },
    {
      Header: columnNames.fourDaysAgo,
      accessor: 'bugun_minus_4',
      Cell: ({ row }) => (
        <div style={{ textAlign: 'right', cursor: 'pointer', color: '#007bff', fontWeight: 'bold' }} onClick={() => handleOpenOrderModal(row.original.bugun_minus_4_ilgili_siparis_numaralari, row.original.cari_kod, row.original.cari_adi)}>
          <FormatNumber value={row.values.bugun_minus_4} />
        </div>
      ),
      disableFilters: true,
      headerClassName: 'delivery-doc-sum__table-header delivery-doc-sum__table-header--right',
      className: 'delivery-doc-sum__table-cell delivery-doc-sum__table-cell--numeric',
    },
    {
      Header: columnNames.thisMonth,
      accessor: 'bu_ay_toplam',
      Cell: ({ row }) => (
        <div style={{ textAlign: 'right', cursor: 'pointer', color: '#007bff', fontWeight: 'bold' }} onClick={() => handleOpenOrderModal(row.original.bu_ay_ilgili_siparis_numaralari, row.original.cari_kod, row.original.cari_adi)}>
          <FormatNumber value={row.values.bu_ay_toplam} />
        </div>
      ),
      disableFilters: true,
      headerClassName: 'delivery-doc-sum__table-header delivery-doc-sum__table-header--right',
      className: 'delivery-doc-sum__table-cell delivery-doc-sum__table-cell--numeric',
    },
    {
      Header: columnNames.lastMonth,
      accessor: 'bu_ay_minus_1_toplam',
      Cell: ({ row }) => (
        <div style={{ textAlign: 'right', cursor: 'pointer', color: '#007bff', fontWeight: 'bold' }} onClick={() => handleOpenOrderModal(row.original.bu_ay_minus_1_ilgili_siparis_numaralari, row.original.cari_kod, row.original.cari_adi)}>
          <FormatNumber value={row.values.bu_ay_minus_1_toplam} />
        </div>
      ),
      disableFilters: true,
      headerClassName: 'delivery-doc-sum__table-header delivery-doc-sum__table-header--right',
      className: 'delivery-doc-sum__table-cell delivery-doc-sum__table-cell--numeric',
    },
    {
      Header: columnNames.thisYear,
      accessor: 'yillik_toplam',
      Cell: ({ row }) => (
        <div style={{ textAlign: 'right', cursor: 'pointer', fontWeight: 'bold' }}>
          <FormatNumber value={row.values.yillik_toplam} />
        </div>
      ),
      disableFilters: true,
      headerClassName: 'delivery-doc-sum__table-header delivery-doc-sum__table-header--right',
      className: 'delivery-doc-sum__table-cell delivery-doc-sum__table-cell--numeric',
    },
    {
      Header: 'Açık Sevkiyat Toplamı',
      accessor: 'acik_sevkiyat_toplami',
      Cell: ({ row }) => (
        <div style={{ textAlign: 'right', cursor: 'pointer', color: '#007bff', fontWeight: 'bold' }} onClick={() => handleOpenDeliveryModal(row.original.acik_irsaliye_belge_no_tarih_tutar, row.original.cari_kod, row.original.cari_adi)}>
          <FormatNumber value={row.values.acik_sevkiyat_toplami} />
        </div>
      ),
      disableFilters: true,
      headerClassName: 'delivery-doc-sum__table-header delivery-doc-sum__table-header--right',
      className: 'delivery-doc-sum__table-cell delivery-doc-sum__table-cell--numeric',
    },
    {
      Header: 'Açık Sipariş Toplamı',
      accessor: 'acik_siparis_toplami',
      Cell: ({ row }) => (
        <div style={{ textAlign: 'right', cursor: 'pointer', fontWeight: 'bold' }}>
          <FormatNumber value={row.values.acik_siparis_toplami} />
        </div>
      ),
      disableFilters: true,
      headerClassName: 'delivery-doc-sum__table-header delivery-doc-sum__table-header--right',
      className: 'delivery-doc-sum__table-cell delivery-doc-sum__table-cell--numeric',
    },
    {
      Header: 'İrsaliye Sayısı',
      accessor: 'irsaliye_sayisi',
      Cell: ({ row }) => (
        <div style={{ textAlign: 'right', cursor: 'pointer', fontWeight: 'bold' }}>
          <FormatNumber value={row.values.irsaliye_sayisi} />
        </div>
      ),
      disableFilters: true,
      headerClassName: 'delivery-doc-sum__table-header delivery-doc-sum__table-header--right',
      className: 'delivery-doc-sum__table-cell delivery-doc-sum__table-cell--numeric',
    },
  ], [columnNames]);

  const defaultColumn = useMemo(() => ({
    Filter: ColumnFilter,
    headerClassName: 'delivery-doc-sum__table-header',
    className: 'delivery-doc-sum__table-cell',
  }), []);

  const [orderModalIsOpen, setOrderModalIsOpen] = useState(false);
  const [deliveryModalIsOpen, setDeliveryModalIsOpen] = useState(false);
  const [selectedOrders, setSelectedOrders] = useState('');
  const [selectedDeliveries, setSelectedDeliveries] = useState('');
  const [cariKod, setCariKod] = useState('');
  const [cariAdi, setCariAdi] = useState('');

  const handleOpenOrderModal = (orders, kod, adi) => {
    setSelectedOrders(orders);
    setCariKod(kod);
    setCariAdi(adi);
    setOrderModalIsOpen(true);
  };

  const handleCloseOrderModal = () => {
    setOrderModalIsOpen(false);
  };

  const handleOpenDeliveryModal = (deliveries, kod, adi) => {
    setSelectedDeliveries(deliveries);
    setCariKod(kod);
    setCariAdi(adi);
    setDeliveryModalIsOpen(true);
  };

  const handleCloseDeliveryModal = () => {
    setDeliveryModalIsOpen(false);
  };

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    prepareRow,
    page,
    canPreviousPage,
    canNextPage,
    pageCount,
    gotoPage,
    nextPage,
    previousPage,
    setPageSize,
    state: { pageIndex, pageSize },
    rows
  } = useTable(
    {
      columns,
      data,
      defaultColumn,
      initialState: { pageIndex: 0, pageSize: 10, sortBy: [{ id: 'yillik_toplam', desc: true }] },
    },
    useFilters,
    useSortBy,
    usePagination
  );

  const subtotals = useDynamicSubtotals(rows, ['bugun', 'bugun_minus_1', 'bugun_minus_2', 'bugun_minus_3', 'bugun_minus_4', 'bu_ay_toplam', 'bu_ay_minus_1_toplam', 'yillik_toplam', 'acik_sevkiyat_toplami', 'acik_siparis_toplami', 'irsaliye_sayisi']);

  return (
    <div>
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
      <table {...getTableProps()} className="delivery-doc-sum__table">
        <thead>
          {headerGroups.map(headerGroup => (
            <tr {...headerGroup.getHeaderGroupProps()}>
              {headerGroup.headers.map(column => (
                <th {...column.getHeaderProps(column.getSortByToggleProps())}>
                  {column.render('Header')}
                  <div>{column.canFilter ? column.render('Filter') : null}</div>
                  <span>
                    {column.isSorted ? (column.isSortedDesc ? ' ↓' : ' ↑') : ''}
                  </span>
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
                  <td {...cell.getCellProps()}>
                    {cell.render('Cell')}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
        <tfoot>
          <tr>
            <td colSpan={4} style={{ textAlign: 'right', fontWeight: 'bold' }}>Toplam</td>
            {['bugun', 'bugun_minus_1', 'bugun_minus_2', 'bugun_minus_3', 'bugun_minus_4', 'bu_ay_toplam', 'bu_ay_minus_1_toplam', 'yillik_toplam', 'acik_sevkiyat_toplami', 'acik_siparis_toplami', 'irsaliye_sayisi'].map((accessor, index) => (
              <td key={index} style={{ textAlign: 'right', fontWeight: 'bold' }}>
                <FormatNumber value={subtotals[accessor]} />
              </td>
            ))}
          </tr>
        </tfoot>
      </table>

      {/* Modal for showing order numbers */}
      <ShowModalOrderNumbers
        modalIsOpen={orderModalIsOpen}
        closeModal={handleCloseOrderModal}
        selectedOrders={selectedOrders}
        cariKod={cariKod}
        cariAdi={cariAdi}
      />

      {/* Modal for showing open deliveries */}
      <ShowModalOpenDelivery
        modalIsOpen={deliveryModalIsOpen}
        closeModal={handleCloseDeliveryModal}
        selectedDeliveries={selectedDeliveries}
        cariKod={cariKod}
        cariAdi={cariAdi}
      />
    </div>
  );
};

export default DeliveryDocSumTable;