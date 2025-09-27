// frontend/src/App.js
import React from 'react';
import NotFound from './components/NotFound';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import AuthProvider from './auth/AuthProvider';
import Navbar from './components/NavBar/NavBar';
import Home from './components/Home/Home';
import LoginForm from './components/LoginForm/LoginForm';
import EduVideo from './components/EduVideo/containers/EduVideo';
import TotalRiskContainer from './components/TotalRisk/containers/TotalRiskContainer';
import ProductPictureContainer from './components/productpicture/containers/ProductPictureContainer';
import ActivitiesContainer from './components/Activities/containers/ActivitiesContainer';
import SalesOrderContainer from './components/salesorder/containers/SalesOrderContainer';
import SalesOrderDetailContainer from './components/SalesOrderDetail/Container/SalesOrderDetailContainer';
import CustomerSalesContainer from './components/CustomerSales/containers/CustomerSalesContainer';
import SupplierPaymentContainer from './components/SupplierPayment/containers/SupplierPaymentContainer';
import CustomerCollectionContainer from './components/CustomerCollection/containers/CustomerCollectionContainer';
import SalesBudgetContainer from './components/SalesBudget/containers/SalesBudgetContainer';
import SalesBudgetEURContainer from './components/SalesBudgetEur'; 
import SalesBudgetContainerv2 from './components/SalesBudgetv2/containers/SalesBudgetContainerv2';
import DocumentContainer from './components/DocArchiveV2/containers/DocumentContainer';
import DeliveryDocSumContainer from './components/DeliveryDocSum/containers/DeliveryDocSumContainer';
import DeliveryDocSumContainerV2 from './components/DeliveryDocSumV2/containers/DeliveryDocSumContainerV2';
import OpenOrderDocSumContainer from './components/OpenOrderDocSum/containers/OpenOrderDocSumContainer';
import OrderArchive from './components/orderarchive/containers/OrderArchiveContainer';
import SalesOrderDocSumContainer from './components/SalesOrderDocSum/containers/SalesOrderDocSumContainer';
import GirsbergerOrdrOpqtContainer from './components/GirsbergerOrdrOpqt/containers/GirsbergerOrdrOpqtContainer';
import LogoSupplierReceivablesAgingContainer from './components/LogoSupplierReceivablesAging/containers/LogoSupplierReceivablesAgingContainer';
import LogoCustomerBalanceContainer from './components/LogoCustomerBalance/containers/LogoCustomerBalanceContainer';
import LogoSupplierBalanceContainer from './components/LogoSupplierBalance/containers/LogoSupplierBalanceContainer';
import LogoCustomerCollectionContainer from './components/LogoCustomerCollection';
import DynamicReportContainer from './components/DynamicReport/containers/DynamicReportContainer';
import DynamicReportView from './components/DynamicReport/pages/DynamicReportView';
import SalesOfferDocSumContainer from './components/SalesOfferDocSum/containers/SalesOfferDocSumContainer';
import CrmBlogContainer from './components/CrmBlog/containers/CrmBlogContainer';
import RawMaterialWarehouseStockContainer from './components/RawMaterialWarehouseStock/containers/RawMaterialWarehouseStockContainer';
import FileShareHubContainer from './components/FileShareHub/containers/filesharehubcontainer';
import FileShareHubV2 from "./components/FileShareHub_V2";
import ShipWeekPlannerContainer from './components/ShipWeekPlanner/cotainers/ShipWeekPlannerContainer';
import ProductGroupDeliverySumContainer from './components/ProductGroupDeliverySum/containers/productgroupdeliverysumcontainer';
import SalesInvoiceSumContainer from './components/SalesInvoiceSum/containers/SalesInvoiceSumContainer';
import NewCustomerFormMain from './components/NewCustomerForm/containers/NewCustomerFormMain';
import EditCustomerForm from './components/NewCustomerForm/containers/EditCustomerForm';
import SystemNotebook from './components/SystemNotebook';

// hana stok kart entegrasyon
import { StockCardDashboard } from './components/StockCardIntegration';

// ProductConfig bileşenleri
import pcStore from './components/ProductConfig/store/pcStore';
import PCConfigurationPage from './components/ProductConfig/pages/PCConfigurationPage';
import PCVariantList from './components/ProductConfig/variant/PCVariantList';
import PCVariantDetails from './components/ProductConfig/variant/PCVariantDetails';

// BOM Cost Manager Bileşenleri
import BomCostTableContainer from './components/BomCostManager/containers/BomCostTableContainer';
import ProductListContainer from './components/BomCostManager/containers/ProductListContainer';
import VersionHistoryContainer from './components/BomCostManager/containers/VersionHistoryContainer';
import bomCostStore from './components/BomCostManager/redux/bomcoststore';

import { ProcureCompareContainer } from './components/ProcureCompare';


// Yeni ProductConfig V2 entegrasyonu
import { ProductConfigProvider } from './components/ProductConfigv2/contexts/ProductConfigContext';
import { RuleProvider } from './components/ProductConfigv2/contexts/RuleContext';
import ConfiguratorMain from './components/ProductConfigv2/components/Configurator/ConfiguratorMain';
import VariantProductListPage from './components/ProductConfigv2/pages/VariantProductListPage'; 
import VariantListPage from './components/ProductConfigv2/pages/VariantListPage'; 

// Tuna insaat importlari
import TunaInsTotalRiskContainer from './components/TunaInsTotalRisk/containers/TunaInsTotalRiskContainer';
import TunaInsSupplierPaymentContainer from './components/TunaInsSupplierPayment/containers/TunaInsSupplierPaymentContainer';
import TunaInsSupplierAdvanceBalanceContainer from './components/TunaInsSupplierAdvanceBalance/containers/TunaInsSupplierAdvanceBalanceContainer';

