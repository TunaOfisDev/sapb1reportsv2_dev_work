// frontend/src/components/NavBar/NavBar.js
import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import useAuth from '../../auth/useAuth';
import authService from '../../auth/authService';
import './NavBar.css';

function Navbar() {
  const navigate = useNavigate();
  const { isAuthenticated, logout } = useAuth();
  const [departments, setDepartments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function fetchUserDepartmentsAndPositions() {
      const data = await authService.getUserDepartmentsAndPositions();
      if (data) {
        setDepartments(data.departments);
      }
      setIsLoading(false);
    }

    if (isAuthenticated) {
      fetchUserDepartmentsAndPositions();
    } else {
      setIsLoading(false);
    }
  }, [isAuthenticated]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const userEmail = authService.getUserEmail();
  const username = userEmail ? userEmail.split('@')[0] : '';

  if (isLoading) {
    return <div>Loading...</div>;
  }

  const crmBlogOnlyDepartments = ['izmir_bayi'];

  return (
    <div className="global-navbar">
      <Link className="global-navbar__item" to="/">Anasayfa</Link>
  
      {/* Eğer kullanıcı izmir_bayi departmanında değilse Dynamic Reports linki gösterilir */}
      {isAuthenticated && !crmBlogOnlyDepartments.some(department => departments.includes(department)) && (
        <Link className="global-navbar__item" to="/dynamicreport">Dynamic Reports</Link>
      )}
  
      {/* Eğer kullanıcı izmir_bayi departmanında değilse Eğitim linki gösterilir */}
      {!crmBlogOnlyDepartments.some(department => departments.includes(department)) && (
        <Link className="global-navbar__item" to="/eduvideo">Eğitim</Link>
      )}
  
      {departments.includes('Bilgi_Sistem') && (
        <div className="global-navbar__dropdown">
          <span>API Doc</span>
          <div className="dropdown-content">
            <a href="http://10.130.212.112/admin/" target="_blank" rel="noopener noreferrer">Admin</a>
            <a href="http://10.130.212.112/api/schema/swagger-ui/" target="_blank" rel="noopener noreferrer">Swagger</a>
            <a href="http://10.130.212.112/api/schema/redoc/" target="_blank" rel="noopener noreferrer">ReDoc</a>
          </div>
        </div>
      )}
  
     <div className="right-menu">
        {isAuthenticated && (
          <>
            <span className="global-navbar__welcome-message">{username} Hoşgeldiniz!</span>
            <span className="global-navbar__separator">|</span>
            <Link
              to="/systemnotebook"
              className="global-navbar__item"
              style={{ fontWeight: 'bold', color: '#ffc107' }}
            >
              Sistem Notları
            </Link>
            <span className="global-navbar__separator">|</span>
          </>
        )}
        <span className="global-navbar__version">V2-290825Usrv</span>
        <span className="global-navbar__separator">|</span>
        {isAuthenticated ? (
          <button className="global-navbar__button" onClick={handleLogout}>Logout</button>
        ) : (
          <button className="global-navbar__button" onClick={() => navigate('/login')}>Login</button>
        )}
      </div>


    </div>
  );
  
}

export default Navbar;
