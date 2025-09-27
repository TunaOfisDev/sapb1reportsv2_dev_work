// frontend/src/components/EduVideo/utils/Pagination.js
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
  pageSize,
  setPageSize,
}) {
  return (
    <div className='pagination-controls'>
      {/* Sayfa satır gösterim seçimi */}
      <div className='pagination-size-selector'>
      <select
  className='pagination-select'
  value={pageSize}
  onChange={(e) => setPageSize(Number(e.target.value))}
>
  {[10, 20, 30, 50, 100].map((size) => (
    <option key={size} value={size}>
      {size} göster
    </option>
  ))}
</select>

      </div>
      {/* İlk sayfaya ve önceki sayfaya gitme butonları */}
      <button className='pagination-button' onClick={() => gotoPage(0)} disabled={!canPreviousPage}>
        <FontAwesomeIcon icon={faAngleDoubleLeft} />
      </button>
      <button className='pagination-button' onClick={() => gotoPage(pageIndex - 1)} disabled={!canPreviousPage}>
        <FontAwesomeIcon icon={faAngleLeft} />
      </button>
      {/* Sayfa numaralarını kaldırıldı */}
      {/* Sonraki sayfaya ve son sayfaya gitme butonları */}
      <button className='pagination-button' onClick={() => gotoPage(pageIndex + 1)} disabled={!canNextPage}>
        <FontAwesomeIcon icon={faAngleRight} />
      </button>
      <button className='pagination-button' onClick={() => gotoPage(pageCount - 1)} disabled={!canNextPage}>
        <FontAwesomeIcon icon={faAngleDoubleRight} />
      </button>
      {/* Mevcut sayfa ve toplam sayfa sayısı bilgisi */}
      <span className='pagination-info'>
        {pageIndex + 1} / {pageCount} sayfa
      </span>
    </div>
  );
}

export default Pagination;