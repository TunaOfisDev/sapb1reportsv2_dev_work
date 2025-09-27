// frontend/src/components/SalesInvoiceSum/utils/DynamicNameColumn.js
import React, { useMemo } from 'react';
import { format, subDays, startOfMonth, startOfYear, subMonths, parseISO, isValid } from 'date-fns';
import PropTypes from 'prop-types';

const getDynamicColumnNames = (dateString) => {
  if (!dateString) return {};

  const now = parseISO(dateString);
  if (!isValid(now)) {
    console.error('Invalid dateString provided to getDynamicColumnNames');
    return {};
  }

  return {
    today: `Bugün = ${format(now, 'dd.MM.yyyy')}`,
    yesterday: `Dün = ${format(subDays(now, 1), 'dd.MM.yyyy')}`,
    dayBeforeYesterday: `Önceki Gün = ${format(subDays(now, 2), 'dd.MM.yyyy')}`,
    threeDaysAgo: `Bugün-3Gün = ${format(subDays(now, 3), 'dd.MM.yyyy')}`,
    fourDaysAgo: `Bugün-4Gün = ${format(subDays(now, 4), 'dd.MM.yyyy')}`,
    thisMonth: `Bu Ay = ${format(startOfMonth(now), 'MM.yyyy')}`,
    lastMonth: `Geçen Ay = ${format(startOfMonth(subMonths(now, 1)), 'MM.yyyy')}`,
    thisYear: `Yıllık = ${format(startOfYear(now), 'yyyy')}`
  };
};

const DynamicNameColumn = ({ dateString }) => {
  const columnNames = useMemo(() => getDynamicColumnNames(dateString), [dateString]);

  if (!Object.keys(columnNames).length) {
    return <p>Geçerli bir tarih sağlanmadı veya tarih formatı hatalı.</p>;
  }

  return (
    <ul>
      {Object.entries(columnNames).map(([key, value]) => (
        <li key={key} className={`dynamic-name-column__${key}`}>
          {value}
        </li>
      ))}
    </ul>
  );
};

DynamicNameColumn.propTypes = {
  dateString: PropTypes.string.isRequired
};

export { getDynamicColumnNames };
export default DynamicNameColumn;
