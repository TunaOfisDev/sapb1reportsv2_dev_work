// frontend/src/components/DeliveryDocSumV2/utils/ShowModalOpenDelivery.js
import React from 'react';
import Modal from 'react-modal';

Modal.setAppElement('#root'); // Make sure to set this properly if not already done.

const ShowModalOpenDelivery = ({ modalIsOpen, closeModal, selectedDeliveries, cariKod, cariAdi }) => {
    const deliveryList = selectedDeliveries && selectedDeliveries !== '0' ? 
        selectedDeliveries.split(';').map((delivery, index) => (
            <div key={index}>{delivery.trim()}</div>
        )) 
        : <div>Mevcut açık sevkiyat yok.</div>;

    return (
        <Modal
            isOpen={modalIsOpen}
            onRequestClose={closeModal}
            contentLabel="Açık Sevkiyatlar"
            style={{
                content: {
                    top: '50%',
                    left: '50%',
                    right: 'auto',
                    bottom: 'auto',
                    marginRight: '-50%',
                    transform: 'translate(-50%, -50%)',
                    width: '50%',
                    maxHeight: '70vh',
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
            <h2>Açık Sevkiyatlar - {cariKod} - {cariAdi}</h2>
            <div>
                {deliveryList}
            </div>
            <button onClick={closeModal}>Kapat</button>
        </Modal>
    );
};

export default ShowModalOpenDelivery;
