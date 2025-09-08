// path: frontend/src/components/NexusCore/index.js
import React, { useState, useEffect, useMemo } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

import useAuth from '../../auth/useAuth';
import authService from '../../auth/authService';

// Layout ve Sayfa Bileşenleri
import Header from './components/layout/Header/Header';
import Sidebar from './components/layout/Sidebar/Sidebar';
import PageWrapper from './components/layout/PageWrapper/PageWrapper';
import Spinner from './components/common/Spinner/Spinner';
import ConnectionManager from './containers/ConnectionManager';
import VirtualTableWorkspace from './containers/VirtualTableWorkspace';
import ReportViewer from './containers/ReportViewer';
import ReportPlayground from './containers/ReportPlayground';
import { NotificationProvider } from './contexts/NotificationContext';
import styles from './NexusCore.module.scss';

const NexusCore = () => {
  const { user, logout, loading: authLoading, isAuthenticated } = useAuth();
  
  const [permissions, setPermissions] = useState(null);
  const [permissionsLoading, setPermissionsLoading] = useState(true);

  useEffect(() => {
    const fetchPermissions = async () => {
      if (isAuthenticated) {
        try {
          const perms = await authService.getUserDepartmentsAndPositions();
          setPermissions(perms || { departments: [], positions: [] });
        } catch (error) {
          console.error("Kullanıcı yetkileri alınırken hata oluştu:", error);
          setPermissions({ departments: [], positions: [] });
        } finally {
          setPermissionsLoading(false);
        }
      } else {
        setPermissionsLoading(false);
      }
    };

    if (!authLoading) {
      fetchPermissions();
    }
  }, [isAuthenticated, authLoading]);

  const isAdmin = useMemo(() => {
    if (!permissions) return false;
    const hasAdminPosition = permissions.positions?.some(pos => pos.toLowerCase().includes('admin'));
    const isInITDepartment = permissions.departments?.some(dep => dep.toLowerCase().includes('it'));
    return hasAdminPosition || isInITDepartment;
  }, [permissions]);

  if (authLoading || permissionsLoading) {
    return <Spinner size="lg" />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // NexusCore modülünün tamamı NotificationProvider ile sarmalanır.
  return (
    <NotificationProvider>
      <div className={styles.appContainer}>
        <Header user={{ name: user.email }} onLogout={logout} />
        <Sidebar isAdmin={isAdmin} />
        <PageWrapper>
          {/* Burası NexusCore modülünün iç yönlendiricisidir */}
          <Routes>
            {/* Admin'e özel rota */}
            {isAdmin && (
              <Route path="admin/connections" element={<ConnectionManager />} />
            )}
            
            {/* Tüm kullanıcılar için rotalar */}
            <Route path="workspace" element={<VirtualTableWorkspace />} />
            <Route path="reports" element={<ReportViewer />} />
            
            {/* --- ROTA GÜNCELLEMESİ BURADA --- */}
            
            {/* 1. YENİ RAPOR OLUŞTURMA ROTASI: */}
            {/* (Örn: /nexus/playground/new/1) */}
            {/* ReportPlayground'u :virtualTableId ile "Yeni" modda açar */}
            <Route 
                path="playground/new/:virtualTableId" 
                element={<ReportPlayground />} 
            />
            
            {/* 2. RAPOR DÜZENLEME ROTASI: */}
            {/* (Örn: /nexus/playground/edit/46) */}
            {/* ReportPlayground'u :reportId ile "Düzeltme" modunda açar */}
            <Route 
                path="playground/edit/:reportId" 
                element={<ReportPlayground />} 
            />
            
            {/* Hatalı olan eski rota (Bunu silebilir veya fallback olarak bırakabiliriz ama en temizi ikili sistemdir) */}
            {/* <Route path="playground/:virtualTableId" element={<ReportPlayground />} /> */}
            
            {/* Varsayılan ve bulunamayan yollar için yönlendirmeler */}
            {/* /nexus/ için varsayılan sayfa workspace olsun */}
            <Route path="/" element={<Navigate replace to="workspace" />} /> 
            <Route path="*" element={<Navigate replace to="workspace" />} />
          </Routes>
        </PageWrapper>
      </div>
    </NotificationProvider>
  );
};

export default NexusCore;