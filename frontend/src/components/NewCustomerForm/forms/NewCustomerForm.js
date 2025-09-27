// frontend/src/components/NewCustomerForm/NewCustomerForm.js
import React from 'react';
import useNewCustomerForm from '../hooks/useNewCustomerForm';
import '../css/NewCustomerForm.css';

const NewCustomerForm = ({ initialData = null, isEdit = false }) => {
  const {
    formData,
    errors,
    isSubmitting,
    submitStatus,
    handleChange,
    handleFileChange,
    handleAddPerson,
    handleRemovePerson,
    handlePersonChange,
    handleSubmit
  } = useNewCustomerForm({
    initialData, // Hook'a başlangıç verilerini gönder
    isEdit      // Edit modunda olduğunu bildir
  });

 return (
   <form onSubmit={handleSubmit} className="new-customer-form">
     <h2 className="new-customer-form__title">Yeni Müşteri Formu</h2>

  
     {/* Firma Bilgileri Bölümü */}
     <section className="new-customer-form__section">
       <h3 className="new-customer-form__section-title">Firma Bilgileri</h3>
       
       <div className="new-customer-form__group">
         <label className="new-customer-form__label new-customer-form__label--required">
           Firma Ünvanı
         </label>
         <input
           type="text"
           name="firma_unvani"
           value={formData.firma_unvani}
           onChange={handleChange}
           className={`new-customer-form__input ${errors.firma_unvani ? 'new-customer-form__input--error' : ''}`}
           maxLength={255}
         />
         {errors.firma_unvani && (
           <span className="new-customer-form__error">{errors.firma_unvani}</span>
         )}
       </div>

       <div className="new-customer-form__group">
         <label className="new-customer-form__label new-customer-form__label--required">
           Vergi Kimlik Numarası / T.C. Kimlik No
         </label>
         <input
           type="text"
           name="vergi_kimlik_numarasi"
           value={formData.vergi_kimlik_numarasi}
           onChange={handleChange}
           className={`new-customer-form__input ${errors.vergi_kimlik_numarasi ? 'new-customer-form__input--error' : ''}`}
           maxLength={50}
         />
         {errors.vergi_kimlik_numarasi && (
           <span className="new-customer-form__error">{errors.vergi_kimlik_numarasi}</span>
         )}
       </div>

       <div className="new-customer-form__group">
         <label className="new-customer-form__label new-customer-form__label--required">
           Vergi Dairesi
         </label>
         <input
           type="text"
           name="vergi_dairesi"
           value={formData.vergi_dairesi}
           onChange={handleChange}
           className={`new-customer-form__input ${errors.vergi_dairesi ? 'new-customer-form__input--error' : ''}`}
           maxLength={255}
         />
         {errors.vergi_dairesi && (
           <span className="new-customer-form__error">{errors.vergi_dairesi}</span>
         )}
       </div>

       <div className="new-customer-form__group">
         <label className="new-customer-form__label new-customer-form__label--required">
           Firma Adresi
         </label>
         <textarea
           name="firma_adresi"
           value={formData.firma_adresi}
           onChange={handleChange}
           className={`new-customer-form__input ${errors.firma_adresi ? 'new-customer-form__input--error' : ''}`}
           rows={4}
         />
         {errors.firma_adresi && (
           <span className="new-customer-form__error">{errors.firma_adresi}</span>
         )}
       </div>
     </section>

     {/* İletişim Bilgileri Bölümü */}
     <section className="new-customer-form__section">
       <h3 className="new-customer-form__section-title">İletişim Bilgileri</h3>

       <div className="new-customer-form__group--inline">
         <div className="new-customer-form__group">
           <label className="new-customer-form__label new-customer-form__label--required">
             Telefon Numarası
           </label>
           <input
             type="tel"
             name="telefon_numarasi"
             value={formData.telefon_numarasi}
             onChange={handleChange}
             className={`new-customer-form__input ${errors.telefon_numarasi ? 'new-customer-form__input--error' : ''}`}
             maxLength={20}
           />
           {errors.telefon_numarasi && (
             <span className="new-customer-form__error">{errors.telefon_numarasi}</span>
           )}
         </div>

         <div className="new-customer-form__group">
           <label className="new-customer-form__label new-customer-form__label--required">
             E-posta Adresi
           </label>
           <input
             type="email"
             name="email"
             value={formData.email}
             onChange={handleChange}
             className={`new-customer-form__input ${errors.email ? 'new-customer-form__input--error' : ''}`}
           />
           {errors.email && (
             <span className="new-customer-form__error">{errors.email}</span>
           )}
         </div>
       </div>

       <div className="new-customer-form__group--inline">
         <div className="new-customer-form__group">
           <label className="new-customer-form__label new-customer-form__label--required">
             Muhasebe İrtibat Telefonu
           </label>
           <input
             type="tel"
             name="muhasebe_irtibat_telefon"
             value={formData.muhasebe_irtibat_telefon}
             onChange={handleChange}
             className={`new-customer-form__input ${errors.muhasebe_irtibat_telefon ? 'new-customer-form__input--error' : ''}`}
             maxLength={20}
           />
           {errors.muhasebe_irtibat_telefon && (
             <span className="new-customer-form__error">{errors.muhasebe_irtibat_telefon}</span>
           )}
         </div>

         <div className="new-customer-form__group">
           <label className="new-customer-form__label new-customer-form__label--required">
             Muhasebe İrtibat E-posta
           </label>
           <input
             type="email"
             name="muhasebe_irtibat_email"
             value={formData.muhasebe_irtibat_email}
             onChange={handleChange}
             className={`new-customer-form__input ${errors.muhasebe_irtibat_email ? 'new-customer-form__input--error' : ''}`}
           />
           {errors.muhasebe_irtibat_email && (
             <span className="new-customer-form__error">{errors.muhasebe_irtibat_email}</span>
           )}
         </div>
       </div>
     </section>

     {/* Ödeme Bilgileri Bölümü */}
     <section className="new-customer-form__section">
       <h3 className="new-customer-form__section-title">Ödeme Bilgileri</h3>

       <div className="new-customer-form__group">
         <label className="new-customer-form__label new-customer-form__label--required">
           Ödeme Şartları ve Vadeleri
         </label>
         <textarea
           name="odeme_sartlari"
           value={formData.odeme_sartlari}
           onChange={handleChange}
           className={`new-customer-form__input ${errors.odeme_sartlari ? 'new-customer-form__input--error' : ''}`}
           rows={4}
         />
         {errors.odeme_sartlari && (
           <span className="new-customer-form__error">{errors.odeme_sartlari}</span>
         )}
       </div>

       <div className="new-customer-form__group">
         <label className="new-customer-form__label">
           İskonto veya Özel Fiyat Anlaşması
         </label>
         <textarea
           name="iskonto_anlasmasi"
           value={formData.iskonto_anlasmasi}
           onChange={handleChange}
           className="new-customer-form__input"
           rows={4}
         />
       </div>
     </section>

     {/* Dosya Yükleme Bölümü */}
     <section className="new-customer-form__section">
       <h3 className="new-customer-form__section-title">Gerekli Belgeler</h3>

       <div className="new-customer-form__group">
         <label className="new-customer-form__label new-customer-form__label--required">
           Vergi Levhası
         </label>
         <div className="new-customer-form__file-upload">
           <input
             type="file"
             name="vergi_levhasi"
             onChange={handleFileChange}
             className="new-customer-form__file-upload-input"
             accept=".pdf,.jpg,.jpeg,.png"
           />
           <span className="new-customer-form__file-upload-text">
             {formData.vergi_levhasi?.name || 'Dosya seçmek için tıklayın (Max: 1MB)'}
           </span>
         </div>
         {errors.vergi_levhasi && (
           <span className="new-customer-form__error">{errors.vergi_levhasi}</span>
         )}
       </div>

       <div className="new-customer-form__group">
         <label className="new-customer-form__label new-customer-form__label--required">
           Faaliyet Belgesi
         </label>
         <div className="new-customer-form__file-upload">
           <input
             type="file"
             name="faaliyet_belgesi"
             onChange={handleFileChange}
             className="new-customer-form__file-upload-input"
             accept=".pdf,.jpg,.jpeg,.png"
           />
           <span className="new-customer-form__file-upload-text">
             {formData.faaliyet_belgesi?.name || 'Dosya seçmek için tıklayın (Max: 1MB)'}
           </span>
         </div>
         {errors.faaliyet_belgesi && (
           <span className="new-customer-form__error">{errors.faaliyet_belgesi}</span>
         )}
       </div>

       <div className="new-customer-form__group">
         <label className="new-customer-form__label new-customer-form__label--required">
           Ticaret Sicil Gazetesi
         </label>
         <div className="new-customer-form__file-upload">
           <input
             type="file"
             name="ticaret_sicil"
             onChange={handleFileChange}
             className="new-customer-form__file-upload-input"
             accept=".pdf,.jpg,.jpeg,.png"
           />
           <span className="new-customer-form__file-upload-text">
             {formData.ticaret_sicil?.name || 'Dosya seçmek için tıklayın (Max: 1MB)'}
           </span>
         </div>
         {errors.ticaret_sicil && (
           <span className="new-customer-form__error">{errors.ticaret_sicil}</span>
         )}
       </div>

       <div className="new-customer-form__group">
         <label className="new-customer-form__label new-customer-form__label--required">
           İmza Sirküleri
         </label>
         <div className="new-customer-form__file-upload">
           <input
             type="file"
             name="imza_sirkuleri"
             onChange={handleFileChange}
             className="new-customer-form__file-upload-input"
             accept=".pdf,.jpg,.jpeg,.png"
           />
           <span className="new-customer-form__file-upload-text">
             {formData.imza_sirkuleri?.name || 'Dosya seçmek için tıklayın (Max: 1MB)'}
           </span>
         </div>
         {errors.imza_sirkuleri && (
           <span className="new-customer-form__error">{errors.imza_sirkuleri}</span>
         )}
       </div>

       <div className="new-customer-form__group">
         <label className="new-customer-form__label new-customer-form__label--required">
           Banka IBAN Bilgileri
         </label>
         <div className="new-customer-form__file-upload">
           <input
             type="file"
             name="banka_iban"
             onChange={handleFileChange}
             className="new-customer-form__file-upload-input"
             accept=".pdf,.jpg,.jpeg,.png"
           />
           <span className="new-customer-form__file-upload-text">
             {formData.banka_iban?.name || 'Dosya seçmek için tıklayın (Max: 1MB)'}
           </span>
         </div>
         {errors.banka_iban && (
           <span className="new-customer-form__error">{errors.banka_iban}</span>
         )}
       </div>
     </section>

     {/* Yetkili Kişiler Bölümü */}
     <section className="new-customer-form__section">
       <h3 className="new-customer-form__section-title">Yetkili Kişiler</h3>

       {formData.yetkili_kisiler.map((person, index) => (
         <div key={index} className="new-customer-form__person-card">
           <div className="new-customer-form__group">
             <label className="new-customer-form__label new-customer-form__label">
               Yetkili Kişi Adı Soyadı
             </label>
             <input
               type="text"
               value={person.ad_soyad}
               onChange={(e) => handlePersonChange(index, 'ad_soyad', e.target.value)}
               className={`new-customer-form__input ${
                 errors.yetkili_kisiler?.[index] ? 'new-customer-form__input--error' : ''
               }`}
               maxLength={255}
             />
           </div>

           <div className="new-customer-form__group--inline">
             <div className="new-customer-form__group">
               <label className="new-customer-form__label new-customer-form__label">
                 Yetkili Telefon
               </label>
               <input
                 type="tel"
                 value={person.telefon}
                 onChange={(e) => handlePersonChange(index, 'telefon', e.target.value)}
                 className={`new-customer-form__input ${
                   errors.yetkili_kisiler?.[index] ? 'new-customer-form__input--error' : ''
                 }`}
                 maxLength={20}
               />
             </div>

             <div className="new-customer-form__group">
               <label className="new-customer-form__label new-customer-form__label">
                 Yetkili E-posta
               </label>
               <input
                 type="email"
                 value={person.email}
                 onChange={(e) => handlePersonChange(index, 'email', e.target.value)}
                 className={`new-customer-form__input ${
                   errors.yetkili_kisiler?.[index] ? 'new-customer-form__input--error' : ''
                 }`}
               />
             </div>
           </div>

           {errors.yetkili_kisiler?.[index] && (
             <span className="new-customer-form__error">
               {errors.yetkili_kisiler[index]}
             </span>
           )}

           {formData.yetkili_kisiler.length > 1 && (
             <button
               type="button"
               onClick={() => handleRemovePerson(index)}
               className="new-customer-form__button new-customer-form__button--secondary"
             >
               Yetkili Kişiyi Kaldır
             </button>
           )}
         </div>
       ))}

       <button
         type="button"
         onClick={handleAddPerson}
         className="new-customer-form__button new-customer-form__button--secondary"
       >
         Yetkili Kişi Ekle
       </button>
     </section>

     {/* Form Submit Bölümü - Bu kısmı güncelleyeceğiz */}
      <div className="new-customer-form__section">
        {/* Mail ve Form Durum Mesajları */}
        {submitStatus.success && (
          <div className={`new-customer-form__message ${
            submitStatus.mailSent 
              ? 'new-customer-form__message--success'
              : 'new-customer-form__message--warning'
          }`}>
            {submitStatus.message}
          </div>
        )}

        {errors.submit && (
          <div className="new-customer-form__message new-customer-form__message--error">
            {errors.submit}
          </div>
        )}

          <button
          type="submit"
          className="new-customer-form__button new-customer-form__button--primary"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Kaydediliyor...' : (isEdit ? 'Değişiklikleri Kaydet' : 'Formu Gönder')}
        </button>
      </div>
    </form>
  );
};

export default NewCustomerForm;