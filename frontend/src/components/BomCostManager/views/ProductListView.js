// frontend/src/components/BomCostManager/views/ProductListView.js

import React from 'react';
import useProductSelection from '../hooks/useProductSelection';
import '../css/ProductListView.css';

const ProductListView = ({ onSelectProduct }) => {
    const { products, selectedProduct, setSelectedProduct, loading, error } = useProductSelection();

    if (loading) return <p className="product-list-view__loading">Yükleniyor...</p>;
    if (error) return <p className="product-list-view__error">Hata: {error}</p>;

    return (
        <div className="product-list-view">
            <h2 className="product-list-view__header">Ürün Listesi</h2>
            <input
                type="text"
                className="product-list-view__search"
                placeholder="Ürün ara..."
                onChange={(e) => {
                    const searchValue = e.target.value.toLowerCase();
                    setSelectedProduct(
                        products.find((product) =>
                            product.item_name.toLowerCase().includes(searchValue)
                        ) || null
                    );
                }}
            />
            <div className="product-list-view__grid">
                {products.map((product) => (
                    <div
                        key={product.item_code}
                        className={`product-list-view__card ${
                            selectedProduct?.item_code === product.item_code ? 'product-list-view__card--selected' : ''
                        }`}
                        onClick={() => {
                            setSelectedProduct(product);
                            if (onSelectProduct) onSelectProduct(product);
                        }}
                    >
                        <h3 className="product-list-view__card-title">{product.item_name}</h3>
                        <p className="product-list-view__card-description">Kodu: {product.item_code}</p>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ProductListView;
