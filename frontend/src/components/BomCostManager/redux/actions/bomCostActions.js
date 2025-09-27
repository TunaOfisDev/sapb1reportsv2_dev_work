// frontend/src/components/BomCostManager/redux/actions/bomCostActions.js

import {
    FETCH_BOM_COST_REQUEST,
    FETCH_BOM_COST_SUCCESS,
    FETCH_BOM_COST_FAILURE,
    UPDATE_BOM_COMPONENT_REQUEST,
    UPDATE_BOM_COMPONENT_SUCCESS,
    UPDATE_BOM_COMPONENT_FAILURE
} from '../types';
import {
    fetchBomComponents,  // Servis katmanında tanımladığımız fonksiyon
    updateBomComponent
} from '../../services/bcm_bomCostApi';

/**
 * Gelen BOM verisini, backend/HANA'daki alan adlarıyla
 * front-end'deki (Redux/Tablo) alan adlarını eşleştiren normalizasyon fonksiyonu.
 */
function normalizeBomData(apiData) {
    return apiData.map(item => ({
        // Models.py alanları -> HANA verisi
        // (nullish coalescing '??' ile yoksa varsayılan değer veriyoruz)
        main_item: item.MainItem,
        sub_item: item.SubItem,
        component_item_code: item.ComponentItemCode,
        component_item_name: item.ComponentItemName,
        quantity: item.Quantity ?? 0,
        level: item.Level ?? 0,
        type_description: item.TypeDescription ?? '',
        last_purchase_price: item.LastPurchasePrice ?? 0,
        currency: item.Currency ?? 'TRY',
        rate: item.Rate ?? 1,
        last_purchase_price_upb: item.LastPurchasePriceUPB ?? 0,
        price_source: item.PriceSource ?? 'Taban Fiyat',
        doc_date: item.DocDate ?? null,
        component_cost_upb: item.ComponentCostUPB ?? 0,
        sales_price: item.SalesPrice ?? 0,
        sales_currency: item.SalesCurrency ?? 'TRY',
        price_list_name: item.PriceListName ?? 'YOK',
        item_group_name: item.ItemGroupName ?? null,

        // Aşağıdakiler override alanları, SAP verisinde yoksa sıfır veya varsayılan
        new_last_purchase_price: item.NewLastPurchasePrice ?? 0,
        new_currency: item.NewCurrency ?? '',
        labor_multiplier: item.LaborMultiplier ?? 1,
        overhead_multiplier: item.OverheadMultiplier ?? 1,
        license_multiplier: item.LicenseMultiplier ?? 1,
        commission_multiplier: item.CommissionMultiplier ?? 1,
        updated_cost: item.UpdatedCost ?? 0
    }));
}

/**
 * BOM bileşenlerini getirmek için Redux action'ı.
 * @param {string} itemCode - Hangi mamul için BOM çekilecek.
 */
export const fetchBomCost = (itemCode) => async (dispatch) => {
    dispatch({ type: FETCH_BOM_COST_REQUEST });
    try {
        // HANA/Backend'den ham veriyi çek
        const data = await fetchBomComponents(itemCode);
        console.log('Fetched BOM Data:', data);

        // Gelen veriyi front-end koduna uyarlayalım
        const normalizedData = normalizeBomData(data);
        console.log('Normalized BOM Data:', normalizedData);

        // Redux store'a normalleştirilmiş veriyi gönder
        dispatch({ type: FETCH_BOM_COST_SUCCESS, payload: normalizedData });
    } catch (error) {
        console.error('BOM Data Fetch Error:', error);
        dispatch({ type: FETCH_BOM_COST_FAILURE, payload: error.message });
    }
};

/**
 * Belirli bir BOM bileşenini güncellemek için Redux action'ı.
 * @param {string} componentId - Güncellenecek bileşen ID'si.
 * @param {Object} updatedData - Güncellenmiş veri objesi.
 */
export const updateBomCostComponent = (componentId, updatedData) => async (dispatch) => {
    dispatch({ type: UPDATE_BOM_COMPONENT_REQUEST });
    try {
        const updatedComponent = await updateBomComponent(componentId, updatedData);
        dispatch({ type: UPDATE_BOM_COMPONENT_SUCCESS, payload: updatedComponent });
    } catch (error) {
        dispatch({ type: UPDATE_BOM_COMPONENT_FAILURE, payload: error.message });
    }
};
