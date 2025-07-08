// File: frontend/src/components/ProcureCompare/components/ProcureCompareTable.jsx

import React, { useMemo, forwardRef, useImperativeHandle, useState } from 'react';
import { useTable, useSortBy, useFilters, usePagination } from 'react-table';
import formatNumber from '../utils/FormatNumber';
import { formatDate } from '../utils/DateTimeFormat';
import ColumnFilter from '../utils/ColumnFilter';
import DateFilter, { dateIncludesFilterFn } from '../utils/DateFilter';
import TeklifFiyatlariCell from './TeklifFiyatlariCell';
import ApprovalButtons from './ApprovalButtons';
import GroupedApprovalHistory from './GroupedApprovalHistory';
import Pagination from '../utils/Pagination'; 
import { useAccordionTable } from '../utils/AccordionTableHelper'; 
import ItemPurchaseHistoryModal from '../utils/ItemPurchaseHistoryModal';
import styles from '../css/ProcureCompare.module.css';

//  forwardRef ile tanım
const ProcureCompareTable = forwardRef(({ data }, ref) => {
  const defaultColumn = useMemo(() => ({
    Filter: ColumnFilter
  }), []);

  const [accordionExpanded, setAccordionExpanded] = useState(false); // BUTON MODU

  const {
    handleRowClick,
    handleExpandAll,
    handleCollapseAll,
    isRowExpanded,
  } = useAccordionTable();

  const [selectedItem, setSelectedItem] = useState({ code: '', name: '' });
  const [isModalOpen, setIsModalOpen] = useState(false);


  const columns = useMemo(() => [
    {
      Header: 'Belge Tarih',
      accessor: 'belge_tarih',
      Filter: DateFilter,
      filter: dateIncludesFilterFn,
      Cell: ({ value }) => (
        <div className={styles['procure-compare__td--belge-tarih']}>
          {formatDate(value)}
        </div>
      )
    },
    {
      Header: 'Belge No',
      accessor: 'belge_no',
      Filter: ({ column }) => (
        <input
          className={`${styles['column-filter__input']} ${styles['procure-compare__filter--belge-no']}`}
          value={column.filterValue || ''}
          onClick={(e) => e.stopPropagation()} 
          onChange={e => column.setFilter(e.target.value)}
          placeholder="Filtrele..."
        />
      ),
      Cell: ({ value }) => (
        <div className={styles['procure-compare__col--belge-no']} title={value}>
          {value}
        </div>
      ),
      className: styles['procure-compare__col--belge-no']
    },
    {
      Header: 'Kalem Tanimi',
      accessor: 'kalem_tanimi',
      Filter: ColumnFilter,
      Cell: ({ row }) => {
        const value = row.original.kalem_tanimi;
        const itemCode = row.original.kalem_kod;
      
        return (
          <div
            className={styles['procure-compare__col--kalem-tanimi']}
            title={value}
            style={{ cursor: 'pointer' }}
            onClick={(e) => {
              e.stopPropagation();
              setSelectedItem({ code: itemCode, name: value });
              setIsModalOpen(true);
            }}
          >
            <span style={{ marginRight: 6, color: '#b8860b', fontSize: '1.2em' }}>➤</span>
            <span className={styles['procure-compare__kalem-tanimi-text']}>
              {value}
            </span>
          </div>
        );
      }
      
      
    },
    {
      Header: 'Tedarikçi',
      accessor: 'tedarikci_ad',
      Filter: ColumnFilter,
      Cell: ({ value }) => (
        <div title={value}>
          {value}
        </div>
      ),
      className: styles['procure-compare__col--tedarikci-ad']
    },
    {
      Header: 'Miktar',
      accessor: 'sip_miktar',
      Filter: ColumnFilter,
      Cell: ({ value }) => (
        <div className={styles['procure-compare__col--sip-miktar']}>
          {formatNumber(value)}
        </div>
      )
    },
    {
      Header: 'Net Fiyat',
      accessor: 'net_fiyat_dpb',
      Filter: ColumnFilter,
      Cell: ({ row }) => {
        const value = row.original.net_fiyat_dpb;
        const currency = row.original.detay_doviz;
        return (
          <div className={styles['procure-compare__td--numeric']}>
            {formatNumber(value, 3)} <span style={{ fontSize: '0.85em' }}>{currency}</span>
          </div>
        );
      }
    },
    
    
    {
      Header: 'Net Tutar (YPB)',
      accessor: 'net_tutar_ypb',
      Filter: ColumnFilter,
      Cell: ({ value }) => (
        <div className={styles['procure-compare__td--numeric']}>
          {formatNumber(value)}
        </div>
      )
    },
   
    {
      Header: 'Teklif Fiyatları',
      accessor: 'teklif_fiyatlari_list',
      disableFilters: true,
      Cell: ({ row }) => (
        <div className={styles['procure-compare__col--teklif-fiyatlari']}>
          <TeklifFiyatlariCell row={row} />
        </div>
      ),
      sortType: (rowA, rowB, columnId) => {
        const listA = rowA.values[columnId];
        const listB = rowB.values[columnId];
    
        const getMinLocal = (list) => {
          if (!Array.isArray(list) || list.length === 0) return Number.POSITIVE_INFINITY;
          return Math.min(...list.map(entry => entry?.local_price ?? Number.POSITIVE_INFINITY));
        };
    
        const minA = getMinLocal(listA);
        const minB = getMinLocal(listB);
    
        return minA === minB ? 0 : minA > minB ? 1 : -1;
      }
    }
    
    ,

    {
      Header: 'İşlem',
      accessor: 'actions',
      disableSortBy: true,
      disableFilters: true,
      Cell: ({ row }) => (
        <div className={styles['procure-compare__col--actions']}>
          <ApprovalButtons comparisonItem={row.original} />
        </div>
      )
    
    },
    {
      Header: 'Onay Geçmişi',
      accessor: 'approval_history',
      disableSortBy: true,
      disableFilters: true,
      Cell: ({ row }) => (
        <div className={styles['procure-compare__col--approval-history']}>
          <GroupedApprovalHistory
            belgeNo={row.original.belge_no}
            uniqDetailNo={row.original.uniq_detail_no}
          />
        </div>
      )
    }
    
       
    
  ], []);

  const tableInstance = useTable(
    {
      columns,
      data,
      defaultColumn,
      initialState: {
        pageSize: 100,
        sortBy: [
          {
            id: 'belge_tarih',
            desc: true // büyükten küçüğe!
          }
        ]
      }
    },
    useFilters,
    useSortBy,
    usePagination
  );
  
  
  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    page,
    prepareRow,
    canNextPage,
    canPreviousPage,
    pageCount,
  
    gotoPage,
    nextPage,
    previousPage,
    setPageSize,
    state: { pageIndex, pageSize } // ← BURAYA DİKKAT!
  } = tableInstance;
  
  
  useImperativeHandle(ref, () => ({
    getFilteredRows: () => page.map(r => r.original) 
  }));
  
  

  return (
    <div className={styles['procure-compare__table-wrapper']}>
      {/* Pagination ve Butonlar */}
      <div className={styles['procure-compare__pagination-container']}>
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
  
  <div className={styles['procure-compare__accordion-buttons']}>
  <button
  onClick={() => {
    if (accordionExpanded) {
      handleCollapseAll();
    } else {
      handleExpandAll(page); // <<< page'i gönderiyoruz!
    }
    setAccordionExpanded(!accordionExpanded);
  }}

    className={`${styles['procure-compare__accordion-button']} ${accordionExpanded ? styles['procure-compare__accordion-button-expanded'] : ''}`}
  >
    <span className={styles['procure-compare__accordion-button-icon']}>
      {accordionExpanded ? '↑' : '↓'}
    </span>
    {accordionExpanded ? 'Tümünü Daralt' : 'Tümünü Genişlet'}
  </button>
</div>


      </div>
  
      {/* Scrollable Table */}
      <div className={styles['procure-compare__scroll-container']}>
        <table {...getTableProps()} className={styles['procure-compare__table']}>
          <thead className={styles['procure-compare__thead']}>
            {headerGroups.map(headerGroup => (
              <tr {...headerGroup.getHeaderGroupProps()} key={headerGroup.id}>
                {headerGroup.headers.map(column => (
                  <th
                    {...column.getHeaderProps(column.getSortByToggleProps())}
                    key={column.id}
                    className={
                      column.id === 'belge_tarih'
                        ? styles['procure-compare__col--belge-tarih']
                        : column.id === 'belge_no'
                        ? styles['procure-compare__col--belge-no']
                        : column.id === 'kalem_tanimi'
                        ? styles['procure-compare__col--kalem-tanimi']
                        : column.id === 'detay_doviz'
                        ? styles['procure-compare__col--doviz']
                        : column.id === 'sip_miktar'
                        ? styles['procure-compare__col--sip-miktar']
                        : column.id === 'net_fiyat_dpb'
                        ? styles['procure-compare__col--net-fiyat']
                        : column.id === 'net_tutar_ypb'
                        ? styles['procure-compare__col--net-fiyat']
                        : column.id === 'tedarikci_ad'
                        ? styles['procure-compare__col--tedarikci-ad']
                        : column.id === 'teklif_fiyatlari_list'
                        ? styles['procure-compare__col--teklif-fiyatlari']
                        : ''
                    }
                  >
                    <div className={styles['procure-compare__header-content']}>
                      <span>{column.render('Header')}</span>
                      <span className={styles['procure-compare__sort-icon']}>
                        {column.isSorted ? (column.isSortedDesc ? '↓' : '↑') : ''}
                      </span>
                    </div>
                    <div style={{ marginTop: '4px' }}>
                      {column.canFilter ? column.render('Filter') : null}
                    </div>
                  </th>
                ))}
              </tr>
            ))}
          </thead>
  
          <tbody {...getTableBodyProps()}>
  {page.length === 0 ? (
    <tr>
      <td colSpan={columns.length} style={{ textAlign: 'center', padding: '1rem' }}>
        Gösterilecek veri bulunamadı.
      </td>
    </tr>
  ) : (
    page.map(row => {
      prepareRow(row);
      return (
        <tr
          {...row.getRowProps()}
          key={row.original.uniq_detail_no || row.index}
          onClick={() => handleRowClick(row.original.uniq_detail_no)}
          className={isRowExpanded(row.original.uniq_detail_no) ? styles['procure-compare__expanded-row'] : styles['procure-compare__collapsed-row']}
        >
          {row.cells.map(cell => {
            const isAccordionField = ['teklif_fiyatlari_list', 'actions', 'approval_history'].includes(cell.column.id);

            return (
              <td
                key={cell.column.id}
                {...cell.getCellProps()}
                className={
                  cell.column.id === 'belge_tarih'
                    ? styles['procure-compare__col--belge-tarih']
                    : cell.column.id === 'belge_no'
                    ? styles['procure-compare__col--belge-no']
                    : cell.column.id === 'kalem_tanimi'
                    ? styles['procure-compare__col--kalem-tanimi']
                    : cell.column.id === 'detay_doviz'
                    ? styles['procure-compare__col--doviz']
                    : cell.column.id === 'sip_miktar'
                    ? styles['procure-compare__col--sip-miktar']
                    : cell.column.id === 'net_fiyat_dpb'
                    ? styles['procure-compare__col--net-fiyat']
                    : cell.column.id === 'net_tutar_ypb'
                    ? styles['procure-compare__col--net-fiyat']
                    : cell.column.id === 'tedarikci_ad'
                    ? styles['procure-compare__col--tedarikci-ad']
                    : cell.column.id === 'teklif_fiyatlari_list'
                    ? styles['procure-compare__col--teklif-fiyatlari']
                    : ''
                }
              >
                {isAccordionField ? (
                  <div className={isRowExpanded(row.original.uniq_detail_no) ? styles['row-wrapper-expanded'] : styles['row-wrapper-collapsed']}>
                    {cell.render('Cell')}
                  </div>
                ) : (
                  cell.render('Cell')
                )}
              </td>
            );
          })}
        </tr>
      );
    })
  )}
</tbody>

        </table>
      </div>

              <ItemPurchaseHistoryModal
          visible={isModalOpen}
          onClose={() => {
            setIsModalOpen(false);
            setSelectedItem({ code: '', name: '' });
          }}
          itemCode={selectedItem.code}
          itemName={selectedItem.name}
        />


    </div>
  );
  
});


export default ProcureCompareTable;
