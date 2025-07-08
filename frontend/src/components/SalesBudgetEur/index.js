// frontend/src/components/SalesBudgetEur/index.js
// -------------------------------------------------------------------
// Barrel file – SalesBudgetEUR module
// Exporting primary container, table, hook and API helpers for easy import.
// -------------------------------------------------------------------

export { default as SalesBudgetEURContainer } from "./container/salesbudgeteurContainer";
export { default as SalesBudgetEURTable } from "./container/salesbudgeteurTable";
export { default as useSalesBudgetEUR } from "./hooks/Usesalesbudgeteur";
export * as salesBudgetEURApi from "./api/salesbudgeteurApi";

// Quick default export (container)
export { default } from "./container/salesbudgeteurContainer";
