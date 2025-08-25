// path: frontend/src/components/NexusCore/index.js
import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

// Layout Bileşenleri
import Header from './components/layout/Header/Header';
import Sidebar from './components/layout/Sidebar/Sidebar';
import PageWrapper from './components/layout/PageWrapper/PageWrapper';

// Container/Sayfa Bileşenleri
import ConnectionManager from './containers/ConnectionManager';

// Context Provider'lar
import { NotificationProvider } from './contexts/NotificationContext';

// Ana uygulama stil dosyası
import styles from './NexusCore.module.scss';


// VirtualTableWorkspace henüz oluşturulmadığı için geçici bir placeholder oluşturalım.
const VirtualTableWorkspace = () => (
  <div>
    <h2>Kullanıcı Çalışma Alanı (VirtualTableWorkspace)</h2>
    <p>Bu alan yakında inşa edilecek.</p>
  </div>
);


/**
 * Nexus Core uygulamasının ana bileşeni.
 * Tüm layout, routing ve context'leri bir araya getirir.
 */
const NexusCore = () => {
  // Gerçek bir uygulamada bu bilgi bir kimlik doğrulama (authentication)
  // servisinden gelecektir. Şimdilik simüle ediyoruz.
  const [user, setUser] = useState({
    name: 'Selim',
    isAdmin: true, // Rol bazlı menü ve route'ları test etmek için
  });

  const handleLogout = () => {
    alert('Çıkış yapma fonksiyonu buraya gelecek.');
    setUser(null);
  };

  // Eğer kullanıcı yoksa (çıkış yapmışsa), bir login ekranı gösterilebilir.
  if (!user) {
    return <div><h1>Giriş Ekranı</h1><button onClick={() => setUser({ name: 'Selim', isAdmin: true })}>Giriş Yap (Simülasyon)</button></div>;
  }

  return (
    <NotificationProvider>
      <Router>
        <div className={styles.appContainer}>
          <Header user={user} onLogout={handleLogout} />
          <Sidebar isAdmin={user.isAdmin} />
          <PageWrapper>
            <Routes>
              {/* Admin'e özel, korumalı route (rota) */}
              {user.isAdmin && (
                <Route path="/admin/connections" element={<ConnectionManager />} />
              )}
              
              {/* Standart kullanıcıların ve adminlerin erişebileceği ana sayfa */}
              <Route path="/workspace" element={<VirtualTableWorkspace />} />
              
              {/* Kök dizine gelindiğinde /workspace'e yönlendir */}
              <Route path="/" element={<Navigate replace to="/workspace" />} />
              
              {/* Tanımlanmayan bir yola gidilirse ana sayfaya yönlendir */}
              <Route path="*" element={<Navigate replace to="/workspace" />} />
            </Routes>
          </PageWrapper>
        </div>
      </Router>
    </NotificationProvider>
  );
};

export default NexusCore;