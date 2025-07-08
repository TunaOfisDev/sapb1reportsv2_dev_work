// frontend/src/components/Activities/utils/Pagination.js
import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faAngleDoubleLeft,
  faAngleLeft,
  faAngleRight,
  faAngleDoubleRight,
} from '@fortawesome/free-solid-svg-icons';
import '../css/Pagination.css';

function Pagination({
  canNextPage,
  canPreviousPage,
  pageCount,
  pageIndex,
  gotoPage,
  nextPage,
  previousPage,
  pageSize,
  setPageSize,
}) {
  return (
    <div className="activities_pagination__controls">
      {/* satır sayısı seçimi */}
      <select
        className="activities_pagination__select"
        value={pageSize}
        onChange={e => setPageSize(Number(e.target.value))}
      >
        {[100, 200, 300, 400, 500, 1000].map(size => (
          <option key={size} value={size}>
            {size}
          </option>
        ))}
      </select>

      <button
        className="activities_pagination__button"
        onClick={() => gotoPage(0)}
        disabled={!canPreviousPage}
        title="İlk sayfa"
      >
        <FontAwesomeIcon icon={faAngleDoubleLeft} />
      </button>

      <button
        className="activities_pagination__button"
        onClick={previousPage}
        disabled={!canPreviousPage}
        title="Önceki"
      >
        <FontAwesomeIcon icon={faAngleLeft} />
      </button>

      <span className="activities_pagination__info">
        <strong>{pageIndex + 1}</strong> / {pageCount}
      </span>

      <button
        className="activities_pagination__button"
        onClick={nextPage}
        disabled={!canNextPage}
        title="Sonraki"
      >
        <FontAwesomeIcon icon={faAngleRight} />
      </button>

      <button
        className="activities_pagination__button"
        onClick={() => gotoPage(pageCount - 1)}
        disabled={!canNextPage}
        title="Son sayfa"
      >
        <FontAwesomeIcon icon={faAngleDoubleRight} />
      </button>
    </div>
  );
}

export default Pagination;

