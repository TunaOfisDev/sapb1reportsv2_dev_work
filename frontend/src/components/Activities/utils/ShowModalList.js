// frontend/src/components/Activities/utils/ShowModalList.js
import React from 'react';
import Modal from 'react-modal';
import dayjs from 'dayjs';
import 'dayjs/locale/tr';
import '../css/ShowModalList.css';

Modal.setAppElement('#root'); // Uygulama root elementini modal için ayarla

const ShowModalList = ({ isOpen, closeModal, dayEvents }) => {
  return (
    <Modal isOpen={isOpen} onRequestClose={closeModal} className="show-modal-list" overlayClassName="show-modal-list__overlay">
      <div className="show-modal-list__header">
        <h2 className="show-modal-list__title">Günün Etkinlik Detayları</h2>
        <button onClick={closeModal} className="show-modal-list__close-button">&times;</button>
      </div>
      <div className="show-modal-list__event-list">
        {dayEvents.map((event, index) => (
          <div key={index} className="show-modal-list__event-item">
            <div className="show-modal-list__event-info">
              <h3 className="show-modal-list__event-title">{event.aktivite || 'Genel Aktivite'}</h3>
              <p className="show-modal-list__event-description"><strong>İşleyen:</strong> {event.isleyen}</p>
              <p className="show-modal-list__event-description"><strong>Başlangıç Tarihi:</strong> {dayjs(event.start).locale('tr').format('LL')}</p>
              <p className="show-modal-list__event-description"><strong>Açıklama:</strong> {event.aciklama || 'Açıklama yok'}</p>
              <p className="show-modal-list__event-description"><strong>Icerik:</strong> {event.icerik || 'Icerik yok'}</p>
            </div>
            <hr className="show-modal-list__divider"/>
          </div>
        ))}
      </div>
    </Modal>
  );
};

export default ShowModalList;
