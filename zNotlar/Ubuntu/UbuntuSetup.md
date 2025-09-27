


1. **Ubuntu'nun Hyper-V'ye Kurulumu:**
   - Sanal makine oluştur, kaynak ataması yap ve Ubuntu ISO ile kurulumu gerçekleştir.

2. **XRDP Kurulumu ve Konfigürasyonu:**
   - XRDP'yi yükleyip yapılandırarak Windows'tan uzaktan masaüstü bağlantısı kur.

3. **Kullanıcı ve Yetkilerin Yapılandırılması:**
   - Gerekli yetkileri vermek için kullanıcı grupları ve erişim izinleri ayarla.
   - var/www/sapb1reports_v2 yetki tanımları user kullanıcı için full yetki
   - user/home/sapb1reports_v2 yetki tanımları user kullanıcı için full yetki

4. **Geliştirme Ortamının Kurulumu:**
   - VS Code, Python, Django, django rest, gunicorn, nginx, Elasticsearch ve Redis kurulumlarını yap.

5. **Proje Klasör Yapısının Oluşturulması:**
   - Proje dizinini oluştur ve alt klasörler olarak 'backend', 'frontend' ve 'venv' dizinlerini yapılandır.

6. **Node.js Kurulumu:**
   - Front-end geliştirme için Node.js ve npm'i kur ve yapılandır.

7. **Proje Yapısının ve Yetkilerin Düzenlenmesi:**
   - Projeyi `/var/www` veya kullanıcı `home` dizininde düzenle ve uygun dosya izinlerini ayarla.

8. **klavye ayarını yap
- setxkbmap -layout us


Sanal makinenizin saat ayarlarını değiştirmek istiyorsanız ve grafiksel kullanıcı arayüzü üzerinden ayarlar kilitliyse, bunu terminal üzerinden yapabilirsiniz. Ayarların kilitlenmiş olması genellikle sanal makinenizin zaman senkronizasyon özelliğinin ana bilgisayar ile etkinleştirilmiş olması nedeniyle olabilir.

Terminali açın ve aşağıdaki komutlarla zamanı manuel olarak ayarlayabilirsiniz:

1. Öncelikle, şu anki zaman dilimi verisini görüntüleyin:
   ```sh
   timedatectl
   ```

2. Eğer `NTP` etkinse (`Network Time Protocol`), bu özelliği devre dışı bırakmanız gerekebilir. Bunu yapmak için:
   ```sh
   sudo timedatectl set-ntp no
   ```

3. Ardından, doğru zaman dilimini ayarlayabilirsiniz, örneğin İstanbul için:
   ```sh
   sudo timedatectl set-timezone Europe/Istanbul
   ```

4. Son olarak, saat ve tarihi manuel olarak ayarlayın. Örneğin, 19 Nisan 2024 saat 08:32 için:
   ```sh
   sudo timedatectl set-time '2024-04-19 08:32:00'
   ```

Bu işlemleri tamamladıktan sonra, `timedatectl` komutu ile yeni ayarlarınızı doğrulayabilirsiniz.

Bu adımlar işe yaramazsa, sanal makine ayarlarınızı kontrol edin. Çoğu sanal makine yazılımı (VMware, VirtualBox vb.), sanal makinenizin ana makineyle zamanı senkronize etmesine izin veren ayarlar içerir. Bu ayarları sanal makinenizin ayarları menüsünden değiştirmeniz gerekebilir.




