// frontend/src/components/Activities/utils/ShowModalCard.js
import React from 'react';
import Modal from 'react-modal';
import dayjs from 'dayjs';
import 'dayjs/locale/tr';
import '../css/ShowModalCard.css';

Modal.setAppElement('#root');

const ShowModalCard = ({ isOpen, closeModal, event }) => { // 'events' yerine 'event' kullanılıyor
  if (!event) {
    return null; // Eğer event tanımlı değilse hiçbir şey render etme
  }

  return (
    <Modal isOpen={isOpen} onRequestClose={closeModal} className="show-modal-card" overlayClassName="show-modal-card__overlay">
      <div className="show-modal-card__header">
        <h2 className="show-modal-card__title">Etkinlik Detayları</h2>
      </div>
      <div className="show-modal-card__event-list">
        <div className="show-modal-card__event-item">
          <h3 className="show-modal-card__event-title">{event.isleyen} - {event.aktivite}</h3>
          <p className="show-modal-card__event-description"><strong>İşleyen:</strong> {event.isleyen}</p>
          <p className="show-modal-card__event-description"><strong>Başlangıç Tarihi:</strong> {dayjs(event.start).locale('tr').format('LL')}</p>
          <p className="show-modal-card__event-description"><strong>Açıklama:</strong> {event.aciklama}</p>
          <p className="show-modal-card__event-description"><strong>icerik:</strong> {event.icerik}</p>
          <hr />
        </div>
      </div>
      <button onClick={closeModal} className="show-modal-card__close-button">Kapat</button>
    </Modal>
  );
};

export default ShowModalCard;
