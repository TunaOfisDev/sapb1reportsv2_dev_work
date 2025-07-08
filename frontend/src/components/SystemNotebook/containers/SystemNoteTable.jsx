
// frontend/src/components/SystemNotebook/containers/SystemNoteTable.jsx

import React, { useState, useMemo } from 'react';
import { useTable, usePagination, useSortBy, useFilters } from 'react-table';
import SystemNoteFilterPanel from './SystemNoteFilterPanel';
import SystemNoteShowModal from './SystemNoteShowModal';
import useSystemNotes from '../hooks/useSystemNotes';
import { formatDateTime, formatSourceLabel, truncateContent } from '../utils/formatSystemNote';
import '../css/systemnotebook-table.css';

const SystemNoteTable = () => {
  const {
    notes,
    loading,
    error,
    applyFilters,
    syncFromGithub,
    createNote,
    updateNote,
    removeNote
  } = useSystemNotes();

  const [selectedNote, setSelectedNote] = useState(null);
  const [isNewNote, setIsNewNote] = useState(false);

  const openNewNoteModal = () => {
    setSelectedNote({ title: '', content: '', source: 'admin' });
    setIsNewNote(true);
  };

  const openExistingNote = (note) => {
    setSelectedNote(note);
    setIsNewNote(false);
  };

  const closeModal = () => {
    setSelectedNote(null);
    setIsNewNote(false);
  };

  const handleSave = async (payload, id) => {
    if (id) {
      await updateNote(id, payload);
    } else {
      await createNote(payload);
    }
    closeModal();
  };

  const handleDelete = async (id) => {
    await removeNote(id);
    closeModal();
  };

  const data = useMemo(() => notes || [], [notes]);

  const columns = useMemo(() => [
    {
      Header: 'Başlık',
      accessor: 'title',
      Cell: ({ row }) => (
        <div
          className="systemnotebook-list__table-title"
          onClick={() => openExistingNote(row.original)}
        >
          {row.original.title}
        </div>
      )
    },
    {
      Header: 'Kaynak',
      accessor: 'source',
      Cell: ({ value }) => formatSourceLabel(value)
    },
    {
      Header: 'Tarih',
      accessor: 'created_at',
      Cell: ({ value }) => formatDateTime(value)
    },
    {
      Header: 'İçerik',
      accessor: 'content',
      Cell: ({ value }) => truncateContent(value, 100)
    }
  ], []);

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    prepareRow,
    page,
    nextPage,
    previousPage,
    canNextPage,
    canPreviousPage,
    pageOptions,
    state: { pageIndex }
  } = useTable(
    { columns, data, initialState: { pageSize: 10 } },
    useFilters,
    useSortBy,
    usePagination
  );

  return (
    <div className="systemnotebook-list">
      <div className="systemnotebook-list__topbar">
        <h2 className="systemnotebook-list__title">Sistem Notları</h2>
        <div className="systemnotebook-list__actions--right">
          <button className="systemnotebook-filter-panel__button" onClick={openNewNoteModal}>
            + Yeni Not Ekle
          </button>
          <button className="systemnotebook-filter-panel__button" onClick={syncFromGithub}>
            GitHub dan Senkronize Et
          </button>
        </div>
      </div>

      <SystemNoteFilterPanel onFilter={applyFilters} />

      {loading && <p>Yükleniyor...</p>}
      {error && <p>Hata: {error.message}</p>}

      <table {...getTableProps()} className="systemnotebook-table">
  <thead className="systemnotebook-table__head">
    {headerGroups.map(headerGroup => (
      <tr
        {...headerGroup.getHeaderGroupProps()}
        className="systemnotebook-table__row"
      >
        {headerGroup.headers.map(column => (
          <th
            {...column.getHeaderProps(column.getSortByToggleProps())}
            className="systemnotebook-table__cell systemnotebook-table__cell--header"
          >
            {column.render('Header')}
            {column.isSorted ? (column.isSortedDesc ? ' ↓' : ' ↑') : ''}
          </th>
        ))}
      </tr>
    ))}
  </thead>

  <tbody className="systemnotebook-table__body" {...getTableBodyProps()}>
    {page.map(row => {
      prepareRow(row);
      return (
        <tr {...row.getRowProps()} className="systemnotebook-table__row">
          {row.cells.map(cell => (
            <td {...cell.getCellProps()} className="systemnotebook-table__cell">
              {cell.render('Cell')}
            </td>
          ))}
        </tr>
      );
    })}
  </tbody>
</table>


<div className="systemnotebook-pagination">
  <button
    className="systemnotebook-pagination__button"
    onClick={() => previousPage()}
    disabled={!canPreviousPage}
  >
    Önceki
  </button>

  <span className="systemnotebook-pagination__info">
    Sayfa {pageIndex + 1} / {pageOptions.length}
  </span>

  <button
    className="systemnotebook-pagination__button"
    onClick={() => nextPage()}
    disabled={!canNextPage}
  >
    Sonraki
  </button>
</div>


      {selectedNote && (
        <SystemNoteShowModal
          visible={!!selectedNote}
          note={selectedNote}
          isNew={isNewNote}
          onClose={closeModal}
          onSave={handleSave}
          onDelete={handleDelete}
        />
      )}
    </div>
  );
};

export default SystemNoteTable;