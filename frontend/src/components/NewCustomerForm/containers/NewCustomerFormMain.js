// frontend/src/components/NewCustomerForm/containers/NewCustomerFormMain.js
import { useState } from 'react';
import NewCustomerFormContainer from './NewCustomerFormContainer';
import NewCustomerFormDashboard from './NewCustomerFormDashboard';
import '../css/NewCustomerFormMain.css';  // CSS dosyasının yolu

const NewCustomerFormMain = () => {
  const [activeTab, setActiveTab] = useState('new');

  return (
    <div className="new-customer-form-main">
      <div className="new-customer-form-main__tabs">
        <button
          className={`new-customer-form-main__tab ${activeTab === 'new' ? 'new-customer-form-main__tab--active' : ''}`}
          onClick={() => setActiveTab('new')}
        >
          Yeni Form Oluştur
        </button>
        <button
          className={`new-customer-form-main__tab ${activeTab === 'dashboard' ? 'new-customer-form-main__tab--active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          Form Dashboard
        </button>
      </div>
      <div className="new-customer-form-main__content">
        {activeTab === 'new' && <NewCustomerFormContainer />}
        {activeTab === 'dashboard' && <NewCustomerFormDashboard />}
      </div>
    </div>
  );
};

export default NewCustomerFormMain;
