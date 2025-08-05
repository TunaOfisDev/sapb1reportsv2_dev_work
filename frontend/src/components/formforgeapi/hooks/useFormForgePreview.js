// path: frontend/src/components/formforgeapi/hooks/useFormForgePreview.js
import { useMemo, useEffect } from 'react';
import { useForm } from 'react-hook-form';

/**
 * FormForge Preview Hook
 * --------------------------------------------------------------------
 * Bu hook, form tasarımcısının "Önizleme" modu için gerekli olan mantığı yönetir.
 *
 * Sorumlulukları:
 * - Verilen form şemasına (`form.fields`) dayanarak `react-hook-form`'u başlatır.
 * - Alanlar için dinamik olarak `defaultValues` ve temel doğrulama kuralları oluşturur.
 * - Önizleme modunda "Gönder" butonuna basıldığında, API'ye gerçek bir istek göndermeden
 * verilerin nasıl toplanacağını simüle eder ve kullanıcıya gösterir.
 * - Formun kontrolünü ve hata durumlarını (`control`, `errors`) dışarıya aktararak
 * dinamik bir form render edilmesini sağlar.
 *
 * @param {Object|null} form - Önizlemesi yapılacak olan ve `fields` dizisini içeren form nesnesi.
 */
export default function useFormForgePreview(form) {
  // 1. Dinamik `defaultValues` oluşturma
  // react-hook-form'un formu başlatabilmesi için alanlara göre varsayılan değerler oluşturulur.
  const defaultValues = useMemo(() => {
    if (!form?.fields) return {};

    const values = {};
    form.fields.forEach(field => {
      // Alan tipine göre varsayılan değer ata.
      switch (field.field_type) {
        case 'checkbox':
          values[field.id] = false;
          break;
        case 'multiselect':
          values[field.id] = [];
          break;
        default:
          values[field.id] = '';
      }
    });
    return values;
  }, [form]);

  // 2. `react-hook-form`'u başlatma
  const {
    control,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm({
    defaultValues,
  });

  // 3. Tasarımcıda form şeması değiştiğinde (örn: yeni alan eklendiğinde)
  // `react-hook-form`'un state'ini yeni `defaultValues` ile güncelle.
  useEffect(() => {
    reset(defaultValues);
  }, [defaultValues, reset]);

  // 4. "Sahte" gönderme işlemi
  // Bu fonksiyon, form gönderildiğinde çalışır ancak API'ye gitmez.
  const onPreviewSubmit = (data) => {
    console.log("--- FORM ÖNİZLEME VERİSİ ---", data);
    alert(
      "Bu bir önizlemedir. Veriler kaydedilmedi.\n\n" +
      "Toplanan verileri görmek için geliştirici konsolunu kontrol edin."
    );
  };

  // 5. Hook'un dışarıya açtığı arayüz
  return {
    /**
     * `react-hook-form`'dan gelen kontrol nesnesi.
     * Form elemanlarını `react-hook-form`'a bağlamak için kullanılır.
     */
    control,

    /**
     * Formdaki doğrulama hatalarını içeren nesne.
     */
    errors,

    /**
     * Önizleme formunun gönderimini yöneten fonksiyon.
     * Formun `onSubmit` olayına bağlanmalıdır.
     * Örn: `<form onSubmit={handlePreviewSubmit}>`
     */
    handlePreviewSubmit: handleSubmit(onPreviewSubmit),
  };
}