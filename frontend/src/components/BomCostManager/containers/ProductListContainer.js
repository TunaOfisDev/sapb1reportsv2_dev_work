// frontend/src/components/BomCostManager/containers/ProductListContainer.js

import React, { useMemo } from 'react';
import { useTable, usePagination } from 'react-table';
import { useNavigate } from 'react-router-dom';
import useProductSelection from '../hooks/useProductSelection';
import Pagination from '../utils/pagination';
import '../css/ProductListContainer.css';

const ProductListContainer = ({ onSelectProduct }) => {
    const navigate = useNavigate();
    const { products, loading, error } = useProductSelection();

    const columns = useMemo(
        () => [
            {
                Header: 'Ürün Kodu',
                accessor: 'item_code',
                Cell: ({ row }) => (
                    <button
                        className="product-list-container__item-code"
                        onClick={() => {
                            console.log("Seçilen Ürün Kodu:", row.original.item_code);
                            navigate(`/bomcost/table/${row.original.item_code}`);
                            if (onSelectProduct) {
                                onSelectProduct(row.original);
                            }
                        }}
                    >
                        {row.original.item_code}
                    </button>
                ),
            },
            { Header: 'Ürün Adı', accessor: 'item_name' },
        ],
        [navigate, onSelectProduct]
    );

    const tableInstance = useTable(
        { columns, data: products, initialState: { pageIndex: 0, pageSize: 20 } },
        usePagination
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
        state: { pageIndex, pageSize }
    } = tableInstance;

    if (loading) return <p className="product-list-container__loading">Yükleniyor...</p>;
    if (error) return <p className="product-list-container__error">Hata: {error}</p>;

    return (
        <div className="product-list-container">
            <h2 className="product-list-container__header">Ürün Listesi</h2>
            <table className="product-list-container__table" {...getTableProps()}>
                <thead>
                    {headerGroups.map(headerGroup => (
                        <tr {...headerGroup.getHeaderGroupProps()} className="product-list-container__header-row">
                            {headerGroup.headers.map(column => (
                                <th {...column.getHeaderProps()}>{column.render('Header')}</th>
                            ))}
                        </tr>
                    ))}
                </thead>
                <tbody {...getTableBodyProps()}>
                    {page.map(row => {
                        prepareRow(row);
                        return (
                            <tr {...row.getRowProps()} className="product-list-container__row">
                                {row.cells.map(cell => (
                                    <td {...cell.getCellProps()}>{cell.render('Cell')}</td>
                                ))}
                            </tr>
                        );
                    })}
                </tbody>
            </table>
            <Pagination
                canPreviousPage={canPreviousPage}
                canNextPage={canNextPage}
                pageCount={pageCount}
                pageIndex={pageIndex}
                gotoPage={gotoPage}
                nextPage={nextPage}
                previousPage={previousPage}
                pageSize={pageSize}
                setPageSize={setPageSize}
            />
        </div>
    );
};

export default ProductListContainer;
