// frontend/src/components/DeliveryDocSumV2/utils/DynamicNameColumn.js
import React from 'react';
import { format, subDays, startOfMonth, startOfYear, subMonths, parseISO } from 'date-fns';

const getDynamicColumnNames = (dateString) => {
  if (!dateString) return {};

  const now = parseISO(dateString);

  return {
    today: `Bugün = ${format(now, 'dd.MM.yyyy')}`,
    yesterday: `Dün = ${format(subDays(now, 1), 'dd.MM.yyyy')}`,
    dayBeforeYesterday: `Önceki Gün = ${format(subDays(now, 2), 'dd.MM.yyyy')}`,
    threeDaysAgo: `Bugün - 3 Gün = ${format(subDays(now, 3), 'dd.MM.yyyy')}`,
    fourDaysAgo: `Bugün - 4 Gün = ${format(subDays(now, 4), 'dd.MM.yyyy')}`,
    thisMonth: `Bu Ay Toplam = ${format(startOfMonth(now), 'MM.yyyy')}`,
    lastMonth: `Bu Ay - 1 Toplam = ${format(startOfMonth(subMonths(now, 1)), 'MM.yyyy')}`,
    thisYear: `Yıllık Toplam = ${format(startOfYear(now), 'yyyy')}`
  };
};

const DynamicNameColumn = ({ dateString }) => {
  const columnNames = getDynamicColumnNames(dateString);

  return (
    <div>
      <p>{columnNames.today}</p>
      <p>{columnNames.yesterday}</p>
      <p>{columnNames.dayBeforeYesterday}</p>
      <p>{columnNames.threeDaysAgo}</p>
      <p>{columnNames.fourDaysAgo}</p>
      <p>{columnNames.thisMonth}</p>
      <p>{columnNames.lastMonth}</p>
      <p>{columnNames.thisYear}</p>
    </div>
  );
};

export { getDynamicColumnNames };
export default DynamicNameColumn;

