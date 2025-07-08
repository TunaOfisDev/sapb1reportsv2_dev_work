// frontend/src/components/productpicture/utils/NumericSort.js
function NumericSort(rowA, rowB, columnId) {
    const cleanNumber = (value) => {
        // Eğer değer null veya undefined ise 0 döndür
        if (value === null || value === undefined) {
            return 0;
        }

        // Sayısal değere dönüştürmek için string'i temizle
        let cleanedNum = value.toString().replace(/[^\d,-]/g, ''); // Rakam, virgül ve negatif işaret hariç her şeyi sil
        cleanedNum = cleanedNum.replace(/,/g, '.'); // Virgül yerine nokta kullan
        return parseFloat(cleanedNum);
    };

    let a = cleanNumber(rowA.values[columnId]);
    let b = cleanNumber(rowB.values[columnId]);

    // Sayısal değerlere dönüştürme hatası kontrolü
    if (isNaN(a) || isNaN(b)) {
        return isNaN(a) ? 1 : -1;
    }

    // Normal sayısal karşılaştırma
    return a > b ? 1 : (a < b ? -1 : 0);
}

export default NumericSort;


