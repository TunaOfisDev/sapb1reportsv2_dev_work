// frontend/src/components/Activities/views/CalendarActivitiesCard.js
import React from 'react';
import dayjs from 'dayjs';
import 'dayjs/locale/tr';
import '../css/CalendarView.css';

const CalendarActivitiesCard = ({ event }) => {
  // Ensure that all the properties you are using below are being passed in the event prop
  return (
    <div className="calendar__event-card">
      <div className="calendar__event-card-header">
        <h3>{event.title}</h3>
      </div>
      <div className="calendar__event-card-body">
        <p><strong>Numara:</strong> {event.numara}</p>
        <p><strong>Başlangıç Tarihi:</strong> {dayjs(event.start).locale('tr').format('LL')}</p>
        <p><strong>İşleyen:</strong> {event.isleyen}</p>
        <p><strong>Tür:</strong> {event.tur}</p>
        <p><strong>Konu:</strong> {event.konu}</p>
        <p><strong>Muhatap:</strong> {event.muhatap_ad || event.muhatap_kod || 'Yok'}</p>
        <p><strong>Durum:</strong> {event.durum}</p>
        <p><strong>Açıklama:</strong> {event.aciklama || 'Açıklama yok'}</p>
        <p><strong>İçerik:</strong> {event.icerik || 'İçerik yok'}</p>
      </div>
    </div>
  );
};

export default CalendarActivitiesCard;
