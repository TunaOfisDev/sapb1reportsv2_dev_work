// frontend/src/components/DynamicReport/utils/DynamicPagination.js
import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faAngleDoubleLeft, faAngleLeft, faAngleRight, faAngleDoubleRight } from '@fortawesome/free-solid-svg-icons';
import '../css/DynamicPagination.css';

function DynamicPagination({
  canNextPage,
  canPreviousPage,
  pageOptions,
  pageCount,
  pageIndex,
  gotoPage,
  nextPage,
  previousPage,
  pageSize,
  setPageSize,
}) {
  const handlePageSizeChange = (e) => {
    setPageSize(Number(e.target.value));
  };

  return (
    <div className="dynamicreport-pagination__controls">
      <div className="dynamicreport-pagination__size-selector">
        <select
          className="dynamicreport-pagination__select"
          value={pageSize}
          onChange={handlePageSizeChange}
        >
          {[10, 20, 30, 40, 50, 100, 500, 1000].map((size) => (
            <option key={size} value={size}>
              {size}
            </option>
          ))}
        </select>
      </div>
      <button
        className="dynamicreport-pagination__button"
        onClick={() => gotoPage(0)}
        disabled={!canPreviousPage}
      >
        <FontAwesomeIcon icon={faAngleDoubleLeft} />
      </button>
      <button
        className="dynamicreport-pagination__button"
        onClick={() => previousPage()}
        disabled={!canPreviousPage}
      >
        <FontAwesomeIcon icon={faAngleLeft} />
      </button>
      <button
        className="dynamicreport-pagination__button"
        onClick={() => nextPage()}
        disabled={!canNextPage}
      >
        <FontAwesomeIcon icon={faAngleRight} />
      </button>
      <button
        className="dynamicreport-pagination__button"
        onClick={() => gotoPage(pageCount - 1)}
        disabled={!canNextPage}
      >
        <FontAwesomeIcon icon={faAngleDoubleRight} />
      </button>
      <span className="dynamicreport-pagination__info">
        Sayfa {pageIndex + 1} / {pageCount}
      </span>
    </div>
  );
}

export default DynamicPagination;


