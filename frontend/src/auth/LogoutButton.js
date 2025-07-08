// frontend/src/auth/LogoutButton.js
import React, { useContext, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AuthContext from './AuthContext';

const LogoutButton = () => {
  const authContext = useContext(AuthContext);
  const navigate = useNavigate();
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);

  const handleLogout = async () => {
    if (showConfirmDialog) {
      const redirectPath = await authContext.logout();
      navigate(redirectPath);
    } else {
      setShowConfirmDialog(true);
    }
  };

  return (
    <>
      <button onClick={handleLogout}>
        {showConfirmDialog ? 'Çıkış yapmak istediğinize emin misiniz?' : 'Çıkış Yap'}
      </button>
      {showConfirmDialog && (
        <button onClick={() => setShowConfirmDialog(false)}>İptal</button>
      )}
    </>
  );
};

export default LogoutButton;
