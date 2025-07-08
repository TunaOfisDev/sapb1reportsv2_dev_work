// frontend/src/components/Activities/utils/Last5DayFilter.js
import React from 'react';
import '../css/Last5DayFilter.css';

const Last5DayFilter = ({ setFilter }) => {
  const handleDayClick = (offset) => {
    const selectedDate = new Date();
    selectedDate.setDate(selectedDate.getDate() - offset);
    setFilter(selectedDate.toISOString().slice(0, 10));
  };

  return (
    <div className="last5DaysFilter">
      {
        Array.from({ length: 5 }, (_, i) => i).map((dayOffset) => (
          <button
            key={dayOffset}
            className={`last5DaysFilter__button ${dayOffset === 0 ? 'last5DaysFilter__button--selected' : ''}`}
            onClick={() => handleDayClick(dayOffset)}>
            {new Date(new Date().setDate(new Date().getDate() - dayOffset)).toLocaleDateString('tr-TR')}
          </button>
        ))
      }
    </div>
  );
};

export default Last5DayFilter;

