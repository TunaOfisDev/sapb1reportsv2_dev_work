// frontend/src/components/Activities/containers/ActivitiesContainer.js
import React, { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import useAuth from '../../../auth/useAuth';
import useActivities from '../hooks/useActivities';
import ActivitiesTable from './ActivitiesTable';
import CalendarView from '../views/CalendarView';
import '../css/ActivitiesContainer.css';

const ActivitiesContainer = () => {
  const { isAuthenticated, loading: authLoading } = useAuth(); // GÜNCELLENDİ
  const {
    localActivities,
    instantActivities,
    isLoading,
    error,
    fetchLocalActivities,
    fetchInstantActivities,
  } = useActivities();
  const [showCalendar, setShowCalendar] = useState(false);

  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      fetchLocalActivities();
    }
  }, [isAuthenticated, authLoading, fetchLocalActivities]); // GÜNCELLENDİ

  // Eğer auth durumu hâlâ yükleniyorsa (örn. token validate ediliyor)
  if (authLoading) {
    return <p>Kimlik doğrulama kontrol ediliyor...</p>;
  }

  // Kimlik doğrulama başarısızsa login'e yönlendir
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (isLoading) return <p>Veriler yükleniyor...</p>;
  if (error) return <p>Aktiviteler yüklenemedi: {error.message || error.toString()}</p>;

  const toggleCalendar = () => setShowCalendar(!showCalendar);

  return (
    <div className="activities-container">
      <div className="activities-container__header">
        <h1 className="activities-container__title">Crm Activities</h1>
        <div className="activities-container__button-wrapper">
          <button onClick={fetchLocalActivities} className="activities-container__button">
            Yerel Veri Çek
          </button>
          <button onClick={fetchInstantActivities} className="activities-container__button">
            HANA Anlık Veri Çek
          </button>
          <button onClick={toggleCalendar} className="activities-container__button">
            {showCalendar ? 'Hide Calendar' : 'Show Calendar'}
          </button>
        </div>
      </div>
      {showCalendar
        ? <CalendarView />
        : <ActivitiesTable activities={localActivities.length > 0 ? localActivities : instantActivities} />}
    </div>
  );
};

export default ActivitiesContainer;
