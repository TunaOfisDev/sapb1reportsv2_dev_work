// frontend/src/components/orderarchive/containers/OrderArchiveTable.js
import React, { useMemo } from 'react';
import { useTable, useSortBy, usePagination } from 'react-table';
import { TABLE_COLUMNS } from '../utils/constants';
import '../css/OrderArchiveTable.css';

const OrderArchiveTable = ({
    data,
    loading,
    error,
    totalItems,
    totalPages,
    currentPage,
    pageSize,
    onPageChange,
}) => {
    // Kolon tanımlamalarını oluştur
    const columns = useMemo(() => TABLE_COLUMNS, []);

    // Sıralama tiplerini tanımlayın
    const sortTypes = useMemo(() => ({
        alphanumeric: (rowA, rowB, columnId) => {
            const valA = rowA.values[columnId] || '';
            const valB = rowB.values[columnId] || '';
            return valA.localeCompare(valB, undefined, { numeric: true, sensitivity: 'base' });
        },
        numeric: (rowA, rowB, columnId) => {
            const valA = parseFloat(rowA.values[columnId]) || 0;
            const valB = parseFloat(rowB.values[columnId]) || 0;
            return valA - valB;
        },
    }), []);

    // React Table hook'unu kullan
    const {
        getTableProps,
        getTableBodyProps,
        headerGroups,
        prepareRow,
        page,
    } = useTable(
        {
            columns,
            data: data || [],
            initialState: {
                pageIndex: currentPage - 1,
                pageSize: pageSize,
            },
            manualPagination: true,
            pageCount: totalPages,
            autoResetPage: false,
            sortTypes, // Özel sıralama tiplerini bağladık
        },
        useSortBy,
        usePagination,
    );

    if (!data.length && !loading && !error) {
        return (
            <div className="orderarchive-table__empty">
                Lütfen arama yapın veya yıl seçin.
            </div>
        );
    }

    if (loading) {
        return (
            <div className="orderarchive__loading">
                <div className="orderarchive__loading-spinner" />
            </div>
        );
    }

    if (error) {
        return <div className="orderarchive__error">{error}</div>;
    }

    return (
        <div className="orderarchive-table-container">
            {/* Sayfalama */}
            <div className="orderarchive-pagination__top">
                <div className="orderarchive-pagination__controls">
                    <button
                        onClick={() => onPageChange(currentPage - 1)}
                        disabled={currentPage === 1}
                        className="orderarchive-pagination__button"
                    >
                        {'<'}
                    </button>
                    <span className="orderarchive-pagination__text">
                        Sayfa {currentPage} / {totalPages}
                    </span>
                    <button
                        onClick={() => onPageChange(currentPage + 1)}
                        disabled={currentPage === totalPages}
                        className="orderarchive-pagination__button"
                    >
                        {'>'}
                    </button>
                </div>
                <div className="orderarchive-pagination__info">
                    Toplam {totalItems.toLocaleString()} kayıt
                </div>
            </div>

            {/* Tablo */}
            <div className="orderarchive-table__wrapper">
            <table {...getTableProps()} className="orderarchive-table">
                <thead>
                    {headerGroups.map(headerGroup => (
                        <tr {...headerGroup.getHeaderGroupProps()}>
                            {headerGroup.headers.map(column => (
                                <th
                                    {...column.getHeaderProps(column.getSortByToggleProps())}
                                    className="orderarchive-table__header"
                                >
                                    <div className="orderarchive-table__header-content">
                                        {column.render('Header')}
                                        <span>
                                            {column.isSorted
                                                ? column.isSortedDesc
                                                    ? ' ↓'
                                                    : ' ↑'
                                                : ''}
                                        </span>
                                    </div>
                                </th>
                            ))}
                        </tr>
                    ))}
                </thead>
                <tbody {...getTableBodyProps()}>
                        {page.map((row) => {
                            prepareRow(row);
                            return (
                                <tr {...row.getRowProps()} className="orderarchive-table__row">
                                    {row.cells.map((cell) => (
                                        <td {...cell.getCellProps()} className="orderarchive-table__cell">
                                            {cell.render('Cell')}
                                        </td>
                                    ))}
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default React.memo(OrderArchiveTable);