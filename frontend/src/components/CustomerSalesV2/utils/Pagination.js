// frontend/src/components/CustomerSalesV2/utils/pgcs.js
import React from 'react';
import PropTypes from 'prop-types';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faAngleDoubleLeft, faAngleLeft, faAngleRight, faAngleDoubleRight } from '@fortawesome/free-solid-svg-icons';
import '../css/Pagination.css';

function pgcs({ canNextPage, canPreviousPage, pageCount, pageIndex, gotoPage, nextPage, previousPage, pageSize, setPageSize }) {
  return (
    <div className='pgcs-controls'>
      <div className='pgcs-controls__size-selector'>
        <label className='pgcs-controls__label' htmlFor="pageSize">Satır:</label>
        <select
          id="pageSize"
          className='pgcs-controls__select'
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

      <button 
        className={`pgcs-controls__button ${!canPreviousPage ? 'pgcs-controls__button--disabled' : ''}`} 
        onClick={() => gotoPage(0)} 
        disabled={!canPreviousPage}
      >
        <FontAwesomeIcon icon={faAngleDoubleLeft} />
      </button>
      <button 
        className={`pgcs-controls__button ${!canPreviousPage ? 'pgcs-controls__button--disabled' : ''}`} 
        onClick={() => previousPage()} 
        disabled={!canPreviousPage}
      >
        <FontAwesomeIcon icon={faAngleLeft} />
      </button>
      
      <span className='pgcs-controls__info'>
        Sayfa <strong>{pageIndex + 1}</strong> / {pageCount}
      </span>
      
      <button 
        className={`pgcs-controls__button ${!canNextPage ? 'pgcs-controls__button--disabled' : ''}`} 
        onClick={() => nextPage()} 
        disabled={!canNextPage}
      >
        <FontAwesomeIcon icon={faAngleRight} />
      </button>
      <button 
        className={`pgcs-controls__button ${!canNextPage ? 'pgcs-controls__button--disabled' : ''}`} 
        onClick={() => gotoPage(pageCount - 1)} 
        disabled={!canNextPage}
      >
        <FontAwesomeIcon icon={faAngleDoubleRight} />
      </button>
    </div>
  );
}

// Prop tiplerini tanımlayarak bileşeni daha güvenli hale getiriyoruz.
pgcs.propTypes = {
    canNextPage: PropTypes.bool.isRequired,
    canPreviousPage: PropTypes.bool.isRequired,
    pageCount: PropTypes.number.isRequired,
    pageIndex: PropTypes.number.isRequired,
    gotoPage: PropTypes.func.isRequired,
    nextPage: PropTypes.func.isRequired,
    previousPage: PropTypes.func.isRequired,
    pageSize: PropTypes.number.isRequired,
    setPageSize: PropTypes.func.isRequired,
};

export default pgcs;