// path: frontend/src/components/formforgeapi/hooks/useDebounce.js

import { useState, useEffect } from 'react';

/**
 * Bir değeri geciktirerek (debounce) döndüren custom hook.
 * Kullanıcı yazmayı bıraktıktan sonra API isteği yapmak gibi durumlar için idealdir.
 * @param {*} value - Geciktirilecek değer (örn: input'taki metin).
 * @param {number} delay - Milisaniye cinsinden gecikme süresi.
 * @returns {*} Geciktirilmiş değer.
 */
export function useDebounce(value, delay) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    // Değer değiştiğinde bir zamanlayıcı başlat
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    // Bir sonraki effect çalışmadan veya component unmount olmadan önce
    // zamanlayıcıyı temizle.
    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]); // Sadece value veya delay değiştiğinde yeniden çalıştır.

  return debouncedValue;
}
