// frontend/src/components/SupplierPayment/utils/MonthlyBalances.js
import React from 'react';
import FormatNumber from './FormatNumber';

const monthNames = {
    "01": "Ocak",
    "02": "Şubat",
    "03": "Mart",
    "04": "Nisan",
    "05": "Mayıs",
    "06": "Haziran",
    "07": "Temmuz",
    "08": "Ağustos",
    "09": "Eylül",
    "10": "Ekim",
    "11": "Kasım",
    "12": "Aralık"
};

const MonthlyBalances = ({ monthlyBalances }) => {
    return (
        <div>
            {Object.entries(monthlyBalances).map(([month, balance]) => (
                <div key={month}>
                    {monthNames[month] || month}: <FormatNumber value={balance} />
                </div>
            ))}
        </div>
    );
};

export default MonthlyBalances;
