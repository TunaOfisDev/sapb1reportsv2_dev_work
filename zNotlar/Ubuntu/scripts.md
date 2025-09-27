`sudo` kullanmadan ve şifre sormadan belirli komutları çalıştırmak için `sudoers` dosyasına ilgili komutları ekleyerek, belirli kullanıcıların bu komutları şifresiz çalıştırabilmesini sağlayabilirsiniz. Aşağıdaki adımlarla bu işlemi gerçekleştirebilirsiniz:

### 1. **`sudoers` Dosyasını Düzenleyin**

`sudoers` dosyasını düzenlemek için `visudo` komutunu kullanmanız gerekir. Bu komut, `sudoers` dosyasını düzenlerken hata yapma riskini azaltır:

```bash
sudo visudo
```

### 2. **Kullanıcıya Özel Kurallar Ekleyin**

`sudoers` dosyasına aşağıdaki satırı ekleyerek belirli bir kullanıcının belirli komutları şifresiz çalıştırmasına izin verebilirsiniz. Bu örnekte, `user` kullanıcısının `piprequirements.sh` scriptini şifresiz çalıştırmasına izin veriyoruz:

```bash
user ALL=(ALL) NOPASSWD: /var/www/sapb1reportsv2/backend/scripts/piprequirements.sh
```

### 3. **Script İçindeki `sudo` Komutlarını Kaldırın**

Scriptinizi düzenleyerek `sudo` komutlarını kaldırmanız gerekecek. Aşağıda örnek scriptin düzenlenmiş hali verilmiştir:

```bash
#!/bin/bash

# Log dosyalarının bulunduğu dizin
LOG_DIR="/var/www/sapb1reportsv2/backend/logs"

# Yetkileri geçici olarak kullanıcıya devret
chown -R user:user /var/www/sapb1reportsv2
echo "Yetkiler devralındı."

# requirements.txt dosyasını güncelle
pip freeze | cut -d '=' -f 1 > /var/www/sapb1reportsv2/backend/requirements.txt
echo "requirements.txt güncellendi."

# Yetkileri www-data kullanıcısına geri ver
chown -R www-data:www-data /var/www/sapb1reportsv2
echo "Yetkiler geri verildi."

# Log işlemini kaydet
echo "requirements.txt güncellendi ve yetkiler geri verildi: $(date)" >> $LOG_DIR/piprequirements.log
```

### 4. **Scripti Çalıştırın**

Artık scripti `sudo` komutunu kullanmadan çalıştırabilirsiniz:

```bash
/var/www/sapb1reportsv2/backend/scripts/piprequirements.sh
```
