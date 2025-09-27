// frontend/src/components/BomCostManager/hooks/useFetchBomCost.js

import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchBomCost } from '../redux/actions/bomCostActions';
import { useParams } from 'react-router-dom';

/**
 * BOM bileşenlerini Redux store üzerinden çekmek için özel hook.
 * @returns {{ bomComponents: Array, loading: boolean, error: string }}
 */
const useFetchBomCost = () => {
    const dispatch = useDispatch();
    const { itemCode } = useParams(); // URL'den itemCode parametresini al

    const { bomComponents, loading, error } = useSelector((state) => state.bomCost);

    useEffect(() => {
        if (itemCode) {
            console.log("Fetching BOM Data for:", itemCode); // Debugging için log
            dispatch(fetchBomCost(itemCode));
        }
    }, [dispatch, itemCode]);

    console.log("BOM Components from Redux:", bomComponents); // Debugging için log

    return { bomComponents, loading, error };
};

export default useFetchBomCost;
