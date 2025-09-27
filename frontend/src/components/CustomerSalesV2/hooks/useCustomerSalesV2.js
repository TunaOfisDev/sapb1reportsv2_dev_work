import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import customerSalesApi from '../api/customerSalesApi';

/**
 * CustomerSalesV2 raporu için tüm veri, state ve iş mantığını yöneten custom hook.
 *
 * Bu hook, @tanstack/react-query kullanarak aşağıdaki işlemleri gerçekleştirir:
 * - Rapor verilerini (data, summary, filterOptions) API'den çeker.
 * - Veri çekme sırasındaki yüklenme (loading) ve hata (error) durumlarını yönetir.
 * - HANA'dan veri senkronizasyonunu tetikleyecek bir fonksiyon sağlar.
 * - Senkronizasyon sonrası rapor verilerini otomatik olarak yeniler.
 *
 * @param {object} filters - Rapor verilerini getirmek için kullanılacak filtreler. Filtreler değiştiğinde veri otomatik olarak yeniden çekilir.
 * @returns {object} Bileşenlerin ihtiyaç duyacağı tüm state'leri ve fonksiyonları içeren bir nesne.
 */
const useCustomerSalesV2 = (filters) => {
  const queryClient = useQueryClient();

  // 1. Rapor Verisini Çekmek İçin `useQuery`
  // 'queryKey', bu veriyi önbellekte (cache) saklamak için kullanılan eşsiz bir anahtardır.
  // `filters` objesi anahtara dahil edildiği için, filtreler her değiştiğinde React Query veriyi yeniden çeker.
  const {
    data: reportPayload, // Gelen veriyi 'reportPayload' olarak isimlendiriyoruz
    isLoading: isLoadingReport,
    isError: isReportError,
    error: reportError,
  } = useQuery({
    queryKey: ['customerSalesData', filters],
    queryFn: () => customerSalesApi.getReportData(filters),
    staleTime: 5 * 60 * 1000, // Veri 5 dakika boyunca 'taze' kabul edilecek, tekrar istek atılmayacak.
    refetchOnWindowFocus: false, // Kullanıcı pencereye geri döndüğünde otomatik yenileme yapma.
    placeholderData: (previousData) => previousData, // Yeni veri yüklenirken eski veriyi ekranda tut (UX için).
  });

  // 2. HANA Senkronizasyonunu Tetiklemek İçin `useMutation`
  // `useMutation`, veri çeken (GET) değil, veri değiştiren (POST, PUT, DELETE) işlemler için kullanılır.
  const {
    mutate: triggerSync, // Fonksiyonu 'triggerSync' olarak isimlendiriyoruz
    isPending: isSyncing, // `isLoading` yerine `isPending` kullanılır
    isSuccess: isSyncSuccess,
    isError: isSyncError,
    error: syncError,
  } = useMutation({
    mutationFn: customerSalesApi.triggerHanaSync, // Hangi API fonksiyonunu çalıştıracağı
    onSuccess: () => {
      // Mutasyon (veri çekme) başarılı olduğunda, 'customerSalesData' anahtarına sahip
      // tüm sorguları 'bayat' olarak işaretle. Bu, React Query'nin rapor verisini
      // otomatik olarak yeniden çekmesini tetikler.
      queryClient.invalidateQueries({ queryKey: ['customerSalesData'] });
    },
  });

  // 3. Hook'un Dışarıya Sağlayacağı Değerler
  // Gelen veriyi ve state'leri UI bileşenlerinin kolayca kullanabileceği bir formatta döndürüyoruz.
  return {
    // Rapor Verileri
    reportData: reportPayload?.data || [],
    summaryData: reportPayload?.summary || {},
    filterOptions: reportPayload?.filterOptions || {},
    lastUpdated: reportPayload?.lastUpdated || 'N/A',
    
    // Rapor Yüklenme Durumları
    isLoadingReport,
    isReportError,
    reportError,

    // Senkronizasyon Fonksiyonu ve Durumları
    triggerSync,
    isSyncing,
    isSyncSuccess,
    isSyncError,
    syncError,
  };
};

export default useCustomerSalesV2;