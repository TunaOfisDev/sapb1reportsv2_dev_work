# File: backend/report_orchestrator/utils/lock_utils.py

from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class TaskLock:
    """
    Basit bir cache tabanlı görev kilitleyici.
    Aynı görev eşzamanlı çalışmasın diye Redis üzerinden lock kullanır.
    """

    def __init__(self, key: str, timeout: int = 300):
        """
        :param key: Benzersiz lock anahtarı (örnek: 'report_lock_custumer_balance_top20')
        :param timeout: Lock'un saniye bazlı süresi (varsayılan: 300 saniye)
        """
        self.key = f"tasklock:{key}"
        self.timeout = timeout
        self.acquired = False

    def acquire(self) -> bool:
        """Lock'u alır. Eğer başka işlem o anda lock'u almışsa False döner."""
        self.acquired = cache.add(self.key, "locked", self.timeout)
        if not self.acquired:
            logger.warning(f"[LOCK] Aktif lock bulundu: {self.key}")
        return self.acquired

    def release(self):
        """Eğer lock bu işlem tarafından alındıysa bırakır."""
        if self.acquired:
            cache.delete(self.key)
            logger.info(f"[LOCK] Lock serbest bırakıldı: {self.key}")
