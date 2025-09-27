// frontend/src/components/DeliveryDocSumV2/utils/ShowModalOrderNumbers.js
import React from 'react';
import Modal from 'react-modal';

Modal.setAppElement('#root'); // Make sure to set this properly if not already done.

const ShowModalOrderNumbers = ({ modalIsOpen, closeModal, selectedOrders, cariKod, cariAdi }) => {
    return (
        <Modal
            isOpen={modalIsOpen}
            onRequestClose={closeModal}
            contentLabel="Sipariş Numaraları"
            style={{
                content: {
                    top: '50%',
                    left: '50%',
                    right: 'auto',
                    bottom: 'auto',
                    marginRight: '-50%',
                    transform: 'translate(-50%, -50%)',
                    width: '40%',
                    maxHeight: '70vh', // Modal yüksekliğini ekranın %70'i ile sınırlar
                    border: '1px solid #ccc',
                    background: '#fff',
                    overflow: 'auto',
                    WebkitOverflowScrolling: 'touch',
                    borderRadius: '4px',
                    outline: 'none',
                    padding: '20px'
                }
            }}
        >
            <h2>Sipariş Numaraları - {cariKod} - {cariAdi}</h2>
            {selectedOrders && selectedOrders !== '0' ? 
                <p>{selectedOrders.split(',').map(number => number.trim()).join(', ')}</p> 
                : <p>Mevcut sipariş numarası yok.</p>}
            <button onClick={closeModal}>Kapat</button>
        </Modal>
    );
};

export default ShowModalOrderNumbers;

