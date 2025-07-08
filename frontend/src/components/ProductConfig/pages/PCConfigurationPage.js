import React, { useState, useCallback, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import PCConfigurationFlow from '../configuration/PCConfigurationFlow';
import PCButton from '../common/PCButton';
import PCModal from '../common/PCModal';
import { 
    selectCurrentVariant, 
    deleteVariant,
    fetchVariantDetails,
    clearCurrentVariant
} from '../store/pcVariantSlice';
import '../css/PCConfigurationPage.css';

const PCConfigurationPage = () => {
    const navigate = useNavigate();
    const dispatch = useDispatch();
    const { variantId } = useParams();
    const currentVariant = useSelector(selectCurrentVariant);
    const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);

    useEffect(() => {
        if (variantId) {
            dispatch(fetchVariantDetails(variantId));
        }
    }, [dispatch, variantId]);

    // Yeni konfigürasyon başlatma
    const handleNewConfiguration = useCallback(async () => {
        try {
            if (currentVariant) {
                setIsDeleteModalOpen(true);
            } else {
                await dispatch(clearCurrentVariant());
                localStorage.removeItem('variant_id');
                navigate('/configurator', { replace: true });
                window.location.reload();
            }
        } catch (err) {
            console.error('Yeni konfigürasyon başlatma hatası:', err);
        }
    }, [currentVariant, dispatch, navigate]);

    // Varyant listesine gitme
    const handleGoToVariants = useCallback(() => {
        try {
            window.location.href = '/configurator/variants';
        } catch (err) {
            console.error('Varyant listesine gitme hatası:', err);
        }
    }, []);

    // Varyant silme işlemi
    const handleDeleteConfirm = useCallback(async () => {
        if (currentVariant?.id) {
            try {
                await dispatch(deleteVariant(currentVariant.id)).unwrap();
                setIsDeleteModalOpen(false);
                localStorage.removeItem('variant_id');
                await dispatch(clearCurrentVariant());
                navigate('/configurator', { replace: true });
                window.location.reload();
            } catch (err) {
                console.error('Varyant silme hatası:', err);
            }
        }
    }, [currentVariant, dispatch, navigate]);

    return (
        <div className="pc-configuration-page">
        

            <main className="pc-configuration-page__main">
                <PCConfigurationFlow />
                
                <div className="pc-configuration-page__button-group">
                    <PCButton 
                        variant="primary" 
                        onClick={handleNewConfiguration}
                    >
                        Yeni Konfigürasyon
                    </PCButton>
                    <PCButton 
                        variant="secondary" 
                        onClick={handleGoToVariants}
                    >
                        Varyant Listesi
                    </PCButton>
                </div>
            </main>

            <footer className="pc-configuration-page__footer">
                <p>&copy; 2024 Tuna Ofis. Tüm hakları saklıdır.</p>
            </footer>

            <PCModal
                isOpen={isDeleteModalOpen}
                onClose={() => setIsDeleteModalOpen(false)}
                title="Yeni Konfigürasyon"
            >
                <p>Mevcut varyantı silip yeni bir konfigürasyon başlatmak istediğinizden emin misiniz?</p>
                <div className="pc-configuration-page__modal-actions">
                    <PCButton 
                        onClick={handleDeleteConfirm} 
                        variant="danger"
                    >
                        Evet, Sil ve Yeni Başlat
                    </PCButton>
                    <PCButton 
                        onClick={() => setIsDeleteModalOpen(false)} 
                        variant="secondary"
                    >
                        İptal
                    </PCButton>
                </div>
            </PCModal>
        </div>
    );
};

export default PCConfigurationPage;