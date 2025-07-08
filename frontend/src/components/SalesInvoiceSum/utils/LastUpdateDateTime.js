// frontend/src/components/DeliveryDocSum/utils/LastUpdateDateTime.js
import React, { useEffect } from 'react';
import moment from 'moment';
import useSalesInvoiceSum from '../hooks/useSalesInvoiceSum';

const LastUpdateDateTime = () => {
    const { lastUpdated, loadLocalData } = useSalesInvoiceSum();

    useEffect(() => {
        loadLocalData(); // You might not need this if the parent component already calls it
    }, [loadLocalData]);

    return (
        <span>{lastUpdated ? moment(lastUpdated).format('DD.MM.YYYY HH:mm') : 'Loading...'}</span>
    );
};

export default LastUpdateDateTime;

