// path: frontend/src/components/formforgeapi/utils/SubmissionHistoryModal.jsx

import React from 'react';

// Bileşenleri doğru yollardan import ediyoruz.
import Modal from '../components/reusable/Modal';
import DataTable from '../components/reusable/DataTable';

// Stil dosyasını import ediyoruz.
import styles from '../css/SubmissionHistoryModal.module.css';

/**
 * Gönderi geçmişini detaylı bir tablo olarak gösteren modal.
 * @param {boolean} isOpen - Modalın açık olup olmadığını belirler.
 * @param {function} onClose - Modal kapatıldığında çağrılacak fonksiyon.
 * @param {object} submission - Geçmişi görüntülenen ana gönderi.
 * @param {Array} history - Tabloda gösterilecek gönderi versiyonlarının listesi.
 * @param {boolean} isLoading - Verinin yüklenip yüklenmediğini belirtir.
 * @param {Array} columns - DataTable için sütun tanımları.
 */
const SubmissionHistoryModal = ({ isOpen, onClose, submission, history, isLoading, columns }) => {
    if (!isOpen) {
        return null;
    }

    return (
        <Modal isOpen={isOpen} onClose={onClose} title={`Gönderi Geçmişi (ID: ${submission?.id})`}>
            <div className={styles.historyModal}>
                {isLoading ? (
                    <div className={styles.loadingState}>Geçmiş yükleniyor...</div>
                ) : (
                    // DEĞİŞİKLİK: Basit <ul> listesi yerine artık DataTable bileşenini kullanıyoruz.
                    // Ana ekrandan gelen 'columns' prop'unu doğrudan DataTable'a iletiyoruz.
                    <DataTable columns={columns} data={history} />
                )}
            </div>
        </Modal>
    );
};

export default SubmissionHistoryModal;