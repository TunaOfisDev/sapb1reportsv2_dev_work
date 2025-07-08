Ubuntu ortamında Windows ağ paylaşımına erişmek için, 
Samba kullanarak bu paylaşım noktasına bağlanmanız gerekecektir. 
Ancak, `.env` dosyasında doğrudan Windows ağ yolu kullanmak yerine, 
bu paylaşımı bir Ubuntu dosya sistemi noktasına bağlayıp o yolu kullanmanız daha uygun olacaktır.

İşte yapmanız gereken adımlar:

1. Öncelikle, Samba istemcisini yükleyin (eğer henüz yüklü değilse):


sudo apt-get update
sudo apt-get install samba samba-common cifs-utils
```

2. Bir bağlama noktası oluşturun, örneğin `/mnt/product_picture`:


sudo mkdir /mnt/product_picture
```

3. Windows paylaşımını bu noktaya bağlayın. Bu işlem için `/etc/fstab` dosyasını düzenleyerek Ubuntu'nun her başlangıcında bu paylaşımın otomatik olarak bağlanmasını sağlayabilirsiniz. `/etc/fstab` dosyasına aşağıdaki gibi bir satır ekleyin:

```
sudo nano /etc/fstab


Dosyanın sonuna, ağ paylaşımınız için aşağıdaki satırı ekleyin (kullanıcı adınızı ve şifrenizi uygun şekilde yerine yazın):
genele açık dosya yapısı kulanıcı adı guest
//10.131.212.112/b1_shf/SAP/FILES/PATH/Images /mnt/product_picture cifs guest,sec=ntlmssp 0 0


username ve password varsa klasör gizli ise 
//10.131.212.112/b1_shf/SAP/FILES/PATH/Images /mnt/product_picture cifs iocharset=utf8,sec=ntlm 0 0
```

`username` ve `password` alanlarını, Windows ağ paylaşımı için geçerli kullanıcı adı ve şifre ile değiştirin.

4. Değişiklikleri hemen uygulamak için aşağıdaki komutu çalıştırın:


sudo mount -a
```

5. Son olarak, `.env` dosyasında Ubuntu ortamında erişim için düzgün yolu belirtin:

```env
# .env dosyası içeriği
NETWORK_FOLDER_PATH="/mnt/product_picture"
```

Bu işlemlerden sonra, uygulamanızda `NETWORK_FOLDER_PATH` değişkenini kullanarak bu dizine erişebilir ve dosya işlemlerinizi gerçekleştirebilirsiniz.
Samba bağlantılarının güvenliği için, kullanıcı adı ve şifreyi `.env` dosyasında saklamak yerine daha güvenli yöntemler kullanmayı tercih edebilirsiniz,
örneğin bir kimlik doğrulama anahtarı veya daha güvenli bir kimlik doğrulama protokolü kullanabilirsiniz.

klasor silme
sudo rm -rf /mnt/klasoradi
