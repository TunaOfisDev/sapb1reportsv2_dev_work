Ubuntu sunucusunun IP adresi `10.130.212.112` olduğuna göre, Django ve React uygulamalarınız için Gunicorn ve Nginx yapılandırmalarınızı buna uygun şekilde ayarlamanız gerekiyor. İşte yapmanız gerekenler:

### Django (Gunicorn)

1. **Gunicorn'u Çalıştırma:** Gunicorn'u Django uygulamanız için Unix socket üzerinden çalıştırın. Örneğin:

   ```bash
   gunicorn --workers 3 --bind unix:/home/user/sapb1reportsV2/sapreports.sock sapreports.wsgi:application
   ```

   Burada `--workers 3` seçeneği, 3 adet işçi süreci başlatır. Bu değeri sunucunuzun işlemci sayısına göre ayarlayabilirsiniz.

### Nginx

1. **Nginx Yapılandırması:**

   `/etc/nginx/sites-available/` dizinindeki yapılandırma dosyanızı aşağıdaki gibi güncelleyin:

   ```nginx
   server {
       listen 80;
       server_name 10.130.212.112;  # Sunucunuzun IP adresi

       location / {
           include proxy_params;
           proxy_pass http://unix:/home/user/sapb1reportsV2/sapreports.sock;
       }

       location /static/ {
           alias /home/user/sapb1reportsV2/backend/staticfiles/;
       }

       location /media/ {
           alias /home/user/sapb1reportsV2/backend/media/;
       }

       location /product_pictures/ {
           alias /mnt/product_picture/;
           autoindex off;
       }
   }
   ```

   Burada `/static/`, `/media/` ve `/product_pictures/` dizinlerinin doğru şekilde yapılandırıldığından emin olun.

2. **Nginx'i Yeniden Başlatma:**

   Yapılandırmayı güncelledikten sonra Nginx'i yeniden başlatın:

   ```bash
   sudo systemctl restart nginx
   ```

### React Uygulaması

React uygulamanızın backend API'sine doğru şekilde bağlanması için `axiosconfig.js` dosyasını güncelleyin:

```javascript
// frontend/src/api/axiosconfig.js
import axios from 'axios';
import log from 'loglevel';
import authService from '../auth/authService';

const API_VERSION = 'v2';
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || `http://10.130.212.112/api/${API_VERSION}/`;

const axiosInstance = axios.create({
  baseURL: API_BASE_URL
});

