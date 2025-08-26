// path: frontend/src/components/NexusCore/index.js
import React, { useState, useEffect, useMemo } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

import useAuth from '../../auth/useAuth';
import authService from '../../auth/authService';

// Layout ve Diğer Bileşenler
import Header from './components/layout/Header/Header';
import Sidebar from './components/layout/Sidebar/Sidebar';
import PageWrapper from './components/layout/PageWrapper/PageWrapper';
import Spinner from './components/common/Spinner/Spinner';
import ConnectionManager from './containers/ConnectionManager';
import { NotificationProvider } from './contexts/NotificationContext';
import styles from './NexusCore.module.scss';

// ### YENİ: Gerçek Workspace bileşenimizi import ediyoruz ###
import VirtualTableWorkspace from './containers/VirtualTableWorkspace';

// ### KALDIRILDI: Artık bu geçici placeholder'a ihtiyacımız yok ###
// const VirtualTableWorkspace = () => ( ... );

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
    
    // Projeye özgü admin belirleme mantığı
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

  return (
    <NotificationProvider>
      <div className={styles.appContainer}>
        <Header user={{ name: user.email }} onLogout={logout} />
        <Sidebar isAdmin={isAdmin} />
        <PageWrapper>
          <Routes>
            {isAdmin && (
              <Route path="admin/connections" element={<ConnectionManager />} />
            )}
            
            <Route path="workspace" element={<VirtualTableWorkspace />} />
            
            <Route path="/" element={<Navigate replace to="workspace" />} />
            
            <Route path="*" element={<Navigate replace to="workspace" />} />
          </Routes>
        </PageWrapper>
      </div>
    </NotificationProvider>
  );
};

export default NexusCore;