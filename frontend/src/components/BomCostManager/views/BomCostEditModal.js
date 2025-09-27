// frontend/src/components/BomCostManager/views/BomCostEditModal.js

import React, { useState } from 'react';
import '../css/BomCostEditModal.css';

const BomCostEditModal = ({ component, onClose, onSave }) => {
    const [updatedPrice, setUpdatedPrice] = useState(component.new_last_purchase_price || component.last_purchase_price);

    const handleSave = () => {
        onSave({ ...component, new_last_purchase_price: updatedPrice });
        onClose();
    };

    return (
        <div className="bom-cost-edit-modal">
            <div className="bom-cost-edit-modal__container">
                <h2 className="bom-cost-edit-modal__header">BOM Bileşeni Düzenle</h2>
                <div className="bom-cost-edit-modal__form">
                    <label className="bom-cost-edit-modal__label">Bileşen Kodu:</label>
                    <p className="bom-cost-edit-modal__text">{component.component_item_code}</p>
                    
                    <label className="bom-cost-edit-modal__label">Bileşen Adı:</label>
                    <p className="bom-cost-edit-modal__text">{component.component_item_name}</p>
                    
                    <label className="bom-cost-edit-modal__label">Yeni Fiyat:</label>
                    <input
                        type="number"
                        className="bom-cost-edit-modal__input"
                        value={updatedPrice}
                        onChange={(e) => setUpdatedPrice(parseFloat(e.target.value) || 0)}
                    />
                </div>
                <div className="bom-cost-edit-modal__buttons">
                    <button className="bom-cost-edit-modal__button bom-cost-edit-modal__button--save" onClick={handleSave}>
                        Kaydet
                    </button>
                    <button className="bom-cost-edit-modal__button bom-cost-edit-modal__button--cancel" onClick={onClose}>
                        İptal
                    </button>
                </div>
            </div>
        </div>
    );
};

export default BomCostEditModal;
