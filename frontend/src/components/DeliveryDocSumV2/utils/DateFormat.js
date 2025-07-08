// frontend/src/components/DeliveryDocSumV2/utils/DateFormat.js
import { format, parseISO } from 'date-fns';

export const formatLastUpdated = (dateString) => {
  if (!dateString) return null;
  const parsedDate = parseISO(dateString);
  return format(parsedDate, 'yyyy-MM-dd');
};


