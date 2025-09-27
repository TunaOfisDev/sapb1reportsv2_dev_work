// frontend/src/components/Activities/views/CalendarView.js
import React, { useState } from 'react';
import { Calendar, dateFnsLocalizer } from 'react-big-calendar';
import { parse, startOfWeek, getDay, format } from 'date-fns';
import { tr } from 'date-fns/locale';
import dayjs from 'dayjs';
import 'dayjs/locale/tr';
import useActivities from '../hooks/useActivities';
import ShowModalCard from '../utils/ShowModalCard';
import ShowModalList from '../utils/ShowModalList';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import '../css/CalendarView.css';

const locales = {
  tr: tr,
};

const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek: () => startOfWeek(new Date(), { weekStartsOn: 1 }),
  getDay,
  locales,
});

const CalendarView = () => {
  const { localActivities, loading, error } = useActivities();
  const [isCardModalOpen, setIsCardModalOpen] = useState(false);
  const [isListModalOpen, setIsListModalOpen] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [selectedDayEvents, setSelectedDayEvents] = useState([]);

  const handleEventSelect = (event) => {
    setSelectedEvent(event);
    setIsCardModalOpen(true);
  };

  const handleDayClick = (events) => {
    setSelectedDayEvents(events);
    setIsListModalOpen(true);
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  const events = localActivities.map((activity) => ({
    ...activity,
    title: `${activity.isleyen} - ${activity.aktivite || "Genel Aktivite"}`,
    start: dayjs(activity.baslangic_tarihi).toDate(),
    end: dayjs(activity.baslangic_tarihi).toDate(),
  }));

  return (
    <div className="calendar">
      <Calendar
        localizer={localizer}
        events={events}
        startAccessor="start"
        endAccessor="end"
        style={{ height: '100vh' }}
        onSelectEvent={handleEventSelect}
        onShowMore={(events) => handleDayClick(events)}
      />
      <ShowModalCard
        isOpen={isCardModalOpen}
        closeModal={() => setIsCardModalOpen(false)}
        event={selectedEvent}
      />
      <ShowModalList
        isOpen={isListModalOpen}
        closeModal={() => setIsListModalOpen(false)}
        dayEvents={selectedDayEvents}
      />
    </div>
  );
};

export default CalendarView;
