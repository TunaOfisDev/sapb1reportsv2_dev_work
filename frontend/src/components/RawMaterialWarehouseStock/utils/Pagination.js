// frontend/src/components/RawMaterialWarehouseStock/utils/Pagination.js
import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faAngleDoubleLeft, faAngleLeft, faAngleRight, faAngleDoubleRight } from '@fortawesome/free-solid-svg-icons';
import '../css/Pagination.css';

function Pagination({ canNextPage, canPreviousPage, pageCount, pageIndex, gotoPage, nextPage, previousPage, pageSize, setPageSize }) {
    return (
        <div className='rawmaterial-pagination__controls'>
            {/* Sayfa satır gösterim seçimi */}
            <div className='rawmaterial-pagination__size-selector'>
                <label className='rawmaterial-pagination__size-selector-label' htmlFor="pageSize"></label>
                <select className='rawmaterial-pagination__select'
                    value={pageSize}
                    onChange={e => setPageSize(Number(e.target.value))}
                > 
                    {[50, 100, 500].map(size => (
                        <option key={size} value={size}>
                            {size}
                        </option>
                    ))}
                </select>
            </div>
            <button className='rawmaterial-pagination__button' onClick={() => gotoPage(0)} disabled={!canPreviousPage}>
                <FontAwesomeIcon icon={faAngleDoubleLeft} />
            </button>
            <button className='rawmaterial-pagination__button' onClick={() => previousPage()} disabled={!canPreviousPage}>
                <FontAwesomeIcon icon={faAngleLeft} />
            </button>
            <button className='rawmaterial-pagination__button' onClick={() => nextPage()} disabled={!canNextPage}>
                <FontAwesomeIcon icon={faAngleRight} />
            </button>
            <button className='rawmaterial-pagination__button' onClick={() => gotoPage(pageCount - 1)} disabled={!canNextPage}>
                <FontAwesomeIcon icon={faAngleDoubleRight} />
            </button>
            <span className='rawmaterial-pagination__info'>
                Page {pageIndex + 1} of {pageCount}
            </span>
        </div>
    );
}

export default Pagination;
