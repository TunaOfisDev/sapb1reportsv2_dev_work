// path: frontend/src/components/NexusCore/components/layout/Header/Header.jsx
import React from 'react';
import PropTypes from 'prop-types';
import { LogOut, User } from 'react-feather';
import styles from './Header.module.scss';
// Logo'yu SVG olarak import etmek en iyi pratiktir.
// import { ReactComponent as NexusLogo } from '../../../assets/icons/nexus-logo.svg'; 

// Geçici bir Placeholder Logo
const PlaceholderLogo = () => (
  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2l-5.5 9h11L12 2zM2 15l9.5-5.5L21 15zM2 15v7h19v-7z" />
  </svg>
);


/**
 * Uygulamanın en üstünde yer alan, marka kimliğini ve kullanıcı menüsünü
 * içeren ana Header bileşeni.
 */
const Header = ({ user, onLogout }) => {
  return (
    <header className={styles.header}>
      <div className={styles.header__brand}>
        {/* <NexusLogo className={styles.brandLogo} /> */}
        <PlaceholderLogo />
        <h1 className={styles.brandTitle}>Nexus Core</h1>
      </div>

      {user && (
        <div className={styles.header__userMenu}>
          <div className={styles.userInfo}>
            <User size={18} className={styles.userIcon} />
            <span className={styles.userName}>{user.name || 'Kullanıcı'}</span>
          </div>
          <button className={styles.logoutButton} onClick={onLogout} title="Çıkış Yap">
            <LogOut size={20} />
          </button>
        </div>
      )}
    </header>
  );
};

Header.propTypes = {
  /** Oturum açmış kullanıcı bilgilerini içeren nesne. */
  user: PropTypes.shape({
    name: PropTypes.string,
    // email, avatarUrl etc.
  }),
  /** Çıkış yap butonuna tıklandığında tetiklenecek fonksiyon. */
  onLogout: PropTypes.func.isRequired,
};

export default Header;