// frontend/src/components/ProductConfig/variant/PCVariantList.js
import React, { useEffect, useState, useCallback } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { fetchVariantList, selectVariantList, selectVariantLoading, selectVariantError, deleteVariant } from '../store/pcVariantSlice';
import PCButton from '../common/PCButton';
import PCInput from '../common/PCInput';
import PCShowModalVariantDetail from '../utils/pcShowModalVariantDetail';
import { usePCVariantTableConfig } from '../hooks/usePCVariantTableConfig';
import '../css/PCVariantList.css';

const PCVariantList = () => {
    // Redux ve Router Hooks
    const dispatch = useDispatch();
    const navigate = useNavigate();
    const variants = useSelector(selectVariantList);
    const loading = useSelector(selectVariantLoading);
    const error = useSelector(selectVariantError);

    // Local State
    const [selectedVariant, setSelectedVariant] = useState(null);
    const [showDetailModal, setShowDetailModal] = useState(false);

    // Event Handlers
    const handleShowDetail = useCallback((variant) => {
        setSelectedVariant(variant);
        setShowDetailModal(true);
    }, []);

    const handleCloseDetailModal = useCallback(() => {
        setShowDetailModal(false);
        setSelectedVariant(null);
    }, []);

    const handleCreateNewVariant = useCallback(() => {
        navigate('/configurator');
    }, [navigate]);

    const handleEditVariant = useCallback((variantId) => {
        navigate(`/configurator/${variantId}`);
    }, [navigate]);

    const handleDeleteVariant = useCallback(async (variantId) => {
        if (window.confirm('Bu varyantı silmek istediğinizden emin misiniz?')) {
            try {
                await dispatch(deleteVariant(variantId));
                setShowDetailModal(false);
            } catch (err) {
                console.error('Varyant silme hatası:', err);
            }
        }
    }, [dispatch]);

    // Varyant listesini yükle
    useEffect(() => {
        dispatch(fetchVariantList());
    }, [dispatch]);

    // Tablo konfigürasyonunu hook ile al
    const {
        getTableProps,
        getTableBodyProps,
        headerGroups,
        page,
        prepareRow,
        canPreviousPage,
        canNextPage,
        pageOptions,
        pageCount,
        gotoPage,
        nextPage,
        previousPage,
        setPageSize,
        state,
        setGlobalFilter,
        columns
    } = usePCVariantTableConfig(variants, handleShowDetail);

    const { pageIndex, pageSize, globalFilter } = state;

    // Global arama bileşeni
    const GlobalFilter = useCallback(({ value, onChange }) => {
        return (
            <PCInput
                type="text"
                name="search"
                value={value || ''}
                onChange={onChange}
                placeholder="Varyant ara..."
                className="pc-variant-list__search"
            />
        );
    }, []);

    // Loading ve Error durumlarını kontrol et
    if (loading) return <div className="pc-variant-list__loading">Yükleniyor...</div>;
    if (error) return <div className="pc-variant-list__error">Hata: {error}</div>;

    // Ana render
    return (
        <div className="pc-variant-list">
            {/* Header Bölümü */}
            <div className="pc-variant-list__actions">
                <h1 className="pc-variant-list__title">Varyant Listesi</h1>
                <div className="flex items-center gap-4">
                    <GlobalFilter
                        value={globalFilter}
                        onChange={e => setGlobalFilter(e.target.value || undefined)}
                    />
                    <PCButton onClick={handleCreateNewVariant} variant="primary">
                        Yeni Varyant Oluştur
                    </PCButton>
                </div>
            </div>

            {/* Tablo Bölümü */}
            <div className="pc-variant-list__table-container">
                <table {...getTableProps()} className="pc-variant-list__table">
                    <thead>
                        {headerGroups.map(headerGroup => {
                            const { key: headerGroupKey, ...headerGroupProps } = headerGroup.getHeaderGroupProps();
                            return (
                                <tr key={headerGroupKey} {...headerGroupProps}>
                                    {headerGroup.headers.map(column => {
                                        const { key: columnKey, ...columnProps } = column.getHeaderProps(column.getSortByToggleProps());
                                        return (
                                            <th key={columnKey} {...columnProps}>
                                                {column.render('Header')}
                                                <span>
                                                    {column.isSorted
                                                        ? column.isSortedDesc
                                                            ? ' ↓'
                                                            : ' ↑'
                                                        : ''}
                                                </span>
                                            </th>
                                        );
                                    })}
                                </tr>
                            );
                        })}
                    </thead>

                    <tbody {...getTableBodyProps()}>
                        {page.length === 0 ? (
                            <tr>
                                <td colSpan={columns?.length || 7} className="pc-variant-list__empty">
                                    Varyant bulunamadı.
                                </td>
                            </tr>
                        ) : (
                            page.map(row => {
                                prepareRow(row);
                                const { key: rowKey, ...rowProps } = row.getRowProps();
                                return (
                                    <tr key={rowKey} {...rowProps}>
                                        {row.cells.map(cell => {
                                            const { key: cellKey, ...cellProps } = cell.getCellProps();
                                            return (
                                                <td key={cellKey} {...cellProps}>
                                                    {cell.render('Cell')}
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

            {/* Sayfalama Bölümü */}
            <div className="pc-variant-list__pagination">
                <div className="pc-variant-list__pagination-info">
                    <span>
                        Sayfa{' '}
                        <strong>
                            {pageIndex + 1} / {pageOptions.length}
                        </strong>
                    </span>
                    <select
                        value={pageSize}
                        onChange={e => setPageSize(Number(e.target.value))}
                        className="pc-variant-list__page-size"
                    >
                        {[10, 20, 30, 40, 50].map(size => (
                            <option key={size} value={size}>
                                {size} adet göster
                            </option>
                        ))}
                    </select>
                </div>
                <div className="pc-variant-list__pagination-controls">
                    <PCButton
                        onClick={() => gotoPage(0)}
                        disabled={!canPreviousPage}
                        className="pc-variant-list__pagination-button"
                    >
                        {'<<'}
                    </PCButton>
                    <PCButton
                        onClick={() => previousPage()}
                        disabled={!canPreviousPage}
                        className="pc-variant-list__pagination-button"
                    >
                        {'<'}
                    </PCButton>
                    <PCButton
                        onClick={() => nextPage()}
                        disabled={!canNextPage}
                        className="pc-variant-list__pagination-button"
                    >
                        {'>'}
                    </PCButton>
                    <PCButton
                        onClick={() => gotoPage(pageCount - 1)}
                        disabled={!canNextPage}
                        className="pc-variant-list__pagination-button"
                    >
                        {'>>'}
                    </PCButton>
                </div>
            </div>

            {/* Detay Modal */}
            {showDetailModal && selectedVariant && (
                <PCShowModalVariantDetail 
                    isOpen={showDetailModal} 
                    onClose={handleCloseDetailModal} 
                    variant={selectedVariant}
                    onEditClick={handleEditVariant}
                    onDeleteClick={handleDeleteVariant}
                />
            )}
        </div>
    );
};

export default PCVariantList;

