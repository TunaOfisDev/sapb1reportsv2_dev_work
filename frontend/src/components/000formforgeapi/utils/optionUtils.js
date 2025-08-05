// path: frontend/src/components/formforgeapi/utils/optionUtils.js
/**  Option yardımcıları – “Add option” bug-fix  */

export const addEmptyOption = (options = []) => [
  ...options,
  {
    id: `temp_${Date.now()}`,
    label: "",
    order: options.length,           // uzunluk var → yeni sıra
  },
];

export const updateOptionLabel = (options = [], optionId, newLabel) =>
  options.map((o) =>
    o.id === optionId ? { ...o, label: newLabel } : o
  );

export const deleteOption = (options = [], optionId) =>
  options.filter((o) => o.id !== optionId);
