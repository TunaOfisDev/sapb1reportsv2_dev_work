// frontend/src/components/DynamicReport/utils/utils.js

export const mergeDataWithHeaders = (manualHeaders, tableDetails, dynamicTable) => {
    if (manualHeaders.length === 0 || !tableDetails) {
        return dynamicTable;
    }
    const columns = manualHeaders.map((header) => header);
    const rows = tableDetails.hana_data_set.map((dataRow) => dataRow);
    return {
        columns,
        rows,
    };
    };

    export const handleFetchData = async (triggerFetchData, addNotification) => {
    try {
        await triggerFetchData();
        addNotification('Veri çekme işlemi başlatıldı.', 'info');
        addNotification('Veriler başarıyla çekildi.', 'success');
    } catch (error) {
        addNotification('Veriler çekilemedi.', 'error');
    }
    };
