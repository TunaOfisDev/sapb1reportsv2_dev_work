// path: frontend/src/components/formforgeapi/hooks/useSubmissionColumns.js

import React, { useMemo } from 'react';

export function useSubmissionColumns(currentForm, user, actionHandlers, classNames = {}) {
  
  const columns = useMemo(() => {
    if (!currentForm?.fields) return [];

    const internalHandleViewClick = actionHandlers?.handleViewClick || (() => {});
    const internalHandleEditClick = actionHandlers?.handleEditClick || (() => {});

    // ... (dynamicColumns kısmı aynı kalacak) ...
    const dynamicColumns = currentForm.fields
      .sort((a, b) => a.order - b.order)
      .map((field) => ({
        Header: field.label,
        accessor: (row) => (row.values.find(v => v.form_field === field.id)?.value || "—"),
        Cell: ({ value }) => {
          const displayValue = Array.isArray(value) ? value.join(', ') : value;
          return (
            <div className={classNames.cellContent} title={displayValue}>
              {displayValue}
            </div>
          );
        },
        id: `field_${field.id}`,
      }));

    const staticColumns = [
      { Header: "Versiyon", accessor: (row) => `V${row.version}`, id: 'version' },
      { Header: "Gönderen", accessor: (row) => row.created_by?.email || "Bilinmiyor", id: 'created_by' },
      { Header: "Gönderim Tarihi", accessor: 'created_at', Cell: ({ value }) => new Date(value).toLocaleString(), id: 'created_at' },
      {
        Header: "Eylemler",
        id: "actions",
        Cell: ({ row }) => {
          // --- NİHAİ DÜZELTME: Artık kontrolü backend'den gelen `is_owner` alanına göre yapıyoruz. ---
          // Bu, en güvenilir ve en basit yöntemdir.
          const isOwner = row.original.is_owner;

          return (
            // Hata ayıklama kutusu tamamen kaldırıldı.
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button className={classNames.buttonInfo} onClick={() => internalHandleViewClick(row.original)}>Görüntüle</button>
              {isOwner && (
                <button className={classNames.buttonPrimary} onClick={() => internalHandleEditClick(row.original)}>Düzenle</button>
              )}
            </div>
          );
        },
      },
    ];

    return [...dynamicColumns, ...staticColumns];
  // Artık `user` objesine bağımlı değiliz! Bu, kodu daha da sadeleştirir.
  }, [currentForm, actionHandlers, classNames]); 

  return columns;
}