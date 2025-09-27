// frontend/src/components/Activities/containers/ActivitiesTable.js
import React, { useMemo, useEffect } from 'react';
import { useTable, useSortBy, useFilters, usePagination } from 'react-table';
import useActivities from '../hooks/useActivities';
import Pagination from '../utils/Pagination';
import exportToXLSX from '../utils/XLSXExport';
import { formatDate, formatDateTime } from '../utils/DateFormat';
import ColumnFilter from '../utils/ColumnFilter';
import '../css/ActivitiesTable.css';

const ActivitiesTable = () => {
  /* ------------------------------------------------------------------ */
  /* 1. Veri çek                                                         */
  /* ------------------------------------------------------------------ */
  const {
    localActivities,
    loading,
    error,
    fetchLocalActivities,
  } = useActivities();

  useEffect(() => {
    fetchLocalActivities();
  }, [fetchLocalActivities]);

  const data = useMemo(() => localActivities, [localActivities]);

  /* ------------------------------------------------------------------ */
  /* 2. Özel filterTypes (Tarih filtre desteği)                          */
  /* ------------------------------------------------------------------ */
  const filterTypes = useMemo(
  () => ({
    /* DD.MM.YYYY üzerine text-search */
    dateText: (rows, id, value) => {
      if (!value) return rows;
      const s = value.toLowerCase();
      return rows.filter(r =>
        formatDate(r.values[id]).toLowerCase().includes(s)
      );
    },

    /* DD.MM.YYYY HH:MM üzerine text-search */
    dateTimeText: (rows, id, value) => {
      if (!value) return rows;
      const s = value.toLowerCase();
      return rows.filter(r =>
        formatDateTime(r.values[id]).toLowerCase().includes(s)
      );
    },
  }),
  []
);


  /* ------------------------------------------------------------------ */
  /* 3. Kolon tanımları                                                  */
  /* ------------------------------------------------------------------ */
  const columns = useMemo(
    () => [
      { Header: 'Numara', accessor: 'numara' },

      {
        Header: 'Tarih',
        accessor: 'baslangic_tarihi',
        Cell: ({ value }) => <span>{formatDate(value)}</span>,
        sortType: (a, b) =>
          new Date(a.values.baslangic_tarihi) -
          new Date(b.values.baslangic_tarihi),
        filter: 'dateText', // özel filtre
      },

      { Header: 'İşleyen', accessor: 'isleyen' },

      {
        Header: 'Açıklama - İçerik',
        id: 'aciklama_icerik',
        accessor: row => `${row.aciklama} - ${row.icerik}`,
      },

      {
        Header: 'Kaydedildi',
        accessor: 'create_datetime',
        Cell: ({ value }) => <span>{formatDateTime(value)}</span>,
        sortType: (a, b) =>
          new Date(a.values.create_datetime) - new Date(b.values.create_datetime),
        filter: 'dateTimeText',       // 👈  burada!
      },

    ],
    []
  );

  /* ------------------------------------------------------------------ */
  /* 4. Varsayılan kolon ayarları                                        */
  /* ------------------------------------------------------------------ */
  const defaultColumn = useMemo(
    () => ({
      Filter: ColumnFilter,
      disableSortBy: false,
    }),
    []
  );

  /* ------------------------------------------------------------------ */
  /* 5. react-table hook’ları                                            */
  /* ------------------------------------------------------------------ */
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
      filterTypes,
      initialState: {
        pageIndex: 0,
        pageSize: 100,
        sortBy: [{ id: 'baslangic_tarihi', desc: true }],
      },
    },
    useFilters,
    useSortBy,
    usePagination
  );

  /* ------------------------------------------------------------------ */
  /* 6. Yardımcı fonksiyonlar                                            */
  /* ------------------------------------------------------------------ */
  const handleExportToXLSX = () => {
    const selectedData = page.map(row => row.original);
    exportToXLSX(selectedData, 'activities.xlsx');
  };

  /* ------------------------------------------------------------------ */
  /* 7. Render                                                           */
  /* ------------------------------------------------------------------ */
  if (loading) return <p>Loading...</p>;
  if (error)   return <p>Error loading activities: {error.message}</p>;

  return (
    <>
      <div className="fetch-buttons">
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
        <button onClick={handleExportToXLSX} className="export-button">
          Export XLSX
        </button>
      </div>

      <table {...getTableProps()} className="activities-table">
        <thead>
          {headerGroups.map(hg => (
            <tr {...hg.getHeaderGroupProps()}>
              {hg.headers.map(col => (
                <th
                  {...col.getHeaderProps(col.getSortByToggleProps())}
                  className={
                    col.isSorted
                      ? col.isSortedDesc
                        ? 'sorted-desc'
                        : 'sorted-asc'
                      : ''
                  }
                >
                  {col.render('Header')}
                  {col.isSorted ? (col.isSortedDesc ? ' 🔽' : ' 🔼') : ''}
                  <div>{col.canFilter ? col.render('Filter') : null}</div>
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
                  <td {...cell.getCellProps()}>{cell.render('Cell')}</td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </>
  );
};

export default ActivitiesTable;
