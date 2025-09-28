// frontend/src/components/ProductConfigv2/pages/VariantListPage.js

import React, { useEffect, useMemo, useState, useCallback } from 'react';
import { useTable, usePagination, useSortBy } from 'react-table';
import { Link } from 'react-router-dom'; // YENİ: Link bileşenini import ediyoruz
import { PackagePlus } from 'lucide-react'; // YENİ: İkon için import
import { format } from 'date-fns';
import configApi from '../api/configApi';
import '../styles/VariantListPage.css';

const VariantListPage = () => {
  const [variants, setVariants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Filtre inputlarının anlık değerini tutar
  const [filters, setFilters] = useState({
    project_name: '',
    reference_code: '',
    new_variant_code: '',
  });

  // API isteğini tetikleyecek olan, geciktirilmiş filtre değerini tutar
  const [debouncedFilters, setDebouncedFilters] = useState(filters);

  // Debouncing için useEffect: Kullanıcı yazmayı bıraktıktan 500ms sonra aramayı tetikler
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedFilters(filters);
    }, 500);

    // Kullanıcı yeni bir tuşa basarsa, önceki zamanlayıcıyı iptal et
    return () => {
      clearTimeout(handler);
    };
  }, [filters]);

  // Veri çekme fonksiyonu
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // Sadece dolu olan filtreleri API'ye gönder
      const activeFilters = Object.fromEntries(
        Object.entries(debouncedFilters).filter(([, value]) => value)
      );
      const response = await configApi.getVariants(activeFilters);
      setVariants(response.data.results || []);
    } catch (err) {
      console.error('Varyantlar alınırken hata oluştu:', err);
      setError('Varyantlar yüklenemedi.');
    } finally {
      setLoading(false);
    }
  }, [debouncedFilters]);

  // Filtreler değiştiğinde veriyi yeniden çek
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const columns = useMemo(
    () => [
      { Header: 'Proje Adı', accessor: 'project_name' },
      { Header: 'Referans Kod (55\'li)', accessor: 'reference_code' },
      { Header: 'Üretim Kodu (30\'lu)', accessor: 'new_variant_code' },
      { Header: 'Açıklama', accessor: 'new_variant_description', width: 300 },
      { Header: 'Fiyat', accessor: 'total_price', Cell: ({ value }) => `${parseFloat(value).toFixed(2)} EUR` },
      { Header: 'Oluşturan', accessor: 'created_by_username' },
      { Header: 'Tarih', accessor: 'created_at', Cell: ({ value }) => format(new Date(value), 'dd.MM.yyyy HH:mm') },
    ],
    []
  );

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    page,
    prepareRow,
    canPreviousPage,
    canNextPage,
    pageOptions,
    nextPage,
    previousPage,
    state: { pageIndex },
  } = useTable({
    columns,
    data: variants,
    initialState: { pageSize: 15 },
  }, useSortBy, usePagination);
  
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  return (
    <div className="variant-list-page">
      <div className="variant-list-page__header">
        <h2 className="variant-list-page__title">Oluşturulan Varyantlar</h2>
        <Link to="/configurator-v2" className="variant-list-page__action-link">
          <PackagePlus size={18} />
          <span>Yeni Konfigürasyon</span>
        </Link>
      </div>
      
      <div className="variant-list-page__filters">
        <input name="project_name" value={filters.project_name} onChange={handleFilterChange}
          placeholder="Proje Adına Göre Ara..." className="variant-list-page__filter-input" />
        <input name="reference_code" value={filters.reference_code} onChange={handleFilterChange}
          placeholder="Referans Koduna Göre Ara..." className="variant-list-page__filter-input" />
        <input name="new_variant_code" value={filters.new_variant_code} onChange={handleFilterChange}
          placeholder="Üretim Koduna Göre Ara..." className="variant-list-page__filter-input" />
      </div>

      {loading && <div className="variant-list-page__loading">Yükleniyor...</div>}
      {error && <div className="variant-list-page__error">{error}</div>}
      
      {!loading && !error && (
        <>
          <div className="variant-list-page__table-wrapper">
            <table {...getTableProps()} className="variant-list-page__table">
              <thead>
                {headerGroups.map(headerGroup => (
                  <tr {...headerGroup.getHeaderGroupProps()}>
                    {headerGroup.headers.map(column => (
                      <th {...column.getHeaderProps(column.getSortByToggleProps())} className="variant-list-page__table-header variant-list-page__table-header--sortable">
                        {column.render('Header')}
                        <span>{column.isSorted ? (column.isSortedDesc ? ' 🔽' : ' 🔼') : ''}</span>
                      </th>
                    ))}
                  </tr>
                ))}
              </thead>
              <tbody {...getTableBodyProps()}>
                {page.map(row => {
                  prepareRow(row);
                  return (
                    <tr {...row.getRowProps()} className="variant-list-page__table-row">
                      {row.cells.map(cell => (
                        <td {...cell.getCellProps()} className="variant-list-page__table-cell">{cell.render('Cell')}</td>
                      ))}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          <div className="variant-list-page__pagination">
            <button onClick={() => previousPage()} disabled={!canPreviousPage}>{'<'}</button>
            <span>Sayfa <strong>{pageIndex + 1} / {pageOptions.length}</strong></span>
            <button onClick={() => nextPage()} disabled={!canNextPage}>{'>'}</button>
          </div>
        </>
      )}
    </div>
  );
};

export default VariantListPage;