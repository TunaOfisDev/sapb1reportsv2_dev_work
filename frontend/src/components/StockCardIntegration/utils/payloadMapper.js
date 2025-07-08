// path: frontend/src/components/StockCardIntegration/utils/payloadMapper.js

export const mapToSapPayload = (formData) => ({
  ItemCode: formData.itemCode,
  ItemName: formData.itemName,
  ItemsGroupCode: Number(formData.ItemsGroupCode),
  SalesVATGroup: formData.SalesVATGroup,
  PurchaseVATGroup: formData.SalesVATGroup,
  PurchaseItem: 'tNO',
  SalesItem: 'tYES',
  InventoryItem: 'tYES',
  ManageSerialNumbersOnReleaseOnly: 'tNO',
  SalesUnit: formData.UoMGroupEntry,
  PurchaseUnit: formData.UoMGroupEntry,
  DefaultWarehouse: 'M-01',
  InventoryUOM: formData.UoMGroupEntry,
  PlanningSystem: 'M',
  ProcurementMethod: 'M',
  UoMGroupEntry: 1,
  InventoryUoMEntry: 1,
  DefaultSalesUoMEntry: 1,
  DefaultPurchasingUoMEntry: 1,
  U_eski_bilesen_kod: formData.U_eski_bilesen_kod,
  ItemPrices: [
    {
      PriceList: 1,
      BasePriceList: 1,
      Factor: 1,
      Price: Number(formData.Price),
      Currency: formData.Currency
    }
  ]
});