// Axios interceptors ve diğer konfigürasyonlar...
```

Bu yapılandırma, React uygulamanızın Django backend'ine `10.130.212.112` IP adresi üzerinden bağlanmasını sağlar.

### CORS Ayarları

Django uygulamanızın `settings.py` dosyasında CORS ayarlarınızı da güncelleyebilirsiniz:

```python
CORS_ALLOW_ALL_ORIGINS = True  # Tüm kökenlerden gelen isteklere izin ver
# veya belirli kökenleri belirtin
CORS_ALLOWED_ORIGINS = [
    "http://10.130.212.112",
    "http://localhost:3000",  # React geliştirme sunucusu
]
```

Bu ayarlarla, Django uygulamanızın belirtilen kökenlerden gelen isteklere izin vermesi sağlanır.

Bu adımları takip ettikten sonra, Django backend'iniz Gunicorn ve Nginx aracılığıyla doğru şekilde sunulmuş olacak ve React uygulamanız bu backend'e başarıyla bağlanabilecek.










Installing Nginx on Ubuntu 22.04 can be done by following a few steps. Here's a summarized version of what the process 
generally involves:

1. **Update software repositories**: It's always good practice to update your package lists before installing any new software. 
You can do this by running `sudo apt update` in the terminal.

2. **Install Nginx**: You can install Nginx by running `sudo apt install nginx`.

3. **Adjusting the Firewall**: Ubuntu 22.04 should come with `ufw` firewall running. You need to allow Nginx through the firewall. 
Typically, there are three profiles available for Nginx:
   - **Nginx Full**: Opens both port 80 (normal, unencrypted web traffic) and port 443 (TLS/SSL encrypted traffic).
   - **Nginx HTTP**: Opens only port 80 (normal, unencrypted web traffic).
   - **Nginx HTTPS**: Opens only port 443 (TLS/SSL encrypted traffic).

   You can enable one of these by running `sudo ufw allow 'Nginx HTTP'`.

4. **Checking your Web Server**: After installing Nginx, the web server should have automatically started. You can check its status with `sudo systemctl status nginx`.

5. **Manage the Nginx Process**: Now that Nginx is installed, you can start, stop, and restart the Nginx service using the following commands:
   - `sudo systemctl stop nginx`
   - `sudo systemctl start nginx`
   - `sudo systemctl restart nginx`
   - `sudo systemctl reload nginx` (for when you want to make configuration changes without dropping connections)
   - `sudo systemctl disable nginx` (to stop Nginx from starting at boot)
   - `sudo systemctl enable nginx` (to reverse that and have Nginx start at boot)

6. **Setting Up Server Blocks (Recommended)**: Instead of modifying the default configuration file directly, 
it's recommended to create new configuration files for each domain in the
 `/etc/nginx/sites-available/` directory and then creating symbolic links to those files in the 
 `/etc/nginx/sites-enabled/` directory.

Nginx web sunucusunda `/mnt/product_picture/` dizinini statik dosyalarınız için kullanıma açmak için aşağıdaki adımları takip edebilirsiniz:

1. **Nginx Sunucu Bloğu Oluşturmak**: 
Nginx yapılandırma dosyası genellikle `/etc/nginx/sites-available/` dizininde bulunur. 
Burada, projeniz için bir sunucu bloğu oluşturmanız gerekecek.
 Yapılandırma dosyasını (genellikle `default` veya projenizin adıyla bir dosya) 
 açın veya yeni bir dosya oluşturun.

2. **Statik Dosya Yolu Belirtmek**: Yapılandırma dosyasında, `/mnt/product_picture/` yolunu statik dosya sunucusu olarak belirten bir `location` bloğu ekleyin. Bu, Nginx'in bu klasördeki dosyalara doğrudan erişmesini sağlayacak ve istemcilere sunacaktır.

Örnek bir Nginx yapılandırma bloğu şu şekilde olabilir:

 sudo nano /etc/nginx/sites-available/sapb1reportsV2

```nginx
server {
    listen 80;
    server_name example.com; # Domain adınız veya sunucunuzun IP adresi

    location /product_pictures/ {
        alias /mnt/product_picture/; # Dosyaların sunulacağı dizin yolu
        autoindex off; # Dizin listelemeyi kapatır
    }


}
```

3. **Yapılandırma Dosyasını Etkinleştirmek**: Nginx'de yapılandırma dosyasını etkinleştirmek 
için, bu dosyayı 
`/etc/nginx/sites-enabled/` dizinine sembolik bir bağlantı (symlink) olarak eklemeniz gerekebilir. Bu genellikle şu komutla yapılır:

```bash
sudo ln -s /etc/nginx/sites-available/sapreports /etc/nginx/sites-enabled/
```

4. **Nginx'i Yeniden Başlatmak**: Yapılandırma değişikliklerinin etkili olması için Nginx'i yeniden başlatmanız gerekir. Bu şu komutla yapılır:

```bash
sudo systemctl restart nginx
```

5. **Güvenlik Duvarı Ayarları**: Eğer sunucunuzda bir güvenlik duvarı varsa, HTTP ve HTTPS trafiklerine izin verdiğinizden emin olun.

6. **Dosya İzinlerini Kontrol Etmek**: `/mnt/product_picture/` dizininin ve içindeki dosyaların web sunucusu tarafından okunabilir olduğundan emin olun. Gerekirse dosya izinlerini ayarlayın.

Bu adımları tamamladıktan sonra, web tarayıcınızda `http://example.com/product_pictures/your-image-file.jpg` şeklinde bir URL üzerinden resimlere erişebilirsiniz. `example.com` yerine kendi sunucunuzun domain adını veya IP adresini, `your-image-file.jpg` yerine de göstermek istediğiniz resmin adını kullanın.


Verdiğiniz hata çıktısına göre, NGINX yapılandırma dosyanızda bir problem var. NGINX, `/etc/nginx/sites-enabled/sapb1rportsV2` adında bir dosya arıyor ancak bu dosya mevcut değil. Muhtemelen bu, sembolik link oluştururken bir yazım hatası yapıldığı anlamına geliyor. Linkin adı `sapb1reportsV2` olmalı, ancak hata mesajında `sapb1rportsV2` olarak görünüyor, yani "e" harfi eksik.

Bu sorunu çözmek için şu adımları izleyebilirsiniz:

1. İlk olarak yanlış oluşturulan sembolik linki kaldırın:

   ```bash
   sudo rm /etc/nginx/sites-enabled/sapb1rportsV2
   ```

2. Daha sonra doğru dosya adıyla sembolik link oluşturun:

   ```bash
   sudo ln -s /etc/nginx/sites-available/sapb1reportsV2 /etc/nginx/sites-enabled/
   ```

3. NGINX yapılandırma dosyanızın doğru olduğundan emin olmak için test edin:

   ```bash
   sudo nginx -t
   ```

   Bu komut, herhangi bir hata olup olmadığını kontrol eder. Eğer "syntax is okay" ve "test is successful" mesajlarını görürseniz, yapılandırmanız doğru demektir.

4. Eğer yapılandırma testi başarılı ise, NGINX'i yeniden başlatın:

   ```bash
   sudo systemctl restart nginx
   ```

5. NGINX durumunu kontrol edin:

   ```bash
   sudo systemctl status nginx
   ```

Eğer hala hata alıyorsanız, `/etc/nginx/sites-available/sapb1reportsV2` dosyasının içeriğini kontrol edin ve NGINX yapılandırma sözdiziminin doğru olduğundan emin olun. Dosya içeriğinde yanlış bir yapılandırma veya eksik bir parantez gibi hatalar olabilir. Bu dosyada bir sorun varsa, NGINX başlamayacaktır.