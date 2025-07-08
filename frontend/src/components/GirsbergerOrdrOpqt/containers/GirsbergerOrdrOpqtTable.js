// frontend/src/components/GirsbergerOrdrOpqt/containers/GirsbergerOrdrOpqtTable.js
import React, { useMemo } from 'react';
import { useTable, useSortBy, useFilters, usePagination } from 'react-table';
import useGirsbergerOrdrOpqt from '../hooks/useGirsbergerOrdrOpqt'; 
import ColumnFilter from '../utils/ColumnFilter';
import Pagination from '../utils/Pagination';
import '../css/GirsbergerOrdrOpqtTable.css';

const GirsbergerOrdrOpqtTable = () => {
  const { data, loading, error } = useGirsbergerOrdrOpqt();

  const defaultColumn = useMemo(() => ({
    Filter: ColumnFilter,
  }), []);

  const columns = useMemo(() => [
    { Header: 'BelgeNo', accessor: 'belge_no', Filter: ColumnFilter },
    { Header: 'KaynakDetayNo', accessor: 'salma_teklif_kaynak_detay_no', Filter: ColumnFilter ,  },
    { Header: 'Satıcı', accessor: 'satici', Filter: ColumnFilter },
    { Header: 'BelgeTarih', accessor: 'belge_tarih', Filter: ColumnFilter },
    { Header: 'TeslimTarih', accessor: 'teslim_tarih', Filter: ColumnFilter },
    //{ Header: 'MüşteriKod', accessor: 'musteri_kod', Filter: ColumnFilter },
    { Header: 'MüşteriAd', accessor: 'musteri_ad', Filter: ColumnFilter },
    { Header: 'SatışTipi', accessor: 'satis_tipi', Filter: ColumnFilter },
    { Header: 'SatırStatus', accessor: 'satir_status', Filter: ColumnFilter },
    { Header: 'KalemKod', accessor: 'kalem_kod', Filter: ColumnFilter },
    { Header: 'Salma Teklif Kalem No', accessor: 'salma_teklif_kalem_no', Filter: ColumnFilter ,  },
    { Header: 'KalemTanımı', accessor: 'kalem_tanimi', Filter: ColumnFilter },
    //{ Header: 'Salma Teklif Tedarikçi Kod', accessor: 'salma_teklif_tedarikci_kod', Filter: ColumnFilter ,  },
    { Header: 'Salma Teklif No', accessor: 'salma_teklif_no', Filter: ColumnFilter ,  },
    { Header: 'Salma Teklif Tedarikçi Ad', accessor: 'salma_teklif_tedarikci_ad', Filter: ColumnFilter   },
    { Header: 'SipMiktar', accessor: 'sip_miktar', disableFilters: true,  },
    { Header: 'Salma Teklif Miktar', accessor: 'salma_teklif_miktar', disableFilters: true, },


  ], []);

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    prepareRow,
    page,
    canPreviousPage,
    canNextPage,
    nextPage,
    previousPage,
    gotoPage,
    pageCount,
    setPageSize,
    state: { pageIndex, pageSize },
  } = useTable(
    {
      columns,
      data,
      defaultColumn,
      initialState: { pageIndex: 0, pageSize: 10,
        sortBy: [
          {
            id: 'salma_teklif_kaynak_detay_no', 
            asc: true, 
          },
        ],
       },
    },
    useFilters,
    useSortBy,
    usePagination
  );
  
  if (loading) return <div className="loading-message">Yükleniyor...</div>;
  if (error) return <div className="error-message">Hata: {error.message}</div>;

  return (
    <>
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
      </div>

      <table {...getTableProps()} className="girsberger-ordr-opqt__table">
        <thead className="girsberger-ordr-opqt__thead--header">
          {headerGroups.map(headerGroup => (
            <tr {...headerGroup.getHeaderGroupProps()} className="girsberger-ordr-opqt__row">
              {headerGroup.headers.map(column => (
                <th {...column.getHeaderProps()} className="girsberger-ordr-opqt__cell">
                  <div className="girsberger-ordr-opqt__header-content">
                    <span {...(column.canSort ? column.getSortByToggleProps() : {})}>
                      {column.render('Header')}
                    </span>
                    {column.isSorted ? (column.isSortedDesc ? ' ↓' : ' ↑') : ''}
                  </div>
                  {column.canFilter ? <div className="girsberger-ordr-opqt__filter-container">{column.render('Filter')}</div> : null}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody {...getTableBodyProps()} className="girsberger-ordr-opqt__body">
          {page.map(row => {
            prepareRow(row);
            return (
              <tr {...row.getRowProps()} className="girsberger-ordr-opqt__row">
                {row.cells.map(cell => (
                  <td {...cell.getCellProps()} className="girsberger-ordr-opqt__cell">
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

export default GirsbergerOrdrOpqtTable;
