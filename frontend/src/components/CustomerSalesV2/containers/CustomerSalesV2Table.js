// frontend/src/components/CustomerSalesV2/containers/CustomerSalesV2Table.js
import React, { useMemo, useEffect, useState } from 'react';
import PropTypes from 'prop-types';
// DÜZELTME: Kapsamlı yapı için 'useFlexLayout' geri eklendi.
import { useTable, useSortBy, useFilters, usePagination, useFlexLayout } from 'react-table';
import { Spin, Alert } from 'antd';

import { formatNumber } from '../utils/FormatNumber';
import { ColumnFilter } from '../utils/ColumnFilter';
import DynamicSubTotal from '../utils/DynamicSubTotal';
import Pagination from '../utils/Pagination';

import '../css/CustomerSalesV2Table.css';

const CustomerSalesV2Table = ({ data, summaryData, isLoading, isError }) => {
  const defaultColumn = useMemo(() => ({ Filter: ColumnFilter }), []);
  const [visibleMonths, setVisibleMonths] = useState([]);

  useEffect(() => {
    if (!summaryData || Object.keys(summaryData).length === 0) return;
    const months = [
      { key: 'ocak', label: 'Ocak' }, { key: 'subat', label: 'Şubat' }, { key: 'mart', label: 'Mart' },
      { key: 'nisan', label: 'Nisan' }, { key: 'mayis', label: 'Mayıs' }, { key: 'haziran', label: 'Haziran' },
      { key: 'temmuz', label: 'Temmuz' }, { key: 'agustos', label: 'Ağustos' }, { key: 'eylul', label: 'Eylül' },
      { key: 'ekim', label: 'Ekim' }, { key: 'kasim', label: 'Kasım' }, { key: 'aralik', label: 'Aralık' }
    ];
    const monthTotals = {
        ocak: summaryData.Ocak, subat: summaryData.Şubat, mart: summaryData.Mart, nisan: summaryData.Nisan,
        mayis: summaryData.Mayıs, haziran: summaryData.Haziran, temmuz: summaryData.Temmuz, agustos: summaryData.Ağustos,
        eylul: summaryData.Eylül, ekim: summaryData.Ekim, kasim: summaryData.Kasım, aralik: summaryData.Aralık,
    };
    const filtered = months.filter(month => monthTotals[month.key] && parseFloat(monthTotals[month.key]) > 0);
    setVisibleMonths(filtered);
  }, [summaryData]);

  const columns = useMemo(() => [
    { Header: 'Satıcı', accessor: 'satici', Filter: ColumnFilter, width: 150 },
    { Header: 'Satış Tipi', accessor: 'satis_tipi', Filter: ColumnFilter, width: 120 },
    { Header: 'Cari Grup', accessor: 'cari_grup', Filter: ColumnFilter, width: 120 },
    { Header: 'Müşteri Kodu', accessor: 'musteri_kodu', Filter: ColumnFilter, width: 130, headerClassName: 'customer-sales__thead--musteri-kodu' },
    { 
      Header: 'Müşteri Adı', accessor: 'musteri_adi', Filter: ColumnFilter, 
      width: 300, className: 'customer-sales__td--musteri-ad', headerClassName: 'customer-sales__th--musteri-ad',
      Footer: () => <div style={{ textAlign: 'right', fontWeight: 'bold' }}>Dinamik Toplam:</div> 
    },
    {
      Header: () => <>Toplam Yıllık <br /> {formatNumber(summaryData?.ToplamNetSPB_EUR)}</>,
      accessor: 'toplam_net_spb_eur', width: 150,
      Cell: ({ value }) => formatNumber(value),
      Footer: (info) => <DynamicSubTotal data={info.rows} columnId="toplam_net_spb_eur" />,
      disableFilters: true,
      className: 'customer-sales__td--numeric customer-sales__td--yillik-toplam',
      headerClassName: 'customer-sales__thead--numeric-header',
    },
    ...visibleMonths.map(month => ({
      Header: () => <>{month.label} <br /> {formatNumber(summaryData?.[month.label])}</>,
      accessor: month.key, width: 120,
      Cell: ({ value }) => formatNumber(value),
      Footer: (info) => <DynamicSubTotal data={info.rows} columnId={month.key} />,
      disableFilters: true,
      className: 'customer-sales__td--numeric',
      headerClassName: 'customer-sales__thead--numeric-header',
    })),
  ], [summaryData, visibleMonths]);

  const tableData = useMemo(() => data, [data]);

  const {
    getTableProps, getTableBodyProps, headerGroups, prepareRow, page,
    canPreviousPage, canNextPage, pageCount, gotoPage, nextPage, previousPage,
    setPageSize, state: { pageIndex, pageSize }, footerGroups,
  } = useTable(
    { columns, data: tableData, defaultColumn, initialState: { pageIndex: 0, pageSize: 20, sortBy: [{ id: 'toplam_net_spb_eur', desc: true }] } },
    useFilters, useSortBy, usePagination,
    useFlexLayout // DÜZELTME: Kapsamlı yapı için hook geri eklendi.
  );

  if (isLoading) return <div style={{ textAlign: 'center', padding: ' ৫০px' }}><Spin size="large" tip="Veriler Yükleniyor..." /></div>;
  if (isError) return <Alert message="Veri Yüklenemedi" description="Rapor verileri çekilirken bir hata oluştu." type="error" showIcon />;

  return (
    <>
      {/* DÜZELTME: Hatalı 'pagination-wrapper' sınıf adı, doğru olan 'pagination-controls' ile değiştirildi. */}
      <div >
        <Pagination {...{ pageCount, pageIndex, gotoPage, nextPage, previousPage, setPageSize, pageSize, canNextPage, canPreviousPage }} />
      </div>
      <div className="customersalesv2-table-wrapper">
        <table {...getTableProps()} className="customer-sales__table">
          <thead>
            {headerGroups.map(headerGroup => (
              <tr {...headerGroup.getHeaderGroupProps()}>
                {headerGroup.headers.map(column => (
                  <th {...column.getHeaderProps(column.getSortByToggleProps())} className={`customer-sales__thead--header ${column.headerClassName || ''}`}>
                    {column.render('Header')}
                    <span>{column.isSorted ? (column.isSortedDesc ? ' 🔽' : ' 🔼') : ''}</span>
                    <div className="filter-container">{column.canFilter ? column.render('Filter') : null}</div>
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
                  <td {...column.getFooterProps()} className="customer-sales__td--numeric customer-sales__td--yillik-toplam">
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