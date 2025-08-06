// frontend/src/index.js
import React from 'react';
import ReactDOM from 'react-dom/client';
import 'regenerator-runtime/runtime';

// YENİ: Bootstrap CSS'i burada import ediyoruz.
import 'bootstrap/dist/css/bootstrap.min.css';

import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import AuthProvider from './auth/AuthProvider';
import { Provider } from 'react-redux';
import store from './redux/store';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import dayjs from 'dayjs';
import 'dayjs/locale/tr';
import updateLocale from 'dayjs/plugin/updateLocale';



// 1) React Query için QueryClient oluştur
const queryClient = new QueryClient();

// 2) Day.js yapılandırması
 dayjs.extend(updateLocale);
 dayjs.updateLocale('tr', {
  months: ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"],
  weekdaysMin: ["Pt", "Sa", "Ça", "Pe", "Cu", "Ct", "Pz"],
  weekStart: 1 // Haftanın ilk günü Pazartesi
});

dayjs.locale('tr'); // Varsayılan dili Türkçe olarak ayarla

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
 // <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <Provider store={store}>
        <AuthProvider>
          <App />
        </AuthProvider>
      </Provider>
    </QueryClientProvider>
  //</React.StrictMode>
);

reportWebVitals();
