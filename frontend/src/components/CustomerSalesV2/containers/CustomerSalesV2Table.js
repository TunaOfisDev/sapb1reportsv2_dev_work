import React, { useMemo } from 'react';
import PropTypes from 'prop-types';
import { useTable, useSortBy, useFilters, usePagination, useFlexLayout } from 'react-table';
import { Spin, Alert } from 'antd';

// Varsayılan olarak bu yardımcı bileşenlerin utils klasöründe olduğunu varsayıyoruz.
import { formatNumber } from '../utils/FormatNumber';
import { ColumnFilter } from '../utils/ColumnFilter';
import { DynamicSubTotal } from '../utils/DynamicSubTotal';
import { Pagination } from '../utils/Pagination';

// Referans alınan CSS dosyasını V2 için de kullanabiliriz.
import '../css/CustomerSalesV2Table.css';

/**
 * Müşteri satış verilerini sıralama, filtreleme, sayfalama ve alt toplam
 * özellikleriyle gösteren gelişmiş tablo bileşeni.
 * @param {object} props
 * @param {Array<object>} props.data - Tabloda gösterilecek veri dizisi.
 * @param {object} props.summaryData - Raporun genel toplamlarını içeren nesne.
 * @param {boolean} props.isLoading - Verinin yüklenip yüklenmediğini belirten durum.
 * @param {boolean} props.isError - Veri çekme sırasında hata olup olmadığını belirten durum.
 */
const CustomerSalesV2Table = ({ data, summaryData, isLoading, isError }) => {
  // Her kolon için varsayılan filtre bileşenini tanımlıyoruz.
  const defaultColumn = useMemo(() => ({
    Filter: ColumnFilter,
  }), []);

  // Sütunları ve veriyi useMemo ile sarmalayarak performans optimizasyonu yapıyoruz.
  const columns = useMemo(() => {
    // Sadece toplamı sıfırdan büyük olan ayları gösterelim (dinamik kolonlar)
    const months = [
      { key: 'ocak', label: 'Ocak' }, { key: 'subat', label: 'Şubat' }, { key: 'mart', label: 'Mart' },
      { key: 'nisan', label: 'Nisan' }, { key: 'mayis', label: 'Mayıs' }, { key: 'haziran', label: 'Haziran' },
      { key: 'temmuz', label: 'Temmuz' }, { key: 'agustos', label: 'Ağustos' }, { key: 'eylul', label: 'Eylül' },
      { key: 'ekim', label: 'Ekim' }, { key: 'kasim', label: 'Kasım' }, { key: 'aralik', label: 'Aralık' }
    ];
    
    // Ant Design'dan gelen summaryData isimleri farklı olabilir, eşleştirme yapıyoruz.
    const monthTotals = {
        ocak: summaryData.Ocak, subat: summaryData.Şubat, mart: summaryData.Mart, nisan: summaryData.Nisan,
        mayis: summaryData.Mayıs, haziran: summaryData.Haziran, temmuz: summaryData.Temmuz, agustos: summaryData.Ağustos,
        eylul: summaryData.Eylül, ekim: summaryData.Ekim, kasim: summaryData.Kasım, aralik: summaryData.Aralık,
    };

    const visibleMonths = months.filter(month => parseFloat(monthTotals[month.key]) > 0);

    return [
      { Header: 'Satıcı', accessor: 'satici' },
      { Header: 'Satış Tipi', accessor: 'satis_tipi' },
      { Header: 'Cari Grup', accessor: 'cari_grup' },
      { Header: 'Müşteri Kodu', accessor: 'musteri_kodu' },
      { Header: 'Müşteri Adı', accessor: 'musteri_adi', Footer: () => <div style={{ textAlign: 'right', fontWeight: 'bold' }}>Dinamik Toplam:</div> },
      {
        Header: () => <>Toplam Yıllık <br /> {formatNumber(summaryData.ToplamNetSPB_EUR)}</>,
        accessor: 'toplam_net_spb_eur',
        Cell: ({ value }) => formatNumber(value),
        Footer: (info) => <DynamicSubTotal rows={info.rows} columnId="toplam_net_spb_eur" />,
        disableFilters: true,
        className: 'td-numeric td-total',
      },
      // Sadece verisi olan ayları dinamik olarak ekle
      ...visibleMonths.map(month => ({
        Header: () => <>{month.label} <br /> {formatNumber(monthTotals[month.key])}</>,
        accessor: month.key,
        Cell: ({ value }) => formatNumber(value),
        Footer: (info) => <DynamicSubTotal rows={info.rows} columnId={month.key} />,
        disableFilters: true,
        className: 'td-numeric',
      })),
    ];
  }, [summaryData]);

  const tableData = useMemo(() => data, [data]);

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
    footerGroups,
  } = useTable(
    {
      columns,
      data: tableData,
      defaultColumn,
      initialState: { pageIndex: 0, pageSize: 25, sortBy: [{ id: 'toplam_net_spb_eur', desc: true }] },
    },
    useFilters,
    useSortBy,
    usePagination,
    useFlexLayout // Sütun genişliklerini daha iyi yönetmek için
  );

  if (isLoading) {
    return <div style={{ textAlign: 'center', padding: '50px' }}><Spin size="large" tip="Veriler Yükleniyor..." /></div>;
  }

  if (isError) {
    return <Alert message="Veri Yüklenemedi" description="Rapor verileri çekilirken bir hata oluştu." type="error" showIcon />;
  }

  return (
    <>
      <div className="pagination-wrapper">
        <Pagination
          pageCount={pageCount}
          pageIndex={pageIndex}
          gotoPage={gotoPage}
          nextPage={nextPage}
          previousPage={previousPage}
          setPageSize={setPageSize}
          pageSize={pageSize}
          canNextPage={canNextPage}
          canPreviousPage={canPreviousPage}
        />
      </div>
      <div className="customersalesv2-table-wrapper">
        <table {...getTableProps()} className="customersalesv2-table">
          <thead>
            {headerGroups.map(headerGroup => (
              <tr {...headerGroup.getHeaderGroupProps()}>
                {headerGroup.headers.map(column => (
                  <th {...column.getHeaderProps(column.getSortByToggleProps())}>
                    {column.render('Header')}
                    <span>{column.isSorted ? (column.isSortedDesc ? ' 🔽' : ' 🔼') : ''}</span>
                    <div>{column.canFilter ? column.render('Filter') : null}</div>
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
                    <td {...cell.getCellProps()} className={cell.column.className}>
                      {cell.render('Cell')}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
          <tfoot>
            {footerGroups.map(group => (
              <tr {...group.getFooterGroupProps()}>
                {group.headers.map(column => (
                  <td {...column.getFooterProps()} className="td-numeric td-total">
                    {column.render('Footer')}
                  </td>
                ))}
              </tr>
            ))}
          </tfoot>
        </table>
      </div>
    </>
  );
};

CustomerSalesV2Table.propTypes = {
  data: PropTypes.array.isRequired,
  summaryData: PropTypes.object.isRequired,
  isLoading: PropTypes.bool,
  isError: PropTypes.bool,
};

export default CustomerSalesV2Table;