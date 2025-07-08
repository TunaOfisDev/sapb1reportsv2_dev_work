Belirttiğiniz API yapısına uygun bir dökümantasyon aşağıdaki gibi olabilir:

```markdown
# AuthCentral API Dokümantasyonu

Bu dökümantasyon, AuthCentral API'sini kullanarak kimlik doğrulama ve kullanıcı yönetimi işlemlerini gerçekleştirmek için gerekli bilgileri sağlar.

## Genel Bakış

AuthCentral API, kullanıcıların kimlik doğrulamasını yapmak, oturum açmak ve kullanıcı bilgilerini yönetmek için kullanılır. API, JSON formatında veri alışverişi yapar.

API'yi kullanabilmek için herhangi bir yetkilendirme yöntemi gereklidir. Kimlik doğrulama için [Token-based Authentication](#token-based-authentication) yöntemini kullanabilirsiniz.

## API Yönlendirmeleri

1. [Kimlik Doğrulama](#kimlik-doğrulama)
   - Kullanıcı oturumu açma ve kimlik doğrulama işlemleri için bu yöntemi kullanın.

2. [Oturumu Kapatma](#oturumu-kapatma)
   - Kullanıcı oturumunu kapatma işlemi için bu yöntemi kullanın.

3. [Kullanıcı Bilgilerini Alma](#kullanıcı-bilgilerini-alma)
   - Kullanıcının bilgilerini almak için bu yöntemi kullanın.

4. [Token Geçerliliğini Kontrol Etme](#token-geçerliliğini-kontrol-etme)
   - Token'ın geçerliliğini kontrol etmek için bu yöntemi kullanın.

5. [Token Yenileme](#token-yenileme)
   - Token'ı yenilemek için bu yöntemi kullanın.

## Kimlik Doğrulama

Kullanıcıların kimlik doğrulaması için API'den gelen token kullanılır. Aşağıdaki yöntemi kullanarak token alabilirsiniz:

### Request

- URL: `/login/`
- HTTP Method: `POST`
- Headers:
  - `Content-Type: application/json`
- Request Body:

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

### Response

- Status Code: `200 OK`
- Response Body:

```json
{
  "refresh": "refresh_token_here",
  "access": "access_token_here"
}
```

## Oturumu Kapatma

Kullanıcı oturumunu kapatmak için aşağıdaki yöntemi kullanabilirsiniz:

### Request

- URL: `/logout/`
- HTTP Method: `POST`
- Headers:
  - `Authorization: Bearer <refresh_token_here>`

### Response

- Status Code: `205 Reset Content`

## Kullanıcı Bilgilerini Alma

Kullanıcının bilgilerini almak için aşağıdaki yöntemi kullanabilirsiniz:

### Request

- URL: `/user/`
- HTTP Method: `GET`
- Headers:
  - `Authorization: Bearer <access_token_here>`

### Response

- Status Code: `200 OK`
- Response Body:

```json
{
  "id": 1,
  "email": "user@example.com",
  "is_active": true,
  "is_staff": false,
  "departments": [],
  "position": []
}
```

## Token Geçerliliğini Kontrol Etme

Token'ın geçerliliğini kontrol etmek için aşağıdaki yöntemi kullanabilirsiniz:

### Request

- URL: `/token/validate/`
- HTTP Method: `GET`
- Headers:
  - `Authorization: Bearer <access_token_here>`

### Response

- Status Code: `200 OK`

## Token Yenileme

Token'ı yenilemek için aşağıdaki yöntemi kullanabilirsiniz:

### Request

- URL: `/token/refresh/`
- HTTP Method: `POST`
- Headers:
  - `Authorization: Bearer <refresh_token_here>`

### Response

- Status Code: `200 OK`
- Response Body:

```json
{
  "access": "new_access_token_here"
}
```

Bu dökümantasyon, AuthCentral API'nin temel işlevselliğini açıklar. API kullanımı hakkında daha fazla ayrıntı için ilgili endpoint belgelerine başvurabilirsiniz.
```