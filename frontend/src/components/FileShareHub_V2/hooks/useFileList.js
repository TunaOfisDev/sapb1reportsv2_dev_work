// frontend/src/components/FileShareHub_V2/hooks/useFileList.js
import { useState, useEffect } from "react";
import { fetchFileList } from "../api/fileApi";

export default function useFileList(initialPath = "") {
  const [path, setPath] = useState(initialPath);
  const [data, setData] = useState({ directories: [], files: [] });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);

  useEffect(() => {
    setData({ directories: [], files: [] });
    setPage(1);
  }, [path]);

  useEffect(() => {
    let isMounted = true;
    const loadFiles = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetchFileList(path, page);
        if (!isMounted) return;
        setData((prev) => ({
          directories: page === 1 ? res.directories : prev.directories,
          files: page === 1 ? res.files : [...prev.files, ...res.files],
        }));
        setHasMore(res.files.length > 0);
      } catch (err) {
        console.error("useFileList error:", err);
        if (isMounted) setError("Veri alınamadı.");
      } finally {
        if (isMounted) setLoading(false);
      }
    };
    loadFiles();
    return () => {
      isMounted = false;
    };
  }, [path, page]);

  return {
    data,
    path,
    setPath,
    loading,
    error,
    page,
    setPage,
    hasMore,
  };
}
