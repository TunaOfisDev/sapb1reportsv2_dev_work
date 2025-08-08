import React from 'react';
import { useMemo } from 'react';

export const useSubmissionColumns = (formSchema, user, actionHandlers, classNames, mode = 'mainList') => {
    const columns = useMemo(() => {
        const masterFields = formSchema?.fields
            ? formSchema.fields
                .sort((a, b) => a.order - b.order)
                .map(field => ({
                    Header: field.label,
                    Cell: ({ row }) => {
                        // DÜZELTME: Satırın orijinal verisine 'row.original.values' ile erişiyoruz.
                        const valueObj = row.original.values.find(v => v.form_field === field.id);
                        let cellValue = '—';

                        if (valueObj) {
                            if (Array.isArray(valueObj.value)) {
                                cellValue = valueObj.value.join(', ');
                            } else {
                                cellValue = valueObj.value != null ? String(valueObj.value) : '—';
                            }
                        }
                        
                        return (
                            <span className={classNames.cellContent} title={cellValue}>
                                {cellValue}
                            </span>
                        );
                    }
                }))
            : [];

        const baseColumns = [
            { Header: 'Versiyon', accessor: 'version', Cell: ({ value }) => `V${value}` },
            { Header: 'Gönderen', accessor: 'created_by.email' },
            { Header: 'Gönderim Tarihi', accessor: 'created_at', Cell: ({ value }) => new Date(value).toLocaleString() },
        ];

        const actionColumn = {
            Header: 'Eylemler',
            id: 'actions',
            Cell: ({ row }) => {
                if (mode === 'historyModal') {
                    return (
                        <div className={classNames.cellContent}>
                            <button
                                className={classNames.buttonInfo}
                                onClick={() => actionHandlers.handleView(row.original)}
                            >
                                Görüntüle
                            </button>
                        </div>
                    );
                }

                return (
                    <div className={classNames.cellContent}>
                        <button
                            className={classNames.buttonInfo}
                            onClick={() => actionHandlers.handleView(row.original)}
                        >
                            Görüntüle
                        </button>
                        {row.original.is_owner && (
                            <button
                                className={classNames.buttonPrimary}
                                style={{ marginLeft: '0.5rem' }}
                                onClick={() => actionHandlers.handleEdit(row.original)}
                            >
                                Düzenle
                            </button>
                        )}
                        <button
                            className={classNames.buttonSecondary}
                            style={{ marginLeft: '0.5rem' }}
                            onClick={() => actionHandlers.handleHistory(row.original)}
                        >
                            Geçmiş
                        </button>
                    </div>
                );
            },
        };

        return [...masterFields, ...baseColumns, actionColumn];

    }, [formSchema, user, actionHandlers, classNames, mode]);

    return columns;
};