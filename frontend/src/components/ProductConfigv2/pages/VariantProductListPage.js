// frontend/src/components/ProductConfigv2/pages/VariantProductListPage.js

import React, { useEffect, useMemo, useState } from 'react';
import { useTable, usePagination, useGlobalFilter } from 'react-table';
import { Link } from 'react-router-dom'; // YENİ: Link bileşenini import ediyoruz
import { List } from 'lucide-react'; // YENİ: İkon için import
import { getProducts } from '../api/configApi';
import '../styles/ProductManager.css';

const VariantProductListPage = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await getProducts();
        setProducts(response.data.results || []);
      } catch (error) {
        console.error('Ürünler alınırken hata oluştu:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, []);

  const columns = useMemo(
    () => [
      { Header: 'Ürün Kodu', accessor: 'code' },
      { Header: 'Açıklama', accessor: 'name' },
      { Header: 'Fiyat', accessor: 'base_price', Cell: ({ value }) => `${value} EUR` },
      {
        Header: 'Konfigüre Et',
        accessor: 'id',
        Cell: ({ value }) => (
          <a className="configure-link" href={`/configurator-v2/${value}`}>Yapılandır</a>
        ),
      },
    ],
    []
  );

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    page,
    prepareRow,
    setGlobalFilter,
    state: { globalFilter },
  } = useTable({
    columns,
    data: products,
    initialState: { pageSize: 10 },
  }, useGlobalFilter, usePagination);

  if (loading) return <div className="product-manager__loading">Ürünler yükleniyor...</div>;

  return (
    <div className="product-manager">
      {/* GÜNCELLEME: Başlık ve butonu içeren yeni bir header alanı */}
      <div className="product-manager__header">
        <h2 className="product-manager__title">Konfigüre Edilebilir Ürünler</h2>
        <Link to="/variants" className="product-manager__action-link">
          <List size={18} />
          <span>Varyant Listesi</span>
        </Link>
      </div>

      <input
        value={globalFilter || ''}
        onChange={(e) => setGlobalFilter(e.target.value)}
        placeholder=" Ürün ara..."
        className="search-input"
      />
      <div className="product-table-wrapper">
        <table {...getTableProps()} className="product-table">
          <thead>
            {headerGroups.map(headerGroup => (
              <tr {...headerGroup.getHeaderGroupProps()}>
                {headerGroup.headers.map(column => (
                  <th {...column.getHeaderProps()}>{column.render('Header')}</th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody {...getTableBodyProps()}>
            {page.map(row => {
              prepareRow(row);
              return (
                <tr {...row.getRowProps()}>
                  {row.cells.map(cell => (
                    <td {...cell.getCellProps()}>{cell.render('Cell')}</td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default VariantProductListPage;