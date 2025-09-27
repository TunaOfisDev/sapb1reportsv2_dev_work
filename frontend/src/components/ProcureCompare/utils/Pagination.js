// frontend/src/components/ProcureCompare/utils/Pagination.js
import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faAngleDoubleLeft, faAngleLeft, faAngleRight, faAngleDoubleRight } from '@fortawesome/free-solid-svg-icons';
import '../css/Pagination.css';

function Pagination({ canNextPage, canPreviousPage, pageCount, pageIndex, gotoPage, nextPage, previousPage, pageSize, setPageSize }) {
    return (
        <div className='procurecompare-pagination__controls'>
            {/* Sayfa satır gösterim seçimi */}
            <div className='procurecompare-pagination__size-selector'>
                <label className='procurecompare-pagination__size-selector-label' htmlFor="pageSize"></label>
                <select className='procurecompare-pagination__select'
                    value={pageSize}
                    onChange={e => setPageSize(Number(e.target.value))}
                > 
                    {[100, 200, 300, 400, 500, 1000].map(size => (
                        <option key={size} value={size}>
                            {size}
                        </option>
                    ))}
                </select>
            </div>
            <button className='procurecompare-pagination__button' onClick={() => gotoPage(0)} disabled={!canPreviousPage}>
                <FontAwesomeIcon icon={faAngleDoubleLeft} />
            </button>
            <button className='procurecompare-pagination__button' onClick={() => previousPage()} disabled={!canPreviousPage}>
                <FontAwesomeIcon icon={faAngleLeft} />
            </button>
            <button className='procurecompare-pagination__button' onClick={() => nextPage()} disabled={!canNextPage}>
                <FontAwesomeIcon icon={faAngleRight} />
            </button>
            <button className='procurecompare-pagination__button' onClick={() => gotoPage(pageCount - 1)} disabled={!canNextPage}>
                <FontAwesomeIcon icon={faAngleDoubleRight} />
            </button>
            <span className='procurecompare-pagination__info'>
                Page {pageIndex + 1} of {pageCount}
            </span>
        </div>
    );
}

export default Pagination;
