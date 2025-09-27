// path: frontend/src/components/StockCardIntegration/hooks/useStockCardForm.js

import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import { stockCardValidationSchema } from '../utils/formValidators';

const defaultValues = {
  itemCode: '',
  itemName: '',
  ItemsGroupCode: '',
  UoMGroupEntry: 'Adet',
  SalesVATGroup: 'HES0010',
  Price: '',
  Currency: 'EUR',
  U_eski_bilesen_kod: '',
};

/**
 * Tekil stok kartı oluşturma formu için hook
 */
const useStockCardForm = () => {
  const form = useForm({
    mode: 'onBlur',
    defaultValues,
    resolver: yupResolver(stockCardValidationSchema),
  });

  return form;
};

export default useStockCardForm;
