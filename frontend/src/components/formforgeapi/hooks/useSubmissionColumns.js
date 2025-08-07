// path: frontend/src/components/formforgeapi/hooks/useSubmissionColumns.js

import { useMemo } from 'react';

/**
 * Gönderi veri tablosu için sütunları ve eylem butonlarını oluşturan hook.
 * DÜZELTME: formSchema asenkron yüklendiğinde bile tablonun bozulmamasını sağlar.
 * @param {object} formSchema - Mevcut formun şeması
 * @param {object} user - Giriş yapmış kullanıcı bilgisi
 * @param {object} actionHandlers - handleView, handleEdit, handleHistory fonksiyonlarını içeren obje
 * @param {object} classNames - Butonlar ve hücreler için CSS sınıfları
 * @returns {Array} react-table tarafından kullanılacak columns dizisi.
 */
export const useSubmissionColumns = (formSchema, user, actionHandlers, classNames) => {
    const columns = useMemo(() => {
        // 1. Dinamik 'master' alanlarını sadece form şeması yüklendiğinde oluştur.
        // formSchema henüz yoksa, masterFields boş bir dizi olur.
        const masterFields = formSchema?.fields
            ? formSchema.fields
                .filter(f => f.is_master)
                .sort((a, b) => a.order - b.order)
                .map(field => ({
                    Header: field.label,
                    accessor: (row) => {
                        const valueObj = row.values.find(v => v.form_field === field.id);
                        if (Array.isArray(valueObj?.value)) {
                            return valueObj.value.join(', ');
                        }
                        // Değerin null veya undefined olabileceğini göz önünde bulundurarak String'e çevir.
                        return valueObj ? String(valueObj.value) : '—';
                    }
                }))
            : [];

        // 2. Her zaman gösterilecek olan statik sütunlar.
        const baseColumns = [
            { Header: 'Versiyon', accessor: 'version', Cell: ({ value }) => `V${value}` },
            { Header: 'Gönderen', accessor: 'created_by.email' },
            { Header: 'Gönderim Tarihi', accessor: 'created_at', Cell: ({ value }) => new Date(value).toLocaleString() },
        ];

        // 3. Eylem butonlarını içeren sütun.
        const actionColumn = {
            Header: 'Eylemler',
            id: 'actions',
            Cell: ({ row }) => (
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
            ),
        };

        // 4. Dinamik ve statik sütunları birleştirerek nihai listeyi döndür.
        return [...masterFields, ...baseColumns, actionColumn];

    }, [formSchema, user, actionHandlers, classNames]);

    return columns;
};