Öncelikle, yüklediğin **"Working_with_SAP_Business_One_Service_Layer.pdf"** dosyasında **SAP Business One Service Layer SSL sertifikası** ile ilgili bilgi olup olmadığını kontrol edeceğim. Ardından, **Ubuntu ortamında canlı sistem için SSL entegrasyonu sorunsuz çalıştırmak adına bir iş talimat planı** oluşturacağım. 

Şimdi PDF dosyanın içinde **SSL sertifikasıyla ilgili bir bilgi olup olmadığını** tarıyorum.

Evet, yüklediğin **"Working_with_SAP_Business_One_Service_Layer.pdf"** dosyasında **SAP Business One Service Layer SSL sertifikası ile ilgili bilgiler** mevcut. Özellikle aşağıdaki konular ele alınmış:

1. **Security Certificate Verification During SSL Communication**  
   - SAP Business One bileşenlerinde **hostname veya FQDN**, güvenlik sertifikasının **Common Name (CN)** ve **Subject Alternative Name (SAN)** ile eşleşmelidir.

2. **Service Layer için SSL Sertifikasının Yapılandırılması**  
   - **Service Layer’in b1s.conf yapılandırma dosyasına** `"VerifyTLSCertificate":true` eklenmesi gerekiyor.
   - **Ubuntu/Linux sisteminde sertifika eklemek için:**
     ```sh
     sudo zypper install update-ca-certificates
     sudo cp your_certificate.pem /etc/pki/trust/anchors/
     sudo update-ca-certificates
     sudo systemctl restart b1s
     ```
   - Böylece **Service Layer**, SAP Business One için güvenli bir SSL bağlantısı kurabilir.

---

### **Ubuntu Ortamında SAP HANA Service Layer SSL Sertifikasını Canlıya Alma İş Talimatı**
Bu adımları takip ederek **Ubuntu ortamında SSL sertifikası sorunlarını aşabilir ve canlıya alabilirsiniz**:

#### **1️⃣. SAP Business One Service Layer Sertifikasının Dışa Aktarılması**
1. SAP HANA sunucusundan root sertifikasını dışa aktar:
   ```sh
   openssl s_client -connect 10.131.212.112:50000 -showcerts
   ```
2. Sertifikayı kaydet:
   ```sh
   nano sap_hana_cert.pem
   ```
   İçeriği yapıştır ve kaydet.

---

#### **2️⃣. Sertifikayı Ubuntu'ya Ekleyin**
SAP HANA'nın kendi sertifikasını Ubuntu'nun güvenilir CA deposuna ekleyin:
```sh
sudo cp sap_hana_cert.pem /usr/local/share/ca-certificates/
sudo update-ca-certificates
```
Bu işlemden sonra sistem sertifikayı güvenilir olarak tanıyacaktır.

---

#### **3️⃣. SAP Business One Service Layer Ayarlarını Güncelleyin**
1. **SAP Business One Service Layer yapılandırmasını açın**:
   ```sh
   sudo nano /opt/sap/SAPBusinessOne/ServiceLayer/conf/b1s.conf
   ```
2. **Şu satırı ekleyin veya düzenleyin**:
   ```json
   "VerifyTLSCertificate": true
   ```
3. **Service Layer'i yeniden başlatın**:
   ```sh
   sudo systemctl restart b1s
   ```

---

#### **4️⃣. Python Requests için Sertifika Tanımlayın**
Python uygulamanızın SAP HANA SSL sertifikasını tanıyabilmesi için:
1. Sertifikayı Requests kütüphanesi ile kullan:
   ```python
   import os
   os.environ["REQUESTS_CA_BUNDLE"] = "/usr/local/share/ca-certificates/sap_hana_cert.pem"
   ```
2. Veya doğrudan isteklerde belirtin:
   ```python
   import requests
   response = requests.get("https://10.131.212.112:50000/b1s/v1/Login", verify="/usr/local/share/ca-certificates/sap_hana_cert.pem")
   print(response.text)
   ```

---

#### **5️⃣. Django İçin SSL Sertifikasını Ayarlayın**
Eğer **Django** üzerinden istek gönderiyorsanız, **settings.py** içinde şu ayarı ekleyin:
```python
REQUESTS_CA_BUNDLE = "/usr/local/share/ca-certificates/sap_hana_cert.pem"
```
veya `.env` dosyanıza ekleyin:
```
REQUESTS_CA_BUNDLE=/usr/local/share/ca-certificates/sap_hana_cert.pem
```
Böylece Django otomatik olarak bu sertifikayı kullanacaktır.

---

### **Sonuç ve Test**
1. **Service Layer Login Testi**  
   ```sh
   curl -k --cert /usr/local/share/ca-certificates/sap_hana_cert.pem https://10.131.212.112:50000/b1s/v1/Login
   ```
   Eğer giriş başarılı olursa, **SessionId** dönecektir.

2. **Python Request Testi**
   ```python
   import requests
   response = requests.get("https://10.131.212.112:50000/b1s/v1/Login", verify="/usr/local/share/ca-certificates/sap_hana_cert.pem")
   print(response.json())
   ```

Bu talimatları takip ederek **SAP Business One Service Layer’ı canlı sistemde sorunsuz çalıştırabilirsiniz** .