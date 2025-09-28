
// frontend/src/components/ProductConfigv2/pages/VariantListPage.js

import React, { useEffect, useMemo, useState } from 'react';
import { useTable, usePagination, useSortBy } from 'react-table';
import { Link } from 'react-router-dom';
import { PackagePlus } from 'lucide-react';
import { format } from 'date-fns';
import configApi from '../api/configApi';
import { normalizeForSearch } from '../utils/textUtils'; // YENİ: Arama fonksiyonumuzu import ediyoruz
import '../styles/VariantListPage.css';

const VariantListPage = () => {
  const [allVariants, setAllVariants] = useState([]); // Tüm varyantları burada tutacağız
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [filters, setFilters] = useState({
    project_name: '',
    reference_code: '',
    new_variant_code: '',
  });

  // Veriyi sadece component ilk yüklendiğinde çek
  useEffect(() => {
    const fetchAllData = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await configApi.getVariants(); // Filtresiz tüm veriyi çek
        setAllVariants(response.data.results || []);
      } catch (err) {
        setError('Varyantlar yüklenemedi.');
      } finally {
        setLoading(false);
      }
    };
    fetchAllData();
  }, []);

  // GÜNCELLEME: Filtreleme mantığı artık React içinde
  const filteredVariants = useMemo(() => {
    return allVariants.filter(variant => {
      const normalizedProjectName = normalizeForSearch(variant.project_name);
      const normalizedSearchTerm = normalizeForSearch(filters.project_name);

      const projectNameMatch = filters.project_name ? normalizedProjectName.includes(normalizedSearchTerm) : true;
      const referenceCodeMatch = filters.reference_code ? variant.reference_code.toLowerCase().includes(filters.reference_code.toLowerCase()) : true;
      const newVariantCodeMatch = filters.new_variant_code ? variant.new_variant_code.toLowerCase().includes(filters.new_variant_code.toLowerCase()) : true;

      return projectNameMatch && referenceCodeMatch && newVariantCodeMatch;
    });
  }, [allVariants, filters]);

  const columns = useMemo(() => [
      { 
        Header: 'Proje Adı', 
        accessor: 'project_name',
        Cell: ({ value }) => {const truncatedText = value && value.length > 50 ? `${value.substring(0, 50)}...` : value;
          return (
            <span title={value}>{truncatedText || '---'} </span>
          );
        }
      },
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
    getTableProps, getTableBodyProps, headerGroups, page, prepareRow,
    canPreviousPage, canNextPage, pageOptions, nextPage, previousPage,
    state: { pageIndex },
  } = useTable(
    { columns, data: filteredVariants, initialState: { pageSize: 15 } }, 
    useSortBy, usePagination
  );
  
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };;

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
                        <span>{column.isSorted ? (column.isSortedDesc ? ' ??' : ' ??') : ''}</span>
                      </th>
                    ))}
                  </tr>
                ))}
              </thead>
              <tbody {...getTableBodyProps()}>
                {page.length > 0 ? (
                  page.map(row => {
                    prepareRow(row);
                    return (
                      <tr {...row.getRowProps()} className="variant-list-page__table-row">
                        {row.cells.map(cell => (
                          <td {...cell.getCellProps()} className="variant-list-page__table-cell">{cell.render('Cell')}</td>
                        ))}
                      </tr>
                    );
                  })
                ) : (
                  <tr>
                    <td colSpan={columns.length} style={{ textAlign: 'center', padding: '20px' }}>
                      Arama kriterlerinize uygun sonuç bulunamadı.
                    </td>
                  </tr>
                )}
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