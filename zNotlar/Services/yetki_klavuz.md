🚨 Komutanım, artık sistem çalışıyor ve **tehlikeli `chown -R` komutlarından uzak durma** vaktidir.
Senin için **dosya yollarına özel** olarak yapılandırılmış **TARZ onaylı bir "Yetki ve Sahiplik Eylem Planı"** hazırladım.

---

# 🛡️ SAPB1ReportsV2 – Kurumsal Yetki ve Sahiplik Eylem Planı

Bu plan, tüm dosya yollarına özel olarak:

* `user` ve `www-data` erişim dengesini sağlar
* `systemd` servislerinin çökmesini önler
* `npm`, `gunicorn`, `celery`, `daphne` ve `django` bileşenlerinin **çakışmadan** çalışmasını sağlar

---

## 🧩 Ana Roller

| Rol        | Açıklama                                                |
| ---------- | ------------------------------------------------------- |
| `user`     | Geliştirici, VSCode ve shell üzerinden işlem yapar      |
| `www-data` | Nginx, Gunicorn, Daphne, Celery servislerini çalıştırır |
| `sapb1`    | Ortak grup – hem `user` hem `www-data` bu gruba dahil   |

---

## 📂 Klasör Bazlı Yetki Politikası

### 🔧 1. `backend/logs/` → **Servis log yazımı**

```bash
sudo chown -R www-data:sapb1 /var/www/sapb1reportsv2/backend/logs
sudo chmod -R 775 /var/www/sapb1reportsv2/backend/logs
sudo setfacl -dRm u:www-data:rwX -m u:www-data:rwX /var/www/sapb1reportsv2/backend/logs
sudo setfacl -dRm u:user:rwX    -m u:user:rwX    /var/www/sapb1reportsv2/backend/logs
```

---

### ⚙️ 2. `frontend/build/` → **www-data servis kullanımı, user build yapar**

```bash
sudo chown -R www-data:sapb1 /var/www/sapb1reportsv2/frontend/build
sudo chmod -R 775 /var/www/sapb1reportsv2/frontend/build
```

---

### 🧼 3. `frontend/.npm-cache/`, `node_modules/` → **sadece user kullanır, silme tavsiye edilir**

```bash
rm -rf /var/www/sapb1reportsv2/frontend/.npm-cache
rm -rf /var/www/sapb1reportsv2/frontend/node_modules
```

Ardından `.npmrc` ile özel cache tanımla:

```bash
echo "cache=/tmp/npm-cache" > /var/www/sapb1reportsv2/frontend/.npmrc
```

---

### 📄 4. `.env` ve `venv/` dizini → **root tarafından oluşturulur, servislerce kullanılır**

```bash
sudo chown -R root:sapb1 /var/www/sapb1reportsv2/venv
sudo chmod -R 755 /var/www/sapb1reportsv2/venv/bin
sudo chmod +x /var/www/sapb1reportsv2/venv/bin/*
```

`.env`:

```bash
sudo chown www-data:sapb1 /var/www/sapb1reportsv2/backend/.env
sudo chmod 640 /var/www/sapb1reportsv2/backend/.env
```

---

### 🔧 5. `daphne.sock`, `gunicorn.sock` → **www-data tarafından oluşturulur**

```bash
sudo chown www-data:sapb1 /var/www/sapb1reportsv2/backend/*.sock*
sudo chmod 775 /var/www/sapb1reportsv2/backend/*.sock*
```

---

### 📦 6. Backend Uygulama Klasörleri

Tüm `backend/{modül}` dizinleri için:

```bash
sudo chown -R user:sapb1 /var/www/sapb1reportsv2/backend
sudo chmod -R g+rwX /var/www/sapb1reportsv2/backend
```

→ Bu sayede:

* `user` geliştirme yapar
* `www-data` log, static, media erişimine sahip olur

---

### 📁 7. `media/`, `backend_static/`, `static/`

```bash
sudo chown -R www-data:sapb1 /var/www/sapb1reportsv2/backend/media
sudo chown -R www-data:sapb1 /var/www/sapb1reportsv2/backend/backend_static
sudo chown -R www-data:sapb1 /var/www/sapb1reportsv2/backend/static
sudo chmod -R 775 /var/www/sapb1reportsv2/backend/{media,backend_static,static}
```

---

## 🔐 Kalıcı Güvence için ACL Tanımları

```bash
sudo setfacl -dRm u:www-data:rwX -m u:www-data:rwX /var/www/sapb1reportsv2/backend/logs
sudo setfacl -dRm u:user:rwX -m u:user:rwX /var/www/sapb1reportsv2/backend/logs
```

---

## 🧠 İleri Seviye Tavsiye

* Bu yetki politikasını her `deploy` sonrası `deploy.sh` içinde küçük `check_acl.sh` ile doğrulat
* `logs/`, `sock` ve `build/` klasörleri dışında tüm `chown` işlemlerinden **kaçın**
* `sudo chown -R` asla tüm projeye uygulanmamalıdır!

---

## ✨ Sistem Stabil Olduğunda...

Bu eylem planı, hem geliştirici (sen) hem servisler (nginx, celery, gunicorn) için çatışmasız bir işletim ortamı oluşturur.

İstersen bu klavuzu `zNotlar/YetkiKlavuzi.md` olarak kaydedelim.

Emrin yeter, Komutanım. 🫡
