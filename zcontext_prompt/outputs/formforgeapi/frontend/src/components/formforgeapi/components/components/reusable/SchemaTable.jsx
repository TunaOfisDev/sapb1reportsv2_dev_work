// path: frontend/src/components/formforgeapi/components/components/reusable/SchemaTable.jsx
import React from 'react';
import { useTable, useSortBy } from 'react-table';
import { Link } from 'react-router-dom';
import styles from '../../../css/FormForgeAPI.module.css';

const SchemaTable = ({ schemas, loading, deleteSchema }) => {
    const data = React.useMemo(() => schemas, [schemas]);
    const columns = React.useMemo(() => [
        { Header: 'Form Başlığı', accessor: 'title' },
        { Header: 'Departman', accessor: 'department_name' },
        { Header: 'Oluşturan', accessor: 'created_by.username' },
        {
            Header: 'İşlemler',
            accessor: 'id',
            Cell: ({ row }) => (
                <div className={styles.actions}>
                    <Link to={`/formforgeapi/fill/${row.original.id}`}>Formu Doldur</Link>
                    <Link to={`/formforgeapi/data/${row.original.id}`}>Verileri Gör</Link>
                    <Link to={`/formforgeapi/edit/${row.original.id}`}>Düzenle</Link>
                    <button onClick={() => deleteSchema(row.original.id)} className={styles.deleteButtonSmall}>Sil</button>
                </div>
            )
        }
    ], [deleteSchema]);

    const { getTableProps, getTableBodyProps, headerGroups, rows, prepareRow } = useTable({ columns, data }, useSortBy);
    if (loading) return <div className={styles.loading}>Yükleniyor...</div>;
    return (
        <table {...getTableProps()} className={styles.dataTable}>
            <thead>
                {headerGroups.map(hg => (
                    <tr {...hg.getHeaderGroupProps()}>
                        {hg.headers.map(col => (
                            <th {...col.getHeaderProps(col.getSortByToggleProps())}>
                                {col.render('Header')}
                                <span>{col.isSorted ? (col.isSortedDesc ? ' 🔽' : ' 🔼') : ''}</span>
                            </th>
                        ))}
                    </tr>
                ))}
            </thead>
            <tbody {...getTableBodyProps()}>
                {rows.map(row => {
                    prepareRow(row);
                    return (
                        <tr {...row.getRowProps()}>
                            {row.cells.map(cell => <td {...cell.getCellProps()}>{cell.render('Cell')}</td>)}
                        </tr>
                    );
                })}
            </tbody>
        </table>
    );
};
export default SchemaTable;