import CustomerSalesV2 from './components/CustomerSalesV2';

function App() {
  return (
    <>
      <ToastContainer />
      <AuthProvider>
        <Router>
          <Navbar />
          <Routes>
            {/* Ana uygulama rotaları */}
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<LoginForm />} />
            <Route path="/eduvideo" element={<EduVideo />} />
            <Route path="/totalrisk" element={<TotalRiskContainer />} />            
            <Route path="/productpictures" element={<ProductPictureContainer />} />
            <Route path="/activities" element={<ActivitiesContainer />} />
            <Route path="/salesorder" element={<SalesOrderContainer />} />
            <Route path="/salesorderdetail" element={<SalesOrderDetailContainer />} />
            <Route path="/customersales" element={<CustomerSalesContainer />} />
            <Route path="/supplierpayment" element={<SupplierPaymentContainer />} />
            <Route path="/customercollection" element={<CustomerCollectionContainer />} />
            <Route path="/salesbudget" element={<SalesBudgetContainer />} />
            <Route path="/salesbudgeteur" element={<SalesBudgetEURContainer />} />
            <Route path="/salesbudgetv2" element={<SalesBudgetContainerv2 />} />
            <Route path="/docarchivev2" element={<DocumentContainer />} />
            <Route path="/deliverydocsum" element={<DeliveryDocSumContainer />} />
            <Route path="/deliverydocsumv2" element={<DeliveryDocSumContainerV2 />} />
            <Route path="/openorderdocsum" element={<OpenOrderDocSumContainer />} />
            <Route path="/orderarchive" element={<OrderArchive />} />
            <Route path="/salesorderdocsum" element={<SalesOrderDocSumContainer />} />
            <Route path="/girsbergerordropqt" element={<GirsbergerOrdrOpqtContainer />} />
            <Route path="/logosupplierreceivablesging" element={<LogoSupplierReceivablesAgingContainer />} />
            <Route path="/logocustomerbalance" element={<LogoCustomerBalanceContainer />} />
            <Route path="/logosupplierbalance" element={<LogoSupplierBalanceContainer />} />
            <Route path="/logocustomercollection" element={<LogoCustomerCollectionContainer />} />
            <Route path="/dynamicreport" element={<DynamicReportContainer />} />
            <Route path="/dynamicreportview/:table_name" element={<DynamicReportView />} />
            <Route path="/salesofferdocsum" element={<SalesOfferDocSumContainer />} />
            <Route path="/crmblog" element={<CrmBlogContainer />} />
            <Route path="/rawmaterialstock" element={<RawMaterialWarehouseStockContainer />} />
            <Route path="/filesharehub" element={<FileShareHubContainer />} />
            <Route path="/filesharehub-v2" element={<FileShareHubV2 />} />
            <Route path="/shipweekplanner" element={<ShipWeekPlannerContainer />} />
            <Route path="/productgroupdeliverysum" element={<ProductGroupDeliverySumContainer />} />
            <Route path="/salesinvoicesum" element={<SalesInvoiceSumContainer />} />
            <Route path="/newcustomerform" element={<NewCustomerFormMain />} />
            <Route path="/newcustomerform/edit/:id" element={<EditCustomerForm />} />
            <Route path="/systemnotebook" element={<SystemNotebook />} />

            <Route path="/stockcards" element={<StockCardDashboard />} />

            <Route path="/customersalesv2" element={<CustomerSalesV2 />} />

            {/* BOM Cost Manager Rotaları */}
            <Route
              path="/bomcost/*"
              element={
                <Provider store={bomCostStore}>
                  <Routes>
                    <Route path="table/:itemCode" element={<BomCostTableContainer />} />
                    <Route path="products" element={<ProductListContainer />} />
                    <Route path="version-history" element={<VersionHistoryContainer />} />
                  </Routes>
                </Provider>
              }
            />

            {/* ProductConfig rotaları */}
            <Route
              path="/configurator/*"
              element={
                <Provider store={pcStore}>
                  <Routes>
                    <Route path="/" element={<PCConfigurationPage />} />
                    <Route path="edit/:variantId" element={<PCConfigurationPage />} />
                    <Route path="variants" element={<PCVariantList />} />
                    <Route path="variant/:variantId" element={<PCVariantDetails />} />
                  </Routes>
                </Provider>
              }
            />

            <Route path="/procurecompare" element={<ProcureCompareContainer />} />
            
            {/* Yeni ProductConfigV2 rotaları */}
          <Route
            path="/configurator-v2/*"
            element={
              <ProductConfigProvider>
                <RuleProvider>
                  <Routes>
                    <Route path="" element={<VariantProductListPage />} />
                    <Route path=":productId" element={<ConfiguratorMain />} />
                  </Routes>
                </RuleProvider>
              </ProductConfigProvider>
            }
          />   
          <Route path="/variants" element={<VariantListPage />}/>

            {/* Tuna Insaat rotaları */}  
            <Route path="/tunainstotalrisk" element={<TunaInsTotalRiskContainer />} />  
            <Route path="/tunainssupplierpayment" element={<TunaInsSupplierPaymentContainer />} />  
            <Route path="/tunainssupplieradvancebalance" element={<TunaInsSupplierAdvanceBalanceContainer />} />  

            {/* Fallback (NotFound yönlendirmesi) */}
            <Route path="*" element={<NotFound />} />

          </Routes>
        </Router>
      </AuthProvider>
    </>
  );
}

export default App;





