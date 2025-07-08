// frontend/src/components/OpenOrderDocSum/containers/OpenOrderDocSumTable.js
import React from 'react';
import { useTable, useSortBy, useFilters, usePagination } from 'react-table';
import Pagination from '../utils/Pagination';
import useOpenOrderDocSum from '../hooks/useOpenOrderDocSum';
import FormatNumber from '../utils/FormatNumber';
import formatDate from '../utils/DateFormat';
import DefaultColumnFilter from '../utils/ColumnFilter';
import DateColumnFilter from '../utils/DateColumnFilter';
import useUpperTotal from '../utils/UpperTotal';
import useDynamicSubtotals from '../utils/DynamicSubTotal';
import '../css/OpenOrderDocSumTable.css';
import '../css/ColumnFilter.css';


const OpenOrderDocSumTable = () => {
  const {
    documentSummaries, 
    loading,
    error,
  } = useOpenOrderDocSum();

const uppertotals = useUpperTotal(documentSummaries);

  const columns = React.useMemo(() => [
    { Header: 'Belge No', accessor: 'belge_no', Filter: DefaultColumnFilter, 
    Cell: ({ value }) => <span className="open-order-doc-sum__td--belge-no open-order-doc-sum__th--belge-no">{value}</span>,
    filterClassName: 'open-order-doc-sum__filter open-order-doc-sum__filter input ', 

    },
    {
      Header: 'Satıcı',
      accessor: 'satici',
      Cell: ({ value }) => <span className="open-order-doc-sum__td--satici open-order-doc-sum__th--satici">{value}</span>,
      Filter: DefaultColumnFilter,
      filterClassName: 'open-order-doc-sum__filter' // Bu sınıfı ekliyoruz
    },
    
    { Header: 'Belge Tarihi', accessor: 'belge_tarih', className: 'open-order-doc-sum__td--belge-tarih .open-order-doc-sum__th--belge-tarih', Cell: ({ value }) => formatDate(value) , Filter: DateColumnFilter },
    { Header: 'Teslim Tarihi', accessor: 'teslim_tarih', className: 'open-order-doc-sum__td--teslim-tarih .open-order-doc-sum__th--teslim-tarih', Cell: ({ value }) => formatDate(value), Filter: DateColumnFilter },
    { Header: 'Müşteri Kodu', accessor: 'musteri_kod', Filter: DefaultColumnFilter, className: 'open-order-doc-sum__td--muster-kod .open-order-doc-sum__th--musteri-kod' },
  
    {
      Header: 'Müşteri Adı',
      accessor: 'musteri_ad',
      Cell: ({ value }) => (
        <span className="open-order-doc-sum__td--musteri-ad">
          {value}
        </span>
      ),
      Filter: ({ column: { filterValue, setFilter } }) => (
        <input
          value={filterValue || ''}
          onChange={e => setFilter(e.target.value)}
          onClick={e => e.stopPropagation()}
          placeholder="Ara..."
          className="open-order-doc-sum__filter--musteri-ad"
        />
      )
    },
        
        
    { Header: 'Satış Tipi', accessor: 'satis_tipi', Filter: DefaultColumnFilter, filterClassName: 'open-order-doc-sum__filter open-order-doc-sum__filter input ',  },
    {
      Header: 'Iskonto', 
      accessor: 'belge_iskonto_oran', 
      Cell: ({ value }) => <FormatNumber value={value} className='open-order-doc-sum__td--numeric' />,
      disableFilters: true
    },
    // Finansal kolonlar için Header düzenlemesi
    {
      Header: () => (
        <div style={{ textAlign: 'right' }}>
          Açık Net
          <div>
            <FormatNumber value={uppertotals.acik_net_tutar_ypb} />
          </div>
        </div>
      ),
      accessor: 'acik_net_tutar_ypb',
      Cell: ({ value }) => <FormatNumber value={value} />,
      disableFilters: true
    },
    {
      Header: () => (
        <div style={{ textAlign: 'right' }}>
          Girsberger
          <div>
            <FormatNumber value={uppertotals.girsberger_net_tutar_ypb} />
          </div>
        </div>
      ),
      accessor: 'girsberger_net_tutar_ypb',
      Cell: ({ value }) => <FormatNumber value={value} />,
      disableFilters: true
    },
    {
      Header: () => (
        <div style={{ textAlign: 'right' }}>
          Mamul
          <div>
            <FormatNumber value={uppertotals.mamul_net_tutar_ypb} />
          </div>
        </div>
      ),
      accessor: 'mamul_net_tutar_ypb',
      Cell: ({ value }) => <FormatNumber value={value} />,
      disableFilters: true
    },
    {
      Header: () => (
        <div style={{ textAlign: 'right' }}>
          Ticari
          <div>
            <FormatNumber value={uppertotals.ticari_net_tutar_ypb} />
          </div>
        </div>
      ),
      accessor: 'ticari_net_tutar_ypb',
      Cell: ({ value }) => <FormatNumber value={value} />,
      disableFilters: true
    },
    {
      Header: () => (
        <div style={{ textAlign: 'right' }}>
          Nakliye
          <div>
            <FormatNumber value={uppertotals.nakliye_net_tutar_ypb} />
          </div>
        </div>
      ),
      accessor: 'nakliye_net_tutar_ypb',
      Cell: ({ value }) => <FormatNumber value={value} />,
      disableFilters: true
    },
    {
      Header: () => (
        <div style={{ textAlign: 'right' }}>
          Montaj
          <div>
            <FormatNumber value={uppertotals.montaj_net_tutar_ypb} />
          </div>
        </div>
      ),
      accessor: 'montaj_net_tutar_ypb',
      Cell: ({ value }) => <FormatNumber value={value} />,
      disableFilters: true
    },
  ], [uppertotals]);

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
      data: documentSummaries,
      initialState: {
        pageIndex: 0,
        sortBy: [
          {
            id: 'belge_tarih',
            desc: true
          }
        ]
      },
      defaultColumn: { Filter: DefaultColumnFilter }, 
    },
    useFilters,
    useSortBy,
    usePagination
  );

  // Dinamik alt toplamları hesaplayın
  const subtotals = useDynamicSubtotals(rows, 'musteri_kod', ['acik_net_tutar_ypb', 'girsberger_net_tutar_ypb','mamul_net_tutar_ypb', 'ticari_net_tutar_ypb', 'nakliye_net_tutar_ypb',  'montaj_net_tutar_ypb',]);


  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}</p>;

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
      <table {...getTableProps()} className="open-order-doc-sum__table table table-sm table-striped table-hover">
      <thead>
        {headerGroups.map(headerGroup => (
          <tr {...headerGroup.getHeaderGroupProps()} className="open-order-doc-sum__thead--header">
            {headerGroup.headers.map(column => (
              <th {...column.getHeaderProps(column.getSortByToggleProps())} className="text-left">
              {column.render('Header')}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                {column.canFilter ? column.render('Filter') : null}
                <span>
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
                <td {...cell.getCellProps()} className={cell.column.id.includes('net_tutar_ypb') ? 'open-order-doc-sum__td--numeric' : ''}>
                  {cell.render('Cell')}
                </td>
              ))}
            </tr>
          );
        })}
      </tbody>
        {/* Dinamik alt toplam satırını ekleyin */}
        <tfoot>
          <tr>
            <td className="footer-cell" colSpan="8">Dinamik Alt Toplamlar</td>
            <td className="footer-cell"><FormatNumber value={subtotals.acik_net_tutar_ypb}/></td>
            <td className="footer-cell"><FormatNumber value={subtotals.girsberger_net_tutar_ypb}/></td>
            <td className="footer-cell"><FormatNumber value={subtotals.mamul_net_tutar_ypb}/></td>
            <td className="footer-cell"><FormatNumber value={subtotals.ticari_net_tutar_ypb}/></td>
            <td className="footer-cell"><FormatNumber value={subtotals.nakliye_net_tutar_ypb}/></td>
            <td className="footer-cell"><FormatNumber value={subtotals.montaj_net_tutar_ypb}/></td>
          </tr>
        </tfoot>
    </table>

    </div>
  );
};

export default OpenOrderDocSumTable;
