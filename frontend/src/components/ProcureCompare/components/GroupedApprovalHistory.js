// File: frontend/src/components/ProcureCompare/components/GroupedApprovalHistory.js

import React from 'react';
import PropTypes from 'prop-types';
import useGroupedApprovalHistory from '../hooks/useGroupedApprovalHistory';
import { formatEmailToName } from '../utils/FormatName';
import '../css/GroupedApprovalHistory.css';

const GroupedApprovalHistory = ({ belgeNo, uniqDetailNo }) => {
  const { history, loading, error } = useGroupedApprovalHistory(belgeNo, uniqDetailNo);

  if (loading) return <div className="grouped-history__loading">Yükleniyor...</div>;
  if (error) return <div className="grouped-history__error">⚠ {error}</div>;

  return (
    <div className="grouped-history">
      {history.map((item, index) => (
        <div
          className="grouped-history__item"
          key={index}
          title={item.aciklama || ''} // ✨ Hover ile tam açıklama
        >
          <div className="grouped-history__info">
            <div className="grouped-history__action">{item.action}</div>
            <div className="grouped-history__meta">
              <span>{formatEmailToName(item.kullanici)}</span> | <span>{item.tarih}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

GroupedApprovalHistory.propTypes = {
  belgeNo: PropTypes.string.isRequired,
  uniqDetailNo: PropTypes.string.isRequired
};

export default GroupedApprovalHistory;
