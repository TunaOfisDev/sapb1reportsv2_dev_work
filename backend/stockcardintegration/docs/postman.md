
coklu stok karti olusturmak
http://192.168.2.201/api/v2/stockcardintegration/stock-cards/bulk-create/
[
  {
    "item_code": "40.PRS.BWTW110.M1.TEST130",
    "item_name": "TEST124 BEEWORK DAİRE 3 AYAKLI TOPLANTI MASASI",
    "items_group_code": 105,
    "price": 6745.69,
    "currency": "TRY"
  },
  {
    "item_code": "40.PRS.BWTW110.M1.TEST131",
    "item_name": "TEST125 BEEWORK DAİRE 3 AYAKLI TOPLANTI MASASI",
    "items_group_code": 112,
    "price": 2485.59,
    "currency": "EUR"
  },
    {
    "item_code": "40.PRS.BWTW110.M1.TEST132",
    "item_name": "TEST125 BEEWORK DAİRE 3 AYAKLI TOPLANTI MASASI",
    "items_group_code": 103,
    "price": 1500.50,
    "currency": "EUR"
  }
]

**********************

TEKLI YENI STOK KARTI OLUSTURMA
http://192.168.2.201/api/v2/stockcardintegration/stock-cards/bulk-create/

[{
  "item_code": "40.PRS.BWTW110.M1.TEST139",
  "item_name": "TEST130-NEWCREATE-test BEEWORK DAİRE 3 AYAKLI TOPLANTI MASASI",
  "items_group_code": 112,
  "price": 777.77,
  "currency": "EUR"
}
]

*********************



STOK KARTI GUNCELLEME
http://192.168.2.201/api/v2/stockcardintegration/stock-cards/code/40.PRS.BWTW110.M1.TEST130/

{
  "item_code": "40.PRS.BWTW110.M1.TEST130",
  "item_name": "TEST130-put04-test BEEWORK DAİRE 3 AYAKLI TOPLANTI MASASI",
  "items_group_code": 105,
  "price": 777.77,
  "currency": "EUR"
}


***********
{
  "item_code": "40.PRS.BWTW110.M1.TEST122",
  "item_name": "TEST118 BEEWORK DAİRE 3 AYAKLI TOPLANTI MASASI - MYL MASA TABLA+ALU FLAP KAPAK - E.S BOYALI AYAK - KABLO TAVASI+TRAVERS - MASA Q110 H75CM",
  "items_group_code": 105,
  "price": 696.69,
  "currency": "EUR",
  "extra_data": {
    "ItemType": "itItems",
    "SalesVATGroup": "HES0010",
    "PurchaseVATGroup": "İND010",
    "PurchaseItem": "tNO",
    "SalesItem": "tYES",
    "InventoryItem": "tYES",
    "ManageSerialNumbersOnReleaseOnly": "tNO",
    "SalesUnit": "Ad",
    "PurchaseUnit": "Ad",
    "DefaultWarehouse": "M-01",
    "InventoryUOM": "Ad",
    "PlanningSystem": "M",
    "ProcurementMethod": "M",
    "UoMGroupEntry": 1,
    "InventoryUoMEntry": 1,
    "DefaultSalesUoMEntry": 1,
    "DefaultPurchasingUoMEntry": 1
  }
}