// frontend/src/components/ProductConfig/configuration/PCOptionList.js
import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useSelector } from 'react-redux';
import { selectCurrency } from '../store/pcSettingsSlice';
import PropTypes from 'prop-types';
import PCOptionCard from './PCOptionCard';
import PCModal from '../common/PCModal';
import PCInput from '../common/PCInput';
import PCButton from '../common/PCButton';
import { searchOptionsByName, sortOptionsByPopularity, formatPrice } from '../utils/pcHelpers';
import { MAX_DISPLAYED_OPTIONS } from '../utils/pcConstants';
import PCLoadingTransition from '../common/PCLoadingTransition';
import '../css/PCOptionList.css';

const PCOptionList = ({ 
    options = [], 
    onSelect, 
    initialSelectedOptions = [], 
    onNext = () => {}, // Varsayılan değer burada tanımlandı
    isTransitioning = false // Varsayılan değer burada tanımlandı
}) => {
    const currencyConfig = useSelector(selectCurrency);
    const [displayedOptions, setDisplayedOptions] = useState([]);
    const [selectedOptions, setSelectedOptions] = useState(initialSelectedOptions);
    const [searchTerm, setSearchTerm] = useState('');
    const [modalOption, setModalOption] = useState(null);
    const [showAllOptions, setShowAllOptions] = useState(false);

    const handleSelect = (optionId) => {
        setSelectedOptions([optionId]);
        onSelect([optionId]);
    };

    const sortedOptions = useMemo(() => {
        return sortOptionsByPopularity(options);
    }, [options]);

    const filterOptions = useCallback(() => {
        let filtered = searchOptionsByName(sortedOptions, searchTerm);
        return showAllOptions ? filtered : filtered.slice(0, MAX_DISPLAYED_OPTIONS);
    }, [sortedOptions, searchTerm, showAllOptions]);

    useEffect(() => {
        setDisplayedOptions(filterOptions());
    }, [filterOptions]);

    const closeModal = () => setModalOption(null);
    const handleSearch = (e) => setSearchTerm(e.target.value);
    const toggleShowAllOptions = () => setShowAllOptions(!showAllOptions);

    return (
        <PCLoadingTransition isLoading={isTransitioning}>
            <div className="pc-option-list">
                <PCInput
                    type="text"
                    name="search_term"
                    placeholder="Seçeneklerde ara..."
                    value={searchTerm}
                    onChange={handleSearch}
                    className="pc-option-list__search"
                />
                <div className="pc-option-list__grid">
                    {displayedOptions.map((option) => (
                        <PCOptionCard
                            key={option.id}
                            option={option}
                            isSelected={selectedOptions.includes(option.id)}
                            onSelect={() => handleSelect(option.id)}
                            disabled={false}
                            highlightPopular={option.is_popular || false}
                            showDescription={!!option.description}
                            activePrice={option.final_price || 0}
                        />
                    ))}
                </div>
                {sortedOptions.length > MAX_DISPLAYED_OPTIONS && (
                    <PCButton
                        onClick={toggleShowAllOptions}
                        className="pc-option-list__toggle-button"
                    >
                        {showAllOptions ? 'Daha az göster' : 'Tümünü göster'}
                    </PCButton>
                )}
                {modalOption && (
                    <PCModal
                        isOpen={!!modalOption}
                        onClose={closeModal}
                        title={modalOption.name}
                    >
                        <img
                            src={modalOption.image}
                            alt={modalOption.name}
                            style={{ maxWidth: '100%' }}
                        />
                        <p>{modalOption.description}</p>
                        <p>Fiyat: {formatPrice(modalOption.price_modifier, currencyConfig)}</p>
                    </PCModal>
                )}
            </div>
        </PCLoadingTransition>
    );
};

PCOptionList.propTypes = {
    options: PropTypes.arrayOf(
        PropTypes.shape({
            id: PropTypes.number.isRequired,
            name: PropTypes.string.isRequired,
            image: PropTypes.string,
            final_price: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
            description: PropTypes.string,
            is_popular: PropTypes.bool,
        })
    ).isRequired,
    onSelect: PropTypes.func.isRequired,
    onNext: PropTypes.func, // Artık opsiyonel
    initialSelectedOptions: PropTypes.arrayOf(PropTypes.number),
    isTransitioning: PropTypes.bool // Artık opsiyonel
};

export default PCOptionList;

