// path: frontend/src/components/NexusCore/components/layout/Sidebar/Sidebar.jsx
import React from 'react';
import PropTypes from 'prop-types';
import { NavLink } from 'react-router-dom';
// ### YENİ: İlişkisel modeli temsil etmesi için GitMerge ikonunu ekliyoruz ###
import { Database, Grid, BookOpen, GitMerge } from 'react-feather';
import styles from './Sidebar.module.scss';

const Sidebar = ({ isAdmin = false }) => {
  const getNavLinkClass = ({ isActive }) =>
    isActive ? `${styles.navLink} ${styles.navLinkActive}` : styles.navLink;

  return (
    <aside className={styles.sidebar}>
      <nav className={styles.nav}>
        <ul className={styles.navList}>
          <li className={styles.navItem}>
            <NavLink to="workspace" className={getNavLinkClass}>
              <Grid size={20} className={styles.navIcon} />
              <span className={styles.navText}>Çalışma Alanı</span>
            </NavLink>
          </li>

          {/* ### YENİ: VERİ MODELLERİ LİNKİ EKLENDİ ### */}
          {/* Bu, bizim yeni DataAppWorkspace konteynerimize yönlendirecek. */}
          <li className={styles.navItem}>
            <NavLink to="data-apps" className={getNavLinkClass}>
              <GitMerge size={20} className={styles.navIcon} />
              <span className={styles.navText}>Veri Modelleri</span>
            </NavLink>
          </li>
          {/* ### YENİ LİNK SONU ### */}

          <li className={styles.navItem}>
            <NavLink to="reports" className={getNavLinkClass}>
              <BookOpen size={20} className={styles.navIcon} />
              <span className={styles.navText}>Raporlarım</span>
            </NavLink>
          </li>
                  
          {isAdmin && (
            <li className={styles.navItem}>
              <NavLink to="admin/connections" className={getNavLinkClass}>
                <Database size={20} className={styles.navIcon} />
                <span className={styles.navText}>Veri Kaynakları</span>
              </NavLink>
            </li>
          )}
        </ul>
      </nav>
    </aside>
  );
};

Sidebar.propTypes = {
  isAdmin: PropTypes.bool,
};

export default Sidebar;