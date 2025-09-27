// frontend/src/components/Home/Home.js
import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import useAuth from '../../auth/useAuth';
import authService from '../../auth/authService';
import './Home.css';

function Home() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(true);
  const [departments, setDepartments] = useState([]);
  //const [positions, setPositions] = useState([]);

  useEffect(() => {
    async function fetchUserDepartmentsAndPositions() {
      const data = await authService.getUserDepartmentsAndPositions();
      if (data) {
        setDepartments(data.departments);
        //setPositions(data.positions);
      }
    }

    async function checkTokenValidity() {
      const userData = localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')) : null;
      if (userData && userData.access) {
        const isValid = await authService.validateToken(userData.access);
        if (!isValid) {
          authService.logout();
          navigate('/login');
        } else {
          setIsLoading(false);
          fetchUserDepartmentsAndPositions();
        }
      } else {
        navigate('/login');
      }
    }

    if (!isAuthenticated) {
      checkTokenValidity();
    } else {
      setIsLoading(false);
      fetchUserDepartmentsAndPositions();
    }
  }, [isAuthenticated, navigate]);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  const allowedDepartments = ['Export', 'Yurtici_Satis', 'Genel_Mudur', 'Yonetim', 'Bilgi_Sistem', 'Kurumsal'];
  const crmBlogOnlyDepartments = ['izmir_bayi'];
  const procureCompareDepartments = ['Yonetim', 'Genel_Mudur', 'Satinalma', 'Resepsiyon', 'Bilgi_Sistem'];
  const tunaInsDepartments = ['Yonetim', 'Genel_Mudur', 'Satinalma','Muhasebe', 'Resepsiyon', 'Bilgi_Sistem'];
  const salesOperationDepartments = ['Yurtici_Satis', 'Export', 'Bilgi_Sistem'];

  // ERİŞİM KISITLARI
  const supplierPaymentDepartments = [
    'Resepsiyon','Satinalma','Finans','Muhasebe','Planlama','Genel_Mudur','Yonetim','Bilgi_Sistem'
  ];

  const bomCostProductsDepartments = [
    'Sevkiyat_Planlama','Resepsiyon','Satinalma','Finans','Muhasebe','Planlama','Genel_Mudur','Yonetim','Bilgi_Sistem'
  ];

  return (
    <div className="Home">
      <header className="Home-header">
        <div className="Home-section">
          <h2 className="Home-section-title">CRM</h2>

          {crmBlogOnlyDepartments.some(department => departments.includes(department)) ? (
            <>
              <Link to="/crmblog" className="Home-link-button">Görev Listesi +</Link>
              <Link to="/filesharehub" className="Home-link-button">Görseller Klasörü</Link>
              <Link to="/filesharehub-v2" className="Home-link-button">Görseller Klasörü V2</Link>
            </>
          ) : (
            <>
              <Link to="/activities" className="Home-link-button">CRM Aktiviteleri</Link>
              <Link to="/salesofferdocsum" className="Home-link-button">Satis Teklifleri</Link>
              {allowedDepartments.some(department => departments.includes(department)) && (
                <Link to="/docarchivev2" className="Home-link-button">Önemli Dokümanlar</Link>
              )}
              <Link to="/crmblog" className="Home-link-button">Görev Listesi +</Link>
              <Link to="/filesharehub" className="Home-link-button">Görseller Klasörü</Link>
              <Link to="/filesharehub-v2" className="Home-link-button">Görseller Klasörü V2</Link>
            </>
          )}
        </div>

        {!crmBlogOnlyDepartments.some(department => departments.includes(department)) && (
          <>
            <div className="Home-section">
              <h2 className="Home-section-title">Müşteri</h2>
              <Link to="/totalrisk" className="Home-link-button">Müşteri Toplam Riski</Link>
              <Link to="/customercollection" className="Home-link-button">Müşteri Tahsilat Listesi</Link>
              <Link to="/deliverydocsum" className="Home-link-button">Sevkiyat Takip</Link>
              <Link to="/deliverydocsumv2" className="Home-link-button">Sevkiyat Takip V2</Link>
              <Link to="/productgroupdeliverysum" className="Home-link-button">Sevkiyat Ozet Aylik</Link>
            </div>

            <div className="Home-section">
              <h2 className="Home-section-title">Satis Siparişler</h2>
              <Link to="/salesbudgetv2" className="Home-link-button">Satis Butce (TL) 2025</Link>
              <Link to="/salesbudgeteur" className="Home-link-button">Satis Butce (Eur) 2025</Link>
              <Link to="/customersales" className="Home-link-button">Satis Siparis Aylik Ozet</Link>
              <Link to="/customersalesv2" className="Home-link-button">Satis Tipi Bazında Aylık (Eur)</Link>
              <Link to="/openorderdocsum" className="Home-link-button">Acik Siparis Ozeti Nakliye Montaj</Link>
            </div>

            {salesOperationDepartments.some(dep => departments.includes(dep)) && (
              <div className="Home-section">
                <h2 className="Home-section-title">Satış Operasyon</h2>
                <Link to="/stockcards" className="Home-link-button">Yeni Stok Kart Talebi</Link>
              </div>
            )}

            {supplierPaymentDepartments.some(dep => departments.includes(dep)) && (
              <div className="Home-section">
                <h2 className="Home-section-title">Tedarikci</h2>
                <Link to="/supplierpayment" className="Home-link-button">Tedarikci Odeme Listesi</Link>
              </div>
            )}

            <div className="Home-section">
              <h2 className="Home-section-title">Satis Siparis Kontrol</h2>
              <Link to="/salesorderdocsum" className="Home-link-button">Satis Siparis Belge Kontrol</Link>
              <Link to="/girsbergerordropqt" className="Home-link-button">Girsberger Satis Siparis to Satinalma Teklif</Link>
            </div>

            <div className="Home-section">
              <h2 className="Home-section-title">Uretim Planlama</h2>
              <Link to="/rawmaterialstock" className="Home-link-button">Hammadde Stok Durum</Link>
              <Link to="/shipweekplanner" className="Home-link-button">Haftalik Sevkiyat Plani</Link>
            </div>

            <div className="Home-section">
              <h2 className="Home-section-title">Urun Konfigurator</h2>
              <Link to="/configurator" className="Home-link-button">Urun Konfigurator</Link>
              <Link to="/configurator-v2" className="Home-link-button">Urun Konfigurator V2</Link>
            </div>

            <div className="Home-section">
              <h2 className="Home-section-title">Muhasebe</h2>
              <Link to="/salesinvoicesum" className="Home-link-button">Satis Fatura Ozet</Link>
              <Link to="/newcustomerform" className="Home-link-button">Yeni Müşteri Formu</Link>
            </div>

            {bomCostProductsDepartments.some(dep => departments.includes(dep)) && (
              <div className="Home-section">
                <h2 className="Home-section-title">Mamul Maliyet Analiz</h2>
                <Link to="/bomcost/products" className="Home-link-button">Ürün Listesi BOM</Link>
                {/* <Link to="/bomcost/version-history" className="Home-link-button">Versiyon Geçmişi</Link> */}
              </div>
            )}

            <div className="Home-section">
              <h2 className="Home-section-title">Arsiv</h2>
              <Link to="/orderarchive" className="Home-link-button">Uyumsoft Siparis Detay 2005-2023</Link>
              <Link to="/salesbudget" className="Home-link-button">Sap Satis Butce 2024</Link>
            </div>

            {procureCompareDepartments.some(dep => departments.includes(dep)) && (
              <div className="Home-section">
                <h2 className="Home-section-title">Satın Alma</h2>
                <Link to="/procurecompare" className="Home-link-button">Satınalma Fiyat Karşılaştırma</Link>
              </div>
            )}

            <div className="Home-section">
              <h2 className="Home-section-title">Pasif Raporlar</h2>
              <Link to="/dynamicreportview/satis_siparisleri_ilk_teslimat_sureleri_rapor" className="Home-link-button">
                Satış Siparişleri İlk Teslimat Süreleri Rapor
              </Link>
              <Link to="/dynamicreportview/satis_siparis_musteri_bazinda_aylik_yillik_eur" className="Home-link-button">
                Satis Siparis Müşteri Bazında Aylık Yıllık Eur
              </Link>
              <Link to="/dynamicreportview/satis_siparis_nakliye_montaj_cari_bazinda_aylik_rapor" className="Home-link-button">
                Satış Sipariş Nakliye Montaj Cari Bazında Aylık Rapor
              </Link>
            </div>

            {tunaInsDepartments.some(dep => departments.includes(dep)) && (
              <div className="Home-section">
                <h2 className="Home-section-title">Tuna Ins</h2>
                <Link to="/tunainstotalrisk" className="Home-link-button">Müşteri Bakiye</Link>
                <Link to="/tunainssupplierpayment" className="Home-link-button">Tedarikci Bakiye</Link>
                <Link to="/tunainssupplieradvancebalance" className="Home-link-button">Tedarikci Avans Bakiye</Link>
              </div>
            )}

            {departments.includes('Sofitel') && (
              <div className="Home-section">
                <h2 className="Home-section-title">Sofitel</h2>
                <Link to="/logocustomerbalance" className="Home-link-button">Musteri Bakiye Listesi</Link>
                <Link to="/logocustomercollection" className="Home-link-button">Musteri Tahsilat Listesi</Link>
                <Link to="/logosupplierbalance" className="Home-link-button">Tedarikci Bakiye Listesi</Link>
                <Link to="/logosupplierreceivablesging" className="Home-link-button">Tedarikci Odeme Listesi</Link>
              </div>
            )}
          </>
        )}
      </header>
      <footer className="Home-footer">
        @Tuna Ofis A.Ş. 2024 - Hana Rapor Uygulaması, Tuna Ofis A.Ş. IT departmanı tarafından ChatGPT teknolojisi kullanılarak geliştirilmiştir. Tüm hakları saklıdır.
      </footer>
    </div>
  );
}

export default Home;
