


Gunicorn'u kullanarak Django projeniz için bir Unix socket oluşturmak ve bu socket üzerinden Nginx ile entegre etmek, özellikle production ortamında yaygın bir yöntemdir. Bu ayarlamaların yapılması, projenizin daha güvenli ve verimli bir şekilde çalışmasını sağlar.

İşte `sapb1reportsV2` Django projeniz için gerekli adımlar:

### 1. Gunicorn Kurulumu ve Socket Oluşturma

Öncelikle, Django projenizin bulunduğu ana dizine gidin:

```bash
cd /home/user/sapb1reportsV2
```

Gunicorn'u sanal ortamınıza kurun:

```bash
source venv/bin/activate
pip install gunicorn
```

Gunicorn ile Unix socket oluşturmak için aşağıdaki komutu kullanabilirsiniz. 
Bu komut, projenizin WSGI uygulamasını Gunicorn üzerinden çalıştırır ve `sapreports.sock` 
adında bir Unix socket dosyası oluşturur:

(env) cd /home/user/sapb1reportsV2/backend icinde calistir
```bash
gunicorn --workers 3 --bind unix:/home/user/sapb1reportsV2/sapreports.sock sapreports.wsgi:application
```
gunicorn --bind 0.0.0.0:8000 sapreports.wsgi

- `--workers 3`: Gunicorn işlemcilerinin sayısını belirtir. Genellikle CPU çekirdek sayısının 2-4 katı arası bir değer önerilir.
- `--bind unix:/home/user/sapb1reportsV2/sapreports.sock`: Socket dosyasının yolunu ve adını belirtir.
- `sapreports.wsgi:application`: Django projenizin WSGI uygulamasına işaret eder.

### 2. Nginx Yapılandırması

Nginx yapılandırma dosyasını düzenleyin (örneğin, `/etc/nginx/sites-available/sapb1reportsV2` veya benzer bir dosya). Bu dosyada, Nginx'in Gunicorn socket'ine nasıl yönlendirme yapacağını belirtin:

```nginx
server {
    listen 80;
    server_name example.com;  # Sunucunuzun domain adı veya IP adresi

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

- `proxy_pass` komutu, gelen istekleri Gunicorn'un oluşturduğu Unix socket'e yönlendirir.
- `location /static/` ve `location /media/`, statik ve medya dosyalarının sunulacağı yolları belirtir.
- `location /product_pictures/` ise, `/mnt/product_picture/` dizinindeki resim dosyalarına erişimi sağlar.

Nginx yapılandırma dosyasını kontrol edin ve Nginx'i yeniden başlatın:

```bash
sudo nginx -t
sudo systemctl restart nginx
```

Bu ayarlar sonrasında, Django uygulamanız Nginx üzerinden isteklere yanıt verecek ve statik dosyalarınızı, medya dosyalarınızı ve ürün resimlerinizi doğru şekilde sunacaktır.

Gunicorn çalıştırılırken karşılaşılan `ModuleNotFoundError: No module named 'sapreports'` hatası, Gunicorn'un `sapreports` WSGI modülünü bulamadığını gösteriyor. Bu sorun genellikle yanlış dizinde çalıştırıldığında veya WSGI uygulama yolunun yanlış belirtildiğinde meydana gelir.

### Sorunu Çözme Adımları

1. **Doğru Dizinde Çalıştırın:**
   Gunicorn'u, Django proje dizininizde (`sapb1reportsV2`) çalıştırdığınızdan emin olun. Django projenizin `manage.py` dosyasının olduğu dizinde olmalısınız.

2. **WSGI Uygulama Yolunu Doğrulayın:**
   `sapreports.wsgi:application` ifadesi, `sapreports/wsgi.py` dosyasındaki `application` objesini işaret eder. Bu yolu ve dosyanın varlığını kontrol edin.

3. **Virtual Environment Aktif Mi?**
   Gunicorn'u sanal ortamınızın (virtual environment) aktif olduğu bir terminalden çalıştırdığınızdan emin olun. Bu, Django projenizdeki bağımlılıkların doğru yüklenmesini sağlar.

4. **WSGI Dosyasının İçeriğini Kontrol Edin:**
   `sapreports/wsgi.py` dosyasının içeriğini kontrol edin. Bu dosya şu şekilde olmalıdır:

   ```python
   """
   WSGI config for sapreports project.

   It exposes the WSGI callable as a module-level variable named ``application``.
   """

   import os
   from django.core.wsgi import get_wsgi_application

   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sapreports.settings')

   application = get_wsgi_application()
   ```

   Burada `DJANGO_SETTINGS_MODULE` değişkeni, projenizin `settings.py` dosyasına doğru şekilde işaret etmelidir.

5. **Gunicorn Komutunu Tekrar Çalıştırın:**
   Sanal ortamınız aktif iken ve doğru dizindeyken, Gunicorn'u yeniden başlatın:

   ```bash
   gunicorn --workers 3 --bind unix:/home/user/sapb1reportsV2/sapreports.sock sapreports.wsgi:application
   ```

Bu adımları izleyerek hata nedeninin tespit edilmesi ve çözümüne yönelik ilerleme kaydedilebilir. Eğer hala hata alınıyorsa, Django projenizin yapısını ve WSGI dosyanızın içeriğini yeniden gözden geçirmeniz gerekebilir.