// path: frontend/src/components/NexusCore/components/layout/Sidebar/Sidebar.jsx
import React from 'react';
import PropTypes from 'prop-types';
import { NavLink } from 'react-router-dom';
import { Database, Grid } from 'react-feather'; // İkonlarımızı import ediyoruz
import styles from './Sidebar.module.scss';

/**
 * Uygulamanın sol tarafında yer alan, ana sayfalara navigasyon sağlayan Sidebar bileşeni.
 * Kullanıcı rolüne göre farklı linkler gösterebilir.
 */
const Sidebar = ({ isAdmin = false }) => {
  // Aktif link stilini yönetmek için bir fonksiyon. NavLink'in className prop'u bunu destekler.
  const getNavLinkClass = ({ isActive }) =>
    isActive ? `${styles.navLink} ${styles.navLinkActive}` : styles.navLink;

  return (
    <aside className={styles.sidebar}>
      <nav className={styles.nav}>
        <ul className={styles.navList}>
          <li className={styles.navItem}>
            <NavLink to="/workspace" className={getNavLinkClass}>
              <Grid size={20} className={styles.navIcon} />
              <span className={styles.navText}>Çalışma Alanı</span>
            </NavLink>
          </li>
          
          {/* Sadece admin rolündeki kullanıcılar bu linki görebilir */}
          {isAdmin && (
            <li className={styles.navItem}>
              <NavLink to="/admin/connections" className={getNavLinkClass}>
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
  /** Kullanıcının admin olup olmadığını belirtir, admin menüsünü kontrol eder. */
  isAdmin: PropTypes.bool,
};

export default Sidebar;