// DateRangeColumnFilter.js
import React from 'react';
import DatePicker from 'react-datepicker';
import { tr } from 'date-fns/locale';
import 'react-datepicker/dist/react-datepicker.css';
import '../css/DateRangeColumnFilter.css';

const DateRangeColumnFilter = ({ column: { filterValue = [], setFilter } }) => {
  const [startDate, endDate] = filterValue;

  const resetTime = (date) => {
    return date ? new Date(date.setHours(0, 0, 0, 0)) : null;
  };

  // Tıklama olayını durdur
  const handleClick = (e) => {
    e.stopPropagation();
  };

  return (
    <div className="date-range-filter" onClick={handleClick}>
      <DatePicker
        selected={startDate}
        onChange={date => setFilter((old = []) => [resetTime(date), old[1]])}
        selectsStart
        startDate={startDate}
        endDate={endDate}
        dateFormat="dd.MM.yyyy"
        locale={tr}
        isClearable
        placeholderText="Başlangıç"
        className="date-range-filter__input"
        wrapperClassName="date-range-filter__wrapper"
        calendarClassName="date-range-filter__calendar"
        popperClassName="date-range-filter__popper"
      />
      <DatePicker
        selected={endDate}
        onChange={date => setFilter((old = []) => [old[0], resetTime(date)])}
        selectsEnd
        startDate={startDate}
        endDate={endDate}
        minDate={startDate}
        dateFormat="dd.MM.yyyy"
        locale={tr}
        isClearable
        placeholderText="Bitiş"
        className={`date-range-filter__input ${!startDate ? 'date-range-filter__input--disabled' : ''}`}
        wrapperClassName="date-range-filter__wrapper"
        calendarClassName="date-range-filter__calendar"
        popperClassName="date-range-filter__popper"
      />
    </div>
  );
};

export default DateRangeColumnFilter;