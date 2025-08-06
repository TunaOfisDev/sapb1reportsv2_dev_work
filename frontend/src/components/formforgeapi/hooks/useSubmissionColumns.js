// path: frontend/src/components/formforgeapi/hooks/useSubmissionColumns.js

import React, { useMemo } from 'react';

// Bu hook'un en kararlı ve doğru çalışan versiyonudur.
export function useSubmissionColumns(currentForm, user, actionHandlers, classNames = {}) {
  
  // Önceki hataya sebep olan destructuring işlemini buradan kaldırıyoruz.
  // Bunun yerine, 'actionHandlers' objesinin tamamını useMemo'ya bağımlılık olarak vereceğiz.

  const columns = useMemo(() => {
    if (!currentForm?.fields) return [];

    // Fonksiyonları useMemo'nun İÇİNDE güvenli bir şekilde çağırıyoruz.
    // actionHandlers tanımsız olsa bile, ?. (optional chaining) ve || (or) sayesinde çökmeyecek.
    const internalHandleViewClick = actionHandlers?.handleViewClick || (() => {});
    const internalHandleEditClick = actionHandlers?.handleEditClick || (() => {});

    const dynamicColumns = currentForm.fields
      .sort((a, b) => a.order - b.order)
      .map((field) => ({
        Header: field.label,
        accessor: (row) => (row.values.find(v => v.form_field === field.id)?.value || "—"),
        Cell: ({ value }) => (
          <div className={classNames.cellContent} title={value}>
            {value}
          </div>
        ),
        id: `field_${field.id}`,
      }));

    const staticColumns = [
      { Header: "Gönderen", accessor: (row) => row.created_by?.email || "Bilinmiyor", id: 'created_by' },
      { Header: "Gönderim Tarihi", accessor: 'created_at', Cell: ({ value }) => new Date(value).toLocaleString(), id: 'created_at' },
      {
        Header: "Eylemler",
        id: "actions",
        Cell: ({ row }) => (
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button className={classNames.buttonInfo} onClick={() => internalHandleViewClick(row.original)}>Görüntüle</button>
            {user && user.id === row.original.created_by?.id && (
              <button className={classNames.buttonPrimary} onClick={() => internalHandleEditClick(row.original)}>Düzenle</button>
            )}
          </div>
        ),
      },
    ];

    return [...dynamicColumns, ...staticColumns];
  // `useMemo` artık doğrudan `actionHandlers` objesini dinliyor.
  // Bu obje değiştiğinde, useMemo yeniden çalışacak ve butonlar doğru fonksiyonlara bağlanacaktır.
  }, [currentForm, user, actionHandlers, classNames]);

  return columns;
}