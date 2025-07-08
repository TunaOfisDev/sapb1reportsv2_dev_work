// frontend/src/components/CrmBlog/utils/crmblog-pagination.js
import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faAngleDoubleLeft, faAngleLeft, faAngleRight, faAngleDoubleRight } from '@fortawesome/free-solid-svg-icons';
import '../css/Pagination.css';

function Pagination({ canNextPage, canPreviousPage, pageCount, pageIndex, gotoPage, nextPage, previousPage, pageSize, setPageSize }) {
  return (
    <div className='crmblog-pagination__controls'>
      <div className='crmblog-pagination__size-selector'>
        <label className='crmblog-pagination__size-selector-label' htmlFor="pageSize">Göster:</label>
        <select
          className='crmblog-pagination__select'
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
      <button className='crmblog-pagination__button' onClick={() => gotoPage(0)} disabled={!canPreviousPage}>
        <FontAwesomeIcon icon={faAngleDoubleLeft} />
      </button>
      <button className='crmblog-pagination__button' onClick={() => previousPage()} disabled={!canPreviousPage}>
        <FontAwesomeIcon icon={faAngleLeft} />
      </button>
      <button className='crmblog-pagination__button' onClick={() => nextPage()} disabled={!canNextPage}>
        <FontAwesomeIcon icon={faAngleRight} />
      </button>
      <button className='crmblog-pagination__button' onClick={() => gotoPage(pageCount - 1)} disabled={!canNextPage}>
        <FontAwesomeIcon icon={faAngleDoubleRight} />
      </button>
      <span className='crmblog-pagination__info'>
        Sayfa {pageIndex + 1} / {pageCount}
      </span>
    </div>
  );
}

export default Pagination;