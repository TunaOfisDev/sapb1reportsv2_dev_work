// File: frontend/src/components/ProcureCompare/utils/AccordionTableHelper.jsx

import { useState } from 'react';

export const useAccordionTable = () => {
  const [expandedRows, setExpandedRows] = useState(new Set());

  const handleRowClick = (rowId) => {
    setExpandedRows((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(rowId)) {
        newSet.delete(rowId);
      } else {
        newSet.add(rowId);
      }
      return newSet;
    });
  };

  const handleExpandAll = (rows) => {
    const allRowIds = new Set(rows.map((row) => row.original.uniq_detail_no));
    setExpandedRows(allRowIds);
  };

  const handleCollapseAll = () => {
    setExpandedRows(new Set());
  };

  const isRowExpanded = (rowId) => {
    return expandedRows.has(rowId);
  };

  const allExpanded = false; // İstersen dinamik kontrol ekleyebilirim.

  return {
    expandedRows,
    allExpanded,
    handleRowClick,
    handleExpandAll,
    handleCollapseAll,
    isRowExpanded,
  };
};
