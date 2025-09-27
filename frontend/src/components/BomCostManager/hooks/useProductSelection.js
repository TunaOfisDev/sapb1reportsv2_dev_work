// frontend/src/components/BomCostManager/hooks/useProductSelection.js

import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchProducts } from '../redux/actions/productActions';

/**
 * Kullanıcının BOM ürünlerini seçmesi ve yönetmesi için özel hook.
 * @returns {{ products: Array, selectedProduct: Object, setSelectedProduct: Function, loading: boolean, error: string }}
 */
const useProductSelection = () => {
    const dispatch = useDispatch();
    const { products, loading, error } = useSelector((state) => state.product);
    const [selectedProduct, setSelectedProduct] = useState(null);

    useEffect(() => {
        dispatch(fetchProducts());
    }, [dispatch]);

    return { products, selectedProduct, setSelectedProduct, loading, error };
};

export default useProductSelection;
