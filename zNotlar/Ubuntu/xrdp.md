Ubuntu ortamında XRDP kurulumu için aşağıdaki terminal komutlarını kullanabilirsiniz:

1. XRDP paketini kurun:
   ```
   sudo apt-get update
   sudo apt-get install xrdp
   ```

2. XRDP servisini başlatın ve otomatik başlamasını sağlayın:
   ```
   sudo systemctl start xrdp
   sudo systemctl enable xrdp
   ```

3. Kullanıcıya XRDP için yetki verin. Burada "user" kullanıcısını örnek olarak kullanıyorum, kendi kullanıcı adınızı buraya girin:
   ```
   sudo adduser user xrdp
   ```

Bu komutlar, XRDP'nin Ubuntu sisteminizde başarılı bir şekilde kurulmasını ve belirtilen kullanıcının XRDP'ye erişimini sağlayacaktır.