// path: frontend/src/components/StockCardIntegration/utils/multiTermTextFilter.js
export const multiTermTextFilter = (rows, id, filterValue) => {
  if (!filterValue) return rows;

  // Kullanıcının girdiği değerleri parçala → '235 186' ⇒ ['235','186']
  const terms = filterValue
    .trim()
    .toLocaleLowerCase('tr-TR')
    .split(/\s+/);

  return rows.filter((row) => {
    const rowText = String(row.values[id] ?? '')
      .toLocaleLowerCase('tr-TR');

    // Her terim satırda geçiyor mu?
    return terms.every((t) => rowText.includes(t));
  });
};

// Boş string geldiğinde filtreyi otomatik kaldır
multiTermTextFilter.autoRemove = (val) => !val;
