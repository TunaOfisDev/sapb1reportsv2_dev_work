/* eslint-disable react/jsx-key */
// frontend/src/components/DeliveryDocSum/containers/DeliveryDocSumTable.js
import React, { useState, useMemo } from 'react';
import { useTable, useSortBy, useFilters, usePagination } from 'react-table';
import FormatNumber from '../utils/FormatNumber';
import Pagination from '../utils/Pagination';
import ColumnFilter from '../utils/ColumnFilter';
import UpperTotal from '../utils/UpperTotal';
import ShowModalOrderNumbers from '../utils/ShowModalOrderNumbers';
import '../css/DeliveryDocSumTable.css';
          

const DeliveryDocSumTable = ({ data }) => {
  const defaultColumn = useMemo(() => ({
    Filter: ColumnFilter,
    headerClassName: 'delivery-doc-sum__table-header',
    className: 'delivery-doc-sum__table-cell',
  }), []);

  const columnTotals = UpperTotal(data);

  const [modalIsOpen, setModalIsOpen] = useState(false);
  const [selectedOrders, setSelectedOrders] = useState('');
  const [cariKod, setCariKod] = useState('');
  const [cariAdi, setCariAdi] = useState('');

  const handleOpenModal = (orders, kod, adi) => {
    setSelectedOrders(orders);
    setCariKod(kod);
    setCariAdi(adi);
    setModalIsOpen(true);
  };

  const handleCloseModal = () => {
    setModalIsOpen(false);
  };

  const columns = useMemo(() => [
  
      {
        Header: 'Temsilci',
        accessor: 'temsilci',
        Filter: ColumnFilter,
        headerClassName: 'delivery-doc-sum__table-header',
        className: 'delivery-doc-sum__table-cell',
      },
      {
        Header: 'Cari Grup',
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
          const truncated = value.length > 20
            ? `${value.slice(0, 20)}…`
            : value;
          return (
            <span title={value} className="ellipsis-cell">
              {truncated}
            </span>
          );
        },
      },
      {
        Header: () => (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
            <span>Günlük Toplam</span>
            <FormatNumber value={columnTotals.gunluk_toplam} />
          </div>
        ),
        accessor: 'gunluk_toplam',
        Cell: ({ row }) => (
          <div style={{ textAlign: 'right', cursor: 'pointer', color: '#007bff', fontWeight: 'bold' }} onClick={() => handleOpenModal(row.original.gunluk_ilgili_siparis_numaralari, row.original.cari_kod, row.original.cari_adi)}>
            <FormatNumber value={row.values.gunluk_toplam} />
          </div>
      ),
        disableFilters: true,
        headerClassName: 'delivery-doc-sum__table-header delivery-doc-sum__table-header--right',
        className: 'delivery-doc-sum__table-cell delivery-doc-sum__table-cell--right',
      },
      {
        Header: () => (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
            <span>Dun Toplamı</span>
            <FormatNumber value={columnTotals.dun_toplam} />
          </div>
        ),
        accessor: 'dun_toplam',
        Cell: ({ row }) => (
          <div style={{ textAlign: 'right', cursor: 'pointer', color: '#007bff', fontWeight: 'bold' }} onClick={() => handleOpenModal(row.original.dun_ilgili_siparis_numaralari, row.original.cari_kod, row.original.cari_adi)}>
            <FormatNumber value={row.values.dun_toplam} />
          </div>
        ),
        disableFilters: true,
        headerClassName: 'delivery-doc-sum__table-header delivery-doc-sum__table-header--right',
        className: 'delivery-doc-sum__table-cell delivery-doc-sum__table-cell--numeric',
      },
      {
        Header: () => (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
            <span>Onceki Gun Toplamı</span>
            <FormatNumber value={columnTotals.onceki_gun_toplam} />
          </div>
        ),
        accessor: 'onceki_gun_toplam',
        Cell: ({ row }) => (
          <div style={{ textAlign: 'right', cursor: 'pointer', color: '#007bff', fontWeight: 'bold' }} onClick={() => handleOpenModal(row.original.onceki_gun_ilgili_siparis_numaralari, row.original.cari_kod, row.original.cari_adi)}>
            <FormatNumber value={row.values.onceki_gun_toplam} />
          </div>
        ),
        disableFilters: true,
        headerClassName: 'delivery-doc-sum__table-header delivery-doc-sum__table-header--right',
        className: 'delivery-doc-sum__table-cell delivery-doc-sum__table-cell--numeric',
      },
      {
        Header: () => (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
            <span>Aylık Toplam</span>
            <FormatNumber value={columnTotals.aylik_toplam} />
          </div>
        ),
        accessor: 'aylik_toplam',
        Cell: ({ value }) => <div style={{ textAlign: 'right' }}><FormatNumber value={value} /></div>,
        disableFilters: true,
        headerClassName: 'delivery-doc-sum__table-header delivery-doc-sum__table-header--right',
        className: 'delivery-doc-sum__table-cell delivery-doc-sum__table-cell--numeric',
      },
      {
        Header: () => (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
            <span>Yıllık Toplam</span>
            <FormatNumber value={columnTotals.yillik_toplam} />
          </div>
        ),
        accessor: 'yillik_toplam',
        Cell: ({ value }) => <div style={{ textAlign: 'right' }}><FormatNumber value={value} /></div>,
        disableFilters: true,
        headerClassName: 'delivery-doc-sum__table-header delivery-doc-sum__table-header--right',
        className: 'delivery-doc-sum__table-cell delivery-doc-sum__table-cell--numeric',
      },
      {
        Header: () => (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
            <span>Açık Sevkiyat Toplamı</span>
            <FormatNumber value={columnTotals.acik_sevkiyat_toplami} />
          </div>
        ),
        accessor: 'acik_sevkiyat_toplami',
        Cell: ({ value }) => <div style={{ textAlign: 'right' }}><FormatNumber value={value} /></div>,
        disableFilters: true,
        headerClassName: 'delivery-doc-sum__table-header delivery-doc-sum__table-header--right',
        className: 'delivery-doc-sum__table-cell delivery-doc-sum__table-cell--numeric',
      },
      {
        Header: () => (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
            <span>Açık Sipariş Toplamı</span>
            <FormatNumber value={columnTotals.acik_siparis_toplami} />
          </div>
        ),
        accessor: 'acik_siparis_toplami',
        Cell: ({ value }) => <div style={{ textAlign: 'right' }}><FormatNumber value={value} /></div>,
        disableFilters: true,
        headerClassName: 'delivery-doc-sum__table-header delivery-doc-sum__table-header--right',
        className: 'delivery-doc-sum__table-cell delivery-doc-sum__table-cell--numeric',
      },
      {
        Header: () => (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
            <span>İrsaliye Sayısı</span>
            <FormatNumber value={columnTotals.irsaliye_sayisi} />
          </div>
        ),
        accessor: 'irsaliye_sayisi',
        Cell: ({ value }) => <div style={{ textAlign: 'right' }}><FormatNumber value={value} /></div>,
        disableFilters: true,
        headerClassName: 'delivery-doc-sum__table-header delivery-doc-sum__table-header--right',
        className: 'delivery-doc-sum__table-cell',
      },
      
    ],
    [columnTotals]
  );  

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
                <th {...column.getHeaderProps()}>
                  <div onClick={() => column.toggleSortBy()}>
                    {column.render('Header')}
                    <span>
                      {column.isSorted ? (column.isSortedDesc ? ' ↓' : ' ↑') : ''}
                    </span>
                  </div>
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
      </table>

       {/* Modal for showing order numbers */}
       <ShowModalOrderNumbers
        modalIsOpen={modalIsOpen}
        closeModal={handleCloseModal}
        selectedOrders={selectedOrders}
        cariKod={cariKod}
        cariAdi={cariAdi}
      />
    </div>
  );
};

export default DeliveryDocSumTable;
