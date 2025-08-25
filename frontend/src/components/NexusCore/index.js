// path: frontend/src/components/NexusCore/index.js
import React, { useState, useEffect, useMemo } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

import useAuth from '../../auth/useAuth';
import authService from '../../auth/authService'; // Yetki kontrolü için servisi import ediyoruz

// Layout ve Diğer Bileşenler
import Header from './components/layout/Header/Header';
import Sidebar from './components/layout/Sidebar/Sidebar';
import PageWrapper from './components/layout/PageWrapper/PageWrapper';
import Spinner from './components/common/Spinner/Spinner';
import ConnectionManager from './containers/ConnectionManager';
import { NotificationProvider } from './contexts/NotificationContext';
import styles from './NexusCore.module.scss';

const VirtualTableWorkspace = () => (
  <div>
    <h2>Kullanıcı Çalışma Alanı (VirtualTableWorkspace)</h2>
    <p>Bu alan yakında inşa edilecek.</p>
  </div>
);

const NexusCore = () => {
  const { user, logout, loading: authLoading, isAuthenticated } = useAuth();
  
  // Kullanıcının departman/pozisyon gibi yetki bilgilerini tutacak state
  const [permissions, setPermissions] = useState(null);
  const [permissionsLoading, setPermissionsLoading] = useState(true);

  // Auth bilgisi yüklendikten sonra, kullanıcının yetkilerini backend'den çek
  useEffect(() => {
    const fetchPermissions = async () => {
      if (isAuthenticated) {
        try {
          const perms = await authService.getUserDepartmentsAndPositions();
          setPermissions(perms || { departments: [], positions: [] });
        } catch (error) {
          console.error("Kullanıcı yetkileri alınırken hata oluştu:", error);
          setPermissions({ departments: [], positions: [] }); // Hata durumunda boş yetki ata
        } finally {
          setPermissionsLoading(false);
        }
      } else {
        setPermissionsLoading(false); // Giriş yapmamışsa, yetki yüklemesi de bitmiştir.
      }
    };

    // Sadece ana kimlik doğrulama yüklemesi bittiyse yetkileri çek
    if (!authLoading) {
      fetchPermissions();
    }
  }, [isAuthenticated, authLoading]); // authLoading durumu değiştiğinde tetiklenir

  // Admin yetkisini, gelen yetki verisine göre HESAPLA.
  // useMemo, permissions değişmediği sürece bu hesabın tekrar yapılmasını engeller.
  const isAdmin = useMemo(() => {
    if (!permissions) return false;
    
    // --- BURASI İŞ MANTIĞININ TANIMLANDIĞI YER ---
    // Kural: Pozisyonları içinde 'Admin' VEYA Departmanları içinde 'IT' olanlar admin sayılır.
    // Bu kuralları kendi sistemine göre güncelleyebilirsin.
    const hasAdminPosition = permissions.positions?.some(pos => pos.toLowerCase().includes('admin'));
    const isInITDepartment = permissions.departments?.some(dep => dep.toLowerCase().includes('it'));
    
    return hasAdminPosition || isInITDepartment;
  }, [permissions]);

  // Hem ilk kimlik doğrulama hem de yetki kontrolü yüklemesi bitene kadar bekle
  if (authLoading || permissionsLoading) {
    return <Spinner size="lg" />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <NotificationProvider>
      <div className={styles.appContainer}>
        <Header user={{ name: user.email }} onLogout={logout} />
        <Sidebar isAdmin={isAdmin} />
        <PageWrapper>
          <Routes>
            {isAdmin && (
              // ### DEĞİŞİKLİK: Baştaki '/' kaldırıldı ###
              <Route path="admin/connections" element={<ConnectionManager />} />
            )}
            
            {/* ### DEĞİŞİKLİK: Baştaki '/' kaldırıldı ### */}
            <Route path="workspace" element={<VirtualTableWorkspace />} />
            
            {/* ### DEĞİŞİKLİK: Baştaki '/' kaldırıldı ### */}
            {/* Bu kural artık /nexus'a gelindiğinde /nexus/workspace'e yönlendirir */}
            <Route path="/" element={<Navigate replace to="workspace" />} />
            
            {/* ### DEĞİŞİKLİK: Baştaki '/' kaldırıldı ### */}
            <Route path="*" element={<Navigate replace to="workspace" />} />
          </Routes>
        </PageWrapper>
      </div>
    </NotificationProvider>
  );
};

export default NexusCore;