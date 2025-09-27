// frontend\src\components\Pagination\Pagination.js
import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faAngleDoubleLeft, faAngleLeft, faAngleRight, faAngleDoubleRight } from '@fortawesome/free-solid-svg-icons';
import '../css/Pagination.css'

function Pagination({ canNextPage, canPreviousPage, pageCount, pageIndex, gotoPage, nextPage, previousPage, pageSize, setPageSize }) {
    return (
        <div className='pagination-controls'>
            {/* Sayfa satır gösterim seçimi */}
            <div className='pagination-size-selector'>
                <label className='pagination-size-selector label' htmlFor="pageSize"></label>
                <select className='pagination-select'
                    value={pageSize}
                    onChange={e => setPageSize(Number(e.target.value))}
                > 
                    {[10, 20, 30, 40, 50, 100, 500, 1000].map(size => (
                        <option key={size} value={size}>
                            {size}
                        </option>
                    ))}
                </select>
            </div>
            <button className='pagination-button' onClick={() => gotoPage(0)} disabled={!canPreviousPage}>
                <FontAwesomeIcon icon={faAngleDoubleLeft} />
            </button>
            <button className='pagination-button' onClick={() => previousPage()} disabled={!canPreviousPage}>
                <FontAwesomeIcon icon={faAngleLeft} />
            </button>
            <button className='pagination-button' onClick={() => nextPage()} disabled={!canNextPage}>
                <FontAwesomeIcon icon={faAngleRight} />
            </button>
            <button className='pagination-button' onClick={() => gotoPage(pageCount - 1)} disabled={!canNextPage}>
                <FontAwesomeIcon icon={faAngleDoubleRight} />
            </button>
            <span className='pagination-info'>
                Page {pageIndex + 1} of {pageCount}
            </span>
        </div>
    );
}

export default Pagination;