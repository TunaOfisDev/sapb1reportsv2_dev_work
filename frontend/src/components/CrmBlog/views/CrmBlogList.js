// frontend/src/components/CrmBlog/views/CrmBlogList.js
import React, { useMemo, useEffect, useState } from 'react';
import { useTable, usePagination, useFilters, useSortBy } from 'react-table';
import useCrmBlog from '../hooks/useCrmBlog';
import ColumnFilter from '../utils/ColumnFilter';
import Pagination from '../utils/Pagination'; // Sayfalama bileşenini import ediyoruz
import '../css/CrmBlogList.css';
import authService from '../../../auth/authService'; // Auth service to get current user

const CrmBlogList = ({ onEdit, onNewTask }) => {
  const { posts, loading, error } = useCrmBlog();
  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    const fetchUser = async () => {
      const user = await authService.getCurrentUser();
      setCurrentUser(user);
    };
    fetchUser();
  }, []);

  const columns = useMemo(
    () => [
      {
        Header: 'Son Tarih',
        accessor: 'deadline',
        Filter: ColumnFilter,
      },
      {
        Header: 'Yazar',
        accessor: 'author_email',
        Cell: ({ value }) => value.split('@')[0], // Extract username from email
        Filter: ColumnFilter,
      },
      {
        Header: 'Başlık',
        accessor: 'task_and_project',
        Cell: ({ row }) => (
          <span>
            {row.original.task_title} - {row.original.project_name}
          </span>
        ),
        Filter: ColumnFilter,
      },
      {
        Header: 'Görev Açıklamaları',
        accessor: 'task_description',
        Filter: ColumnFilter,
      },
      {
        Header: 'Eylemler',
        accessor: 'actions',
        Cell: ({ row }) => (
          currentUser && row.original.author_email === currentUser.email && (
            <button
              className="crm-blog-list__button"
              onClick={() => onEdit(row.original.id)}
            >
              Düzenle
            </button>
          )
        ),
        disableFilters: true,
      },
    ],
    [onEdit, currentUser]
  );

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    page,
    prepareRow,
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
      data: posts,
      initialState: {
        pageIndex: 0,
        pageSize: 10,
        sortBy: [
          {
            id: 'deadline',
            desc: true,
          },
        ],
      },
    },
    useFilters,
    useSortBy,
    usePagination
  );

  if (loading) {
    return <div>Yükleniyor...</div>;
  }

  if (error) {
    return <div>Hata: {error.message}</div>;
  }

  return (
    <div className="crm-blog-list">
      
      <div className="crm-blog-list__header">
        <h2 className="crm-blog-list__title">Görev Listesi (Satış Harici Crm Aktiviteleri)</h2>
        <button className="crm-blog-list__new-task-button" onClick={onNewTask}>
          Yeni Görev Ekle
        </button>
      </div>
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
      <table {...getTableProps()} className="crm-blog-list__table">
        <thead>
          {headerGroups.map(headerGroup => (
            <tr {...headerGroup.getHeaderGroupProps()}>
              {headerGroup.headers.map(column => (
                <th {...column.getHeaderProps(column.getSortByToggleProps())} className="crm-blog-list__table-header">
                  <div className="header-content">
                    {column.render('Header')}
                    <span className="crm-blog-list__sort-icon">
                      {column.isSorted ? (column.isSortedDesc ? ' ↓' : ' ↑') : ''}
                    </span>
                  </div>
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
                  <td {...cell.getCellProps()}>{cell.render('Cell')}</td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
     
    </div>
  );
};

export default CrmBlogList;
