// path: frontend/src/components/formforgeapi/components/components/reusable/DataTable.jsx
import React from 'react';
import { useTable, useSortBy } from 'react-table';
import styles from '../../../css/FormForgeAPI.module.css';

const DataTable = ({ columns, data, loading }) => {
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
export default DataTable;

