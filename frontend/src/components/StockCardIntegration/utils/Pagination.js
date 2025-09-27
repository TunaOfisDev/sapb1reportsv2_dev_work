// frontend/src/components/StockCardIntegration/utils/Pagination.js
import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faAngleDoubleLeft,
  faAngleLeft,
  faAngleRight,
  faAngleDoubleRight
} from '@fortawesome/free-solid-svg-icons';
import styles from '../css/Pagination.module.css';

function Pagination({
  canNextPage,
  canPreviousPage,
  pageCount,
  pageIndex,
  gotoPage,
  nextPage,
  previousPage,
  pageSize,
  setPageSize
}) {
  return (
    <div className={styles['pagination-container']}>
      <div className={styles['pagination-controls']}>
        <div className={styles['pagination-info']}>
          <span>
            Sayfa {pageIndex + 1} / {pageCount}
          </span>
        </div>

        <div className={styles['pagination-buttons']}>
          <select
            className={styles['pagination-select']}
            value={pageSize}
            onChange={e => setPageSize(Number(e.target.value))}
          >
            {[100, 200, 300, 400, 500, 1000].map(size => (
              <option key={size} value={size}>
                {size}
              </option>
            ))}
          </select>
          <button onClick={() => gotoPage(0)} disabled={!canPreviousPage}>
            <FontAwesomeIcon icon={faAngleDoubleLeft} />
          </button>
          <button onClick={() => previousPage()} disabled={!canPreviousPage}>
            <FontAwesomeIcon icon={faAngleLeft} />
          </button>
          <button onClick={() => nextPage()} disabled={!canNextPage}>
            <FontAwesomeIcon icon={faAngleRight} />
          </button>
          <button onClick={() => gotoPage(pageCount - 1)} disabled={!canNextPage}>
            <FontAwesomeIcon icon={faAngleDoubleRight} />
          </button>
        </div>
      </div>
    </div>
  );
}

export default Pagination;
