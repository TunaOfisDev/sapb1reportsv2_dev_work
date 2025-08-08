## `frontend/src/auth/frontend_auth.md`

### 🏢 Genel Mimarî: Bir Şirket Analojisi

Bu `auth` yapısını, iyi yönetilen bir şirketin departmanları gibi düşünebiliriz. Her dosyanın net bir görevi vardır ve bu sayede sistem düzenli çalışır.

-   **`AuthProvider.js`**: Şirketin **Genel Müdürüdür**. Tüm kararları o verir, kimin şirkette olduğunu (`user` state'i) o bilir.
-   **`AuthContext.js`**: Şirketin **Duyuru Panosudur**. Genel Müdür, önemli bilgileri (kimin login olduğu gibi) bu panoya asar ve diğer tüm çalışanlar bu panoya bakarak bilgi alır.
-   **`authService.js`**: **Dış İlişkiler Departmanıdır**. Sadece o, şirket dışıyla (backend API) görüşür. İşe alım (`login`) veya token doğrulama gibi işlemleri yapar.
-   **`tokenService.js`**: **Kasa Dairesidir**. Dış İlişkiler'in aldığı değerli evrakları (JWT token'ları) alır ve şirketin kasasına (tarayıcının `localStorage`'ı) güvenli bir şekilde koyar veya oradan alır.
-   **`useAuth.js`**: **Genel Müdür'ün Asistanıdır**. Herkesin Genel Müdür'e (ve dolayısıyla Duyuru Panosu'na) kolayca ulaşmasını sağlayan bir kısa yoldur.
-   **`LogoutButton.js`**: Diğer departmanlardan herhangi bir **Çalışandır**. Duyuru Panosu'ndaki bilgileri kullanarak kendi işini yapar.



---

### 📄 Dosyaların Görevleri

Aşağıda her bir dosyanın ne işe yaradığı detaylı olarak açıklanmıştır.

***

#### `AuthContext.js` - Duyuru Panosu
-   **Ne İşe Yarar?** Uygulama genelinde paylaşılacak olan kimlik doğrulama bilgilerinin (`isAuthenticated`, `user`) ve fonksiyonlarının (`login`, `logout`) "kalıbını" oluşturur. React'in `createContext` fonksiyonu ile boş bir "global state" deposu yaratır.
-   **Teknik Detay:** Bu dosya tek başına bir iş yapmaz, sadece diğer bileşenlerin aynı dili konuşmasını sağlayan bir kontrat görevi görür. `AuthProvider` bu depoyu doldurur, diğer bileşenler ise bu depodan veri okur.

***

#### `AuthProvider.js` - Genel Müdür
-   **Ne İşe Yarar?** Kimlik doğrulama sisteminin **beynidir**. Uygulamanın en tepesinde (genellikle `App.js` veya `index.js` içinde) tüm uygulamayı bir `Provider` ile sarmalar.
-   **Ana Görevleri:**
    1.  **Durum Yönetimi (`useState`):** `user`, `isAuthenticated`, `loading` gibi anlık durumları kendi içinde tutar.
    2.  **Veri Sağlama:** Tuttuğu bu durumları ve `login`/`logout` gibi fonksiyonları `AuthContext.Provider` aracılığıyla tüm alt bileşenlerin kullanımına sunar.
    3.  **Oturum Kontrolü (`useEffect`):** Uygulama ilk yüklendiğinde çalışır. `tokenService`'i kullanarak tarayıcı hafızasında geçerli bir token olup olmadığını kontrol eder. Varsa, kullanıcıyı otomatik olarak "login" olmuş kabul eder.
    4.  **İş Mantığı:** `login` ve `logout` fonksiyonlarını tanımlar. Bu fonksiyonlar çalıştığında, API istekleri için `authService`'i, token saklama için `tokenService`'i kullanır ve kendi içindeki `user` state'ini günceller.

***

#### `tokenService.js` - Kasa Dairesi
-   **Ne İşe Yarar?** Uygulamada tarayıcının `localStorage`'ına dokunma yetkisi olan **tek dosyadır**. Bu, sorumluluğu tek bir yerde toplayarak kod tekrarını ve hataları önler.
-   **Ana Görevleri:**
    1.  `setUser(data)`: Login sonrası `authService`'den gelen kullanıcı ve token bilgilerini `localStorage`'a JSON formatında kaydeder.
    2.  `getUser()`: `localStorage`'daki kullanıcı verisini okur ve JSON formatından objeye çevirir.
    3.  `removeUser()`: Logout olduğunda `localStorage`'daki veriyi siler.
    4.  **Yardımcı Fonksiyonlar:** `getLocalAccessToken`, `isTokenExpired` gibi fonksiyonlarla token'larla ilgili işlemleri basitleştirir.

***

#### `authService.js` - Dış İlişkiler Departmanı
-   **Ne İşe Yarar?** Backend API ile kimlik doğrulama arasındaki tüm iletişimi yöneten katmandır. `axiosInstance` kullanarak `authcentral` uygulamasının endpoint'lerine istek atar.
-   **Ana Görevleri:**
    1.  `login(email, password)`: `/login/` endpoint'ine POST isteği gönderir. Başarılı olursa, cevaben gelen token'ları `tokenService` aracılığıyla kaydeder.
    2.  `validateToken()`: Elimizdeki bir token'ın hala geçerli olup olmadığını backend'e sorar.
    3.  `logout()`: `tokenService` aracılığıyla yerel token'ları temizler. (İsteğe bağlı olarak backend'deki bir `/logout/` endpoint'ini de çağırabilir).

***

#### `useAuth.js` - Genel Müdür'ün Asistanı
-   **Ne İşe Yarar?** Diğer bileşenlerin `AuthContext`'e erişimini kolaylaştıran basit bir custom hook'tur.
-   **Avantajı:** Her bileşende `import { useContext } from 'react';` ve `import AuthContext from './AuthContext';` yazıp `useContext(AuthContext)` demek yerine, sadece `const auth = useAuth();` demek yeterlidir. Bu, kodu daha temiz ve kısa hale getirir.

***

#### `LogoutButton.js` - Örnek Çalışan
-   **Ne İşe Yarar?** Bu, yukarıdaki sistemin bir "tüketicisidir". Yani, `AuthContext`'te paylaşılan verileri ve fonksiyonları nasıl kullanacağımıza dair basit bir örnektir.
-   **Çalışma Mantığı:** `useAuth()` hook'unu kullanarak context'e erişir, oradan `logout` fonksiyonunu alır ve butona tıklandığında bu fonksiyonu çağırır.

### Sonuç
Bu yapı, son derece modüler, bakımı kolay ve profesyonel bir kimlik doğrulama sistemidir. Her parçanın tek bir sorumluluğu vardır ve bu sayede sistemin herhangi bir yerini, diğerlerini bozma endişesi olmadan rahatlıkla güncelleyebilirsiniz.