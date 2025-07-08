// frontend/src/components/BomCostManager/utils/pagination.js
import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faAngleDoubleLeft, faAngleLeft, faAngleRight, faAngleDoubleRight } from '@fortawesome/free-solid-svg-icons';
import '../css/Pagination.css';

function pagination({ canNextPage, canPreviousPage, pageCount, pageIndex, gotoPage, nextPage, previousPage, pageSize, setPageSize }) {
    return (
        <div className='bomcostmanager-pagination__controls'>
            {/* Sayfa satır gösterim seçimi */}
            <div className='bomcostmanager-pagination__size-selector'>
                <label className='bomcostmanager-pagination__size-selector-label' htmlFor="pageSize"></label>
                <select className='bomcostmanager-pagination__select'
                    value={pageSize}
                    onChange={e => setPageSize(Number(e.target.value))}
                > 
                    {[20, 30, 40, 50, 100, 500, 1000].map(size => (
                        <option key={size} value={size}>
                            {size}
                        </option>
                    ))}
                </select>
            </div>
            <button className='bomcostmanager-pagination__button' onClick={() => gotoPage(0)} disabled={!canPreviousPage}>
                <FontAwesomeIcon icon={faAngleDoubleLeft} />
            </button>
            <button className='bomcostmanager-pagination__button' onClick={() => previousPage()} disabled={!canPreviousPage}>
                <FontAwesomeIcon icon={faAngleLeft} />
            </button>
            <button className='bomcostmanager-pagination__button' onClick={() => nextPage()} disabled={!canNextPage}>
                <FontAwesomeIcon icon={faAngleRight} />
            </button>
            <button className='bomcostmanager-pagination__button' onClick={() => gotoPage(pageCount - 1)} disabled={!canNextPage}>
                <FontAwesomeIcon icon={faAngleDoubleRight} />
            </button>
            <span className='bomcostmanager-pagination__info'>
                Page {pageIndex + 1} of {pageCount}
            </span>
        </div>
    );
}

export default pagination;
