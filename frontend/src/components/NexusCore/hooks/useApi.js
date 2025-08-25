/* path: frontend/src/components/NexusCore/hooks/useApi.js */

import { useState, useCallback } from 'react';

/**
 * API isteklerini yönetmek için jenerik bir custom hook.
 *
 * @param {Function} apiFunc - Çalıştırılacak olan API fonksiyonu (örn: connectionsApi.getConnections).
 * @returns {{
 * data: any | null,
 * error: Error | null,
 * loading: boolean,
 * request: (...args: any[]) => Promise<void>
 * }}
 * - data: API'den başarıyla dönen veri.
 * - error: İstek sırasında oluşan hata.
 * - loading: İsteğin devam edip etmediğini belirten boolean.
 * - request: API isteğini tetikleyen fonksiyon.
 */
export const useApi = (apiFunc) => {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  // useCallback, `request` fonksiyonunun gereksiz yere yeniden oluşturulmasını engeller.
  // Bu, özellikle bu fonksiyonu useEffect dependency array'ine koyduğumuzda önemlidir.
  const request = useCallback(async (...args) => {
    setLoading(true);
    setError(null); // Yeni bir istek başlarken eski hataları temizle.
    try {
      const result = await apiFunc(...args);
      setData(result);
      // Başarılı olursa, bileşenin kullanabilmesi için sonucu döndürebiliriz.
      return { success: true, data: result };
    } catch (err) {
      setError(err);
      // Hata olursa, hatayı da döndürelim.
      return { success: false, error: err };
    } finally {
      // Ne olursa olsun, işlem bittiğinde loading state'ini kapat.
      setLoading(false);
    }
  }, [apiFunc]);

  return { data, error, loading, request };
};

/* Not: Bu hook'u export default yapmıyoruz ki, 
   gelecekte başka hook'lar da bu dosyaya ekleyebilelim. */