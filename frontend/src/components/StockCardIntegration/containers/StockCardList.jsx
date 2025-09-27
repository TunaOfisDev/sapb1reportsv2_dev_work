// frontend/src/components/StockCardIntegration/containers/StockCardList.jsx
import React, { useEffect, useState, useMemo } from "react";
import styles from "../css/StockCardList.module.css";
import { fetchStockCards } from "../api/stockCardApi";
import useApiStatus from "../hooks/useApiStatus";

const PAGE_SIZE = 20;

const statusLabels = {
  completed: "✅ Tamamlandı",
  failed: "❌ Hatalı",
  pending: "⌛ Beklemede",
};

const formatDate = (isoDate) => {
  if (!isoDate) return "-";
  const d = new Date(isoDate);
  return `${d.getDate().toString().padStart(2, "0")}.${(d.getMonth() + 1)
    .toString()
    .padStart(2, "0")}.${d.getFullYear()}`;
};

const getUserShort = (email) => email?.split("@")[0] || "-";

export default function StockCardList() {
  const [items, setItems] = useState([]);
  const [page, setPage] = useState(0);

  /* loading / error helpers */
  const { loading, error, start, fail, succeed } = useApiStatus();

  /** ------------------------------------------------------------------
   *  Veriyi yalnızca mount’ta çek – bağımlılık listesine;
   *  start / fail / succeed referansları eklendi (stable hook’lar)
   *  ------------------------------------------------------------------ */
  useEffect(() => {
    const fetchData = async () => {
      start();
      try {
        const data = await fetchStockCards();
        const sorted = data.sort(
          (a, b) => new Date(b.created_at) - new Date(a.created_at)
        );
        setItems(sorted);
        succeed();
      } catch (err) {
        fail(err);
      }
    };
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [start, fail, succeed]);

  /** Sayfalama hesaplamaları memoize */
  const paginatedItems = useMemo(
    () => items.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE),
    [items, page]
  );

  const totalPages = useMemo(
    () => Math.ceil(items.length / PAGE_SIZE) || 1,
    [items.length]
  );

  /** ------------------------------------------------------------------ */

  return (
    <div className={styles["stock-card-list"]}>
      <h2 className={styles["stock-card-list__title"]}>Stok Kartları</h2>

      {loading && <p>Yükleniyor…</p>}
      {error && (
        <p style={{ color: "red" }}>
          {error.message || "Beklenmeyen bir hata oluştu"}
        </p>
      )}
      {!loading && items.length === 0 && <p>Henüz stok kartı bulunmuyor.</p>}

      {items.length > 0 && (
        <>
          {/* ----------- Tablo ----------- */}
          <table className={styles["stock-card-list__table"]}>
            <thead>
              <tr>
                <th>ItemCode</th>
                <th>ItemName</th>
                <th>Grup</th>
                <th>Fiyat</th>
                <th>Durum</th>
                <th>İşlem Tarihi</th>
                <th>Kullanıcı</th>
                <th>İşlem Tipi</th>
              </tr>
            </thead>
            <tbody>
              {paginatedItems.map((item) => (
                <tr key={item.id}>
                  <td>{item.item_code}</td>
                  <td>{item.item_name}</td>
                  <td>{item.items_group_code}</td>
                  <td>
                    {item.price} {item.currency}
                  </td>
                  <td>
                    <span
                      className={`${styles["stock-card-list__badge--status"]} ${
                        item.hana_status === "completed"
                          ? styles["stock-card-list__badge--success"]
                          : item.hana_status === "failed"
                          ? styles["stock-card-list__badge--error"]
                          : styles["stock-card-list__badge--pending"]
                      }`}
                    >
                      {statusLabels[item.hana_status] || "❓ Bilinmiyor"}
                    </span>
                  </td>
                  <td>{formatDate(item.created_at)}</td>
                  <td>{getUserShort(item.user_email)}</td>
                  <td>{item.operation === "update" ? "Güncelleme" : "Yeni Kayıt"}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* ----------- Pagination ----------- */}
          <div className={styles["stock-card-list__pagination"]}>
            <button
              className={styles["stock-card-list__pagination-button"]}
              disabled={page === 0}
              onClick={() => setPage((p) => Math.max(p - 1, 0))}
            >
              Önceki
            </button>

            <span>
              Sayfa {page + 1} / {totalPages}
            </span>

            <button
              className={styles["stock-card-list__pagination-button"]}
              disabled={page + 1 >= totalPages}
              onClick={() =>
                setPage((p) => (p + 1 < totalPages ? p + 1 : p))
              }
            >
              Sonraki
            </button>
          </div>
        </>
      )}
    </div>
  );
}


