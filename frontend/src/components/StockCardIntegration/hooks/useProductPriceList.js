// frontend/src/components/StockCardIntegration/hooks/useProductPriceList.js

import { useEffect } from 'react';
import useSWR from 'swr';
import { fetchLiveProductPriceList } from '../api/productPriceListApi';

/**
 * WebSocket destekli ürün fiyat listesi hook'u.
 * - İlk veri çekme: REST API (GET /product-price-list/live/)
 * - Canlı güncelleme: WebSocket tetiklenirse mutate() çağrılır.
 */
const useProductPriceList = () => {
  const { data, error, mutate, isValidating } = useSWR(
    'product-price-list-live',
    fetchLiveProductPriceList,
    {
      refreshInterval: 0,           // Biz manuel yöneteceğiz
      revalidateOnFocus: false,     // Sayfa odaklandığında tekrar fetch etmesin
      shouldRetryOnError: false,
    }
  );

  // WebSocket üzerinden canlı güncelleme desteği
  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const host = window.location.host;
    const ws = new WebSocket(`${protocol}://${host}/ws/price-list/`);

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        if (message.action === 'refresh') {
          mutate(); // yeniden veri çek
        }
      } catch (err) {
        console.warn('WS mesajı çözümlenemedi:', err);
      }
    };

    return () => {
      ws.close();
    };
  }, [mutate]);

  return {
    productPriceList: data || [],
    isLoading: !data && !error,
    isRefreshing: isValidating,
    error,
    refresh: mutate,
  };
};

export default useProductPriceList;
