# zcontext_prompt/frontend_context.md
# ============================================================================
# CONTEXT-2: SAPB1ReportsV2 Frontend Anayasası v3.1
# ============================================================================
# v3.1 GÜNCELLEMESİ:
# - Üretim hatalarını önlemek için en kritik dosyalar (hooks, css)
#   zorunlu üretim listesinin başına alındı.
# - Öncelikleri vurgulamak için bir "ANA DİREKTİF" eklendi.
# - Frontend dosyaları (.js, .jsx) için DOSYA YOLU YORUMU kuralı
#   açık ve net bir şekilde eklendi.
# ============================================================================

# ----------------------------------------------------------------------------
# ANA DİREKTİF: ÜRETİM ÖNCELİKLERİ
# ----------------------------------------------------------------------------
# 1. Her ne olursa olsun, BÖLÜM 2'deki 16 maddelik listenin TAMAMI üretilmelidir.
# 2. Üretim sırasına listenin başından başlanmalıdır.
# 3. En yüksek öncelik, "modülün beyni" olan `hooks` ve stil dosyalarını içeren
#    `css` klasörlerinin oluşturulmasıdır.
# ----------------------------------------------------------------------------

## 1. 🎯 Felsefe ve Amaç
Amacımız, statik CRUD ekranları üretmek değil; kullanıcıya Bitrix24 CRM benzeri, kendi arayüzlerini ve formlarını tasarlama gücü veren, "canlı" ve interaktif modüller inşa etmektir. AI, bu belgedeki kuralları bir anayasa olarak kabul etmek zorundadır.

---

## 2. 📁 Zorunlu Üretim Listesi ve Modül Anatomisi (ÖNCELİK SIRALI)
AI, yeni bir `<module_name>` modülü üretirken, aşağıdaki klasör ve dosyaları **MUTLAKA**, **EKSİKSİZ** ve **AŞAĞIDAKİ SIRAYLA** oluşturmalıdır. Hiçbir parça atlanamaz.

#### Üretim Listesi (Yeni Öncelik Sırası):
1.  **Klasör:** `frontend/src/components/<module_name>/hooks/` **(EN YÜKSEK ÖNCELİK: Modülün beyni)**
2.  **Dosya:** `frontend/src/components/<module_name>/hooks/use<ModuleName>.js` **(EN YÜKSEK ÖNCELİK: Modülün beyni)**
3.  **Klasör:** `frontend/src/components/<module_name>/css/`
4.  **Dosya:** `frontend/src/components/<module_name>/css/<ModuleName>.module.css`
5.  **Klasör:** `frontend/src/components/<module_name>/api/`
6.  **Dosya:** `frontend/src/components/<module_name>/api/<ModuleName>Api.js`
7.  **Klasör:** `frontend/src/components/<module_name>/containers/`
8.  **Dosya:** `frontend/src/components/<module_name>/containers/<ModuleName>Container.jsx`
9.  **Klasör:** `frontend/src/components/<module_name>/components/`
10. **Klasör:** `frontend/src/components/<module_name>/components/page-level/`
11. **Dosya:** `frontend/src/components/<module_name>/components/page-level/FormBuilderScreen.jsx`
12. **Dosya:** `frontend/src/components/<module_name>/components/page-level/FormDataListScreen.jsx`
13. **Dosya:** `frontend/src/components/<module_name>/components/page-level/FormSchemaListScreen.jsx`
14. **Klasör:** `frontend/src/components/<module_name>/components/reusable/`
15. **Dosya:** `frontend/src/components/<module_name>/components/reusable/DataTable.jsx`
16. **Dosya:** `frontend/src/components/<module_name>/components/reusable/SchemaTable.jsx`

---

## 3. 🔗 Kodlama ve Entegrasyon Kuralları

#### 3.1. API Servis Katmanı (KESİNLİKLE UYULACAK KURAL)
- **Tüm backend API istekleri**, modülün kendi `api/<ModuleName>Api.js` dosyası içinde soyutlanmalıdır.
- Hook'lar veya Container'lar **ASLA** doğrudan `axiosClient`'ı çağırmamalıdır.

#### 3.2. Stil Kılavuzu (CSS Kuralları)
- **Yorumlar:** CSS dosyalarındaki yorumlar **mutlaka** `/* Yorum metni */` formatında olmalıdır. `//` kullanımı **YASAKTIR**.
- **BEM ve SAP Paleti:** BEM (`.block__element--modifier`) ve CSS Modules kullanılmalıdır. Renkler **mutlaka** `var(--sap-blue)` gibi `palette.css` dosyasında tanımlı SAP B1 renk değişkenlerinden alınmalıdır.

#### 3.3. Dosya Yolu Yorumu (YENİ VE KRİTİK KURAL)
- **Tüm `.js` ve `.jsx` dosyaları**, **MUTLAKA** `// path: frontend/src/components/dosya_adi.js` formatında bir yorumla başlamalıdır.
- Bu dosyalarda Python stili olan `#` karakterinin yorum için kullanımı **KESİNLİKLE YASAKTIR**.

---

## 4. 🏆 Proje Standardı Kütüphaneler ve "Usta İşi" Desenler

| Alan | Standart Kütüphane / Desen |
| --- | --- |
| **Dinamik Form Alanları** | **`react-hook-form`** kütüphanesinin **`useFieldArray`** hook'u kullanılmalıdır. Bu, kullanıcının dinamik olarak alan ekleyip çıkarmasını sağlar ve Bitrix24 deneyiminin temelidir. |
| **Veri Tabloları** | **`react-table` v7** kullanılacaktır. `useTable` hook'u ve `useSortBy` gibi plugin'ler ile birlikte, `getTableProps`, `getTableBodyProps`, `headerGroups`, `rows`, `prepareRow` propları doğru şekilde kullanılmalıdır. |
| **Dosya İndirme** | Backend'den gelen `blob` verileri indirmek için **`file-saver`** kütüphanesi kullanılmalıdır. AI, `README.md`'de bu kütüphanenin (`npm install file-saver`) bir bağımlılık olduğunu belirtmelidir. |

---

## 5. 💡 En İyi Pratikler ve "Altın Standart" Kod Örnekleri

#### "Usta İşi" Custom Hook Örneği (`useModuleName.js`)
```javascript
// path: frontend/src/components/<module_name>/hooks/use<ModuleName>.js
import { useState, useCallback } from 'react';
import { toast } from 'react-toastify';
import { <moduleName>Api } from '../api/<ModuleName>Api';

export const use<ModuleName> = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);

    const fetchData = useCallback(async (params) => {
        setLoading(true);
        try {
            const response = await <moduleName>Api.getAll(params);
            setData(response.data.data || []);
        } catch (error) {
            toast.error("Veri alınırken bir hata oluştu.");
        } finally {
            setLoading(false);
        }
    }, []);

    return { data, loading, fetchData };
};