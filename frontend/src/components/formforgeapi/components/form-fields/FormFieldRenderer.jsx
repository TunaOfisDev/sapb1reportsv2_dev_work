// path: frontend/src/components/formforgeapi/components/form-fields/FormFieldRenderer.jsx

import React from 'react';
import { FIELD_TYPES } from '../../constants';

// ==============================================================================
// 1. MEVCUT TÜM ALAN BİLEŞENLERİNİ IMPORT ETME
// ==============================================================================

// --- Temel Giriş Alanları ---
import TextField from './TextField';
import TextareaField from './TextareaField';

// --- Seçim Alanları ---
import SelectField from './SelectField';
import UserPickerField from './UserPickerField';
import MultiSelectField from './MultiSelectField';
// Not: CheckboxField ve MultiSelectField henüz oluşturulmadı, eklendiğinde import edilecek.

// --- Tarih/Zaman Alanları ---
import DateTimeField from './DateTimeField';

// --- Gelişmiş Giriş Alanları ---
import PhoneField from './PhoneField';
import CurrencyField from './CurrencyField';
import RatingField from './RatingField';

// --- Yapısal Alanlar ---
import HeadingField from './HeadingField';
import ParagraphField from './ParagraphField';
import SeparatorField from './SeparatorField';

// --- Özel Amaçlı Alanlar ---
import CalculatedField from './CalculatedField';


/**
 * Akıllı Alan Yönlendirici (Smart Field Router)
 * --------------------------------------------------------------------
 * Gelen 'field' nesnesinin tipine göre doğru alan bileşenini, doğru proplarla render eder.
 */
const FormFieldRenderer = ({ field, control, errors, userList, usersLoading, watch, setValue }) => {
  // Veri girişi alanlarına geçilecek ortak proplar.
  const commonInputProps = { field, control, errors };

  // Alan tipine göre doğru bileşeni seç ve render et.
  switch (field.field_type) {
    // --- Metin Bazlı Alanlar ---
    case FIELD_TYPES.TEXT:
    case FIELD_TYPES.EMAIL:
    case FIELD_TYPES.URL:
    case FIELD_TYPES.NUMBER:
    case FIELD_TYPES.PERCENTAGE:
      return <TextField {...commonInputProps} />;

    case FIELD_TYPES.TEXTAREA:
      return <TextareaField {...commonInputProps} />;

    // --- Seçim Bazlı Alanlar ---
    case FIELD_TYPES.SINGLE_SELECT:
      return <SelectField {...commonInputProps} />;
    
    case FIELD_TYPES.USER_PICKER:
      return <UserPickerField {...commonInputProps} userList={userList} isLoading={usersLoading} />;

    // YENİ: multiselect tipi için kendi özel bileşenini kullan
    case FIELD_TYPES.MULTI_SELECT:
      return <MultiSelectField {...commonInputProps} />;
      
    // --- Tarih/Zaman Alanları ---
    case FIELD_TYPES.DATE:
    case FIELD_TYPES.DATETIME:
    case FIELD_TYPES.TIME:
      return <DateTimeField {...commonInputProps} />;

    // --- Gelişmiş Giriş Alanları ---
    case FIELD_TYPES.PHONE:
      return <PhoneField {...commonInputProps} />;
    case FIELD_TYPES.CURRENCY:
      return <CurrencyField {...commonInputProps} />;
    case FIELD_TYPES.RATING:
        return <RatingField {...commonInputProps} />;

    // --- Yapısal Alanlar (Veri girişi yok, sadece 'field' prop'u yeterli) ---
    case FIELD_TYPES.HEADING:
      return <HeadingField field={field} />;
    case FIELD_TYPES.PARAGRAPH:
      return <ParagraphField field={field} />;
    case FIELD_TYPES.SEPARATOR:
      return <SeparatorField />;

    // --- Özel Amaçlı Alanlar ---
    case FIELD_TYPES.CALCULATED:
        return <CalculatedField {...commonInputProps} watch={watch} setValue={setValue} />;

    // --- Henüz oluşturulmamış veya varsayılan alanlar ---
    default:
      // Bilinmeyen bir alan tipi gelirse, varsayılan olarak basit bir metin input'u göster.
      console.warn(`'${field.field_type}' için özel bir bileşen bulunamadı, TextField kullanılıyor.`);
      return <TextField {...commonInputProps} />;
  }
};

export default FormFieldRenderer;