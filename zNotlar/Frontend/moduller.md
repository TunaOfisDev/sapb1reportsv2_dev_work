

sudo chown -R $USER:$USER /var/www/sapb1reportsv2/frontend
sudo npm install



user yetkiler gecici olarak alir
sudo chown -R user:user /var/www/sapb1reportsV2
www-data ya yetkileri geriver 
sudo chown -R www-data:www-data /var/www/sapb1reportsV2

npm install axios
npm install jwt-decode
npm install loglevel
npm install --save @fortawesome/react-fontawesome @fortawesome/free-solid-svg-icons
npm install react-router-dom
npm install react-data-table-component
npm update @tanstack/react-table
npm install xlsx
npm install @mui/material @emotion/react @emotion/styled
sudo chown -R user:user /var/www/sapb1reportsv2
npm i xlsx

npm install react-redux
npm install @reduxjs/toolkit
npm install react-big-calendar moment
npm install moment --save
npm install react-toastify
npm install react-data-table-component
npm install antd
npm install react-select




*******************
frontend.sh script eski kod
#backend/scripts/frontend.sh
#!/bin/bash 

# Frontend build dizinine git
cd /var/www/sapb1reportsv2/frontend

# node_modules ve önbellek dosyalarının sahipliğini güncelle
sudo chown -R user:user node_modules

# Yetkileri geçici olarak güncelle
sudo chown -R user:user build

# Statik dosyaları oluştur (örnek bir komut)
sudo chown -R user:user /var/www/sapb1reportsv2
cd /var/www/sapb1reportsv2/frontend
npm run build

# Yetkileri www-data kullanıcısına geri ver
sudo chown -R www-data:www-data build

sudo chown -R www-data:www-data /var/www/sapb1reportsv2
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
sudo systemctl status nginx
sudo systemctl status gunicorn




Tüm bağımlılıkların en son sürümlerini yüklemek için `npm` veya `yarn` kullanabilirsiniz. Aşağıda, bağımlılıkları güncellemek için izlemeniz gereken adımlar yer almaktadır:

### 1. **npm-check-updates (ncu) Kullanarak Tüm Bağımlılıkları Güncelleme**
`npm-check-updates` adlı bir araç, `package.json` dosyanızdaki tüm bağımlılıkları en son sürümlere günceller. Bu aracı global olarak kurarak ve kullanarak tüm bağımlılıkları güncelleyebilirsiniz.

**npm-check-updates'i Kurma:**

```bash
npm install -g npm-check-updates
```

**Bağımlılıkları Güncelleme:**

```bash
ncu -u
```

Bu komut, `package.json` dosyanızdaki tüm bağımlılıkları en son sürümlere günceller.

**Bağımlılıkları Yeniden Kurma:**

Güncellemeleri yaptıktan sonra, bağımlılıkları yeniden kurmanız gerekecektir:

```bash
npm install
```

### 2. **Manuel Güncelleme**
Eğer belirli paketleri manuel olarak güncellemek isterseniz, aşağıdaki komutu kullanabilirsiniz:

```bash
npm install <paket-adi>@latest --save
```

Bu, belirttiğiniz paketi en son sürüme günceller ve `package.json` dosyasını otomatik olarak günceller.

### 3. **Yarn Kullanarak Güncelleme (Alternatif)**
Eğer `yarn` kullanıyorsanız, tüm bağımlılıkları en son sürümlere güncellemek için `yarn upgrade-interactive --latest` komutunu kullanabilirsiniz:

```bash
yarn upgrade-interactive --latest
```

Bu komut, tüm bağımlılıkları listeleyecek ve hangi bağımlılıkların güncelleneceğini seçmenize olanak tanıyacaktır.

### 4. **Yedekleme ve Test**
Bağımlılıkları güncellemeden önce, mevcut durumun bir yedeğini almak iyi bir fikirdir. Ayrıca, tüm güncellemeleri yaptıktan sonra projenizi baştan aşağı test edin; bazı büyük sürüm değişiklikleri (major updates) mevcut kodunuzla uyumsuz olabilir ve ek düzeltmeler gerekebilir.

Eğer bu adımları takip ederseniz, `package.json` dosyanızdaki tüm bağımlılıkların en son sürümlerini yüklemiş olacaksınız. Eğer başka bir yardıma ihtiyaç duyarsanız, lütfen sormaktan çekinmeyin!