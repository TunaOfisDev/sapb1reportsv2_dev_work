
whitepaper api

api name `rawmaterialwarehousestock`
platform backend djago rest api ve frontend react
amac sap business one hana erp sisteminde hammadde depo H-01 envater bilgilerini ve verilen hammade satinalma siparislerin
takibi amaclanir. api bu amac icin hanadbcon api uzerinden `raw_material_warehouse_stock` adli sql sorgusunu hana db
ye gonderir ve gelen veri setini serilestirerek kullanaciya rest api uzerinden servis eder rapor mantik olarak
crud ile calisir eger stok verilerinde degisim varsa eski veri guncellenir ve kullanici raporu her actiginda guncel
veri ile islem yapmak zorundadir bu durumu backend tarafinda dikkatli bir sekilde ele almaliyiz

