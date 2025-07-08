// File: frontend/src/components/ProcureCompare/cells/TeklifFiyatlariCell.js

import React from 'react';
import PropTypes from 'prop-types';
import formatNumber from '../utils/FormatNumber';
import '../css/TeklifFiyatlariCell.css';

const TeklifFiyatlariCell = ({ row }) => {
  const entries = row.original.teklif_fiyatlari_list;
  const referanslar = row.original.referans_teklifler;

  const tooltipText = (() => {
    try {
      if (!referanslar) return '';
      const parsed = typeof referanslar === 'string' ? JSON.parse(referanslar) : referanslar;
      return Array.isArray(parsed) && parsed.length > 0
        ? `Referans Teklifler: ${parsed.join(', ')}`
        : '';
    } catch {
      return '';
    }
  })();

  if (!entries || !entries.length) return null;

  const minLocal = Math.min(...entries.map(e => e.local_price));
  const EPSILON = 0.001;

  return (
    <div className="teklif-cell__wrapper" title={tooltipText}>
      {entries
        .sort((a, b) => a.local_price - b.local_price)
        .map((entry, idx) => {
          const isMin = Math.abs(entry.local_price - minLocal) < EPSILON;
          
          const displayText = `${entry.firma.slice(0, 8)}-${formatNumber(entry.fiyat, 3)}${entry.doviz}-VG=${entry.vade_gun}-TG=${entry.teslim_gun}`;

          return (
            <div
              key={idx}
              className={`teklif-cell__entry ${isMin ? 'teklif-cell__entry--highlight' : ''}`}
            >
              <span className={`teklif-cell__fiyat ${isMin ? 'teklif-cell__fiyat--highlight' : ''}`}>
                {displayText}
              </span>
            </div>
          );
        })}
    </div>
  );
};

TeklifFiyatlariCell.propTypes = {
  row: PropTypes.object.isRequired
};

export default TeklifFiyatlariCell;


