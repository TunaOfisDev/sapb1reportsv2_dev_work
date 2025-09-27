import React, { useState, useEffect } from 'react';
import Modal from 'react-modal';
import useSalesOfferDocSum from '../hooks/useSalesOfferDocSum';
import FormatNumber from './FormatNumber';
import '../css/ShowModalOfferDocDetail.css';

Modal.setAppElement('#root');

const ShowModalOfferDocDetail = ({ masterBelgeGirisNo, isOpen, onRequestClose }) => {
  const { fetchSalesOfferDetailByBelgeNo, loading, error } = useSalesOfferDocSum();
  const [offerDocDetails, setOfferDocDetails] = useState([]);
  const [masterDetail, setMasterDetail] = useState(null);

  useEffect(() => {
    if (isOpen) {
      const fetchDetails = async () => {
        try {
          const data = await fetchSalesOfferDetailByBelgeNo(masterBelgeGirisNo);
          setOfferDocDetails(data);
          if (data.length > 0) {
            setMasterDetail({
              musteri_ad: data[0].musteri_ad,
              musteri_kod: data[0].musteri_kod,
              sip_no: data[0].belge_no,
              belge_tarihi: data[0].belge_tarih,
              sevk_adresi: data[0].sevk_adres
            });
          }
        } catch (err) {
          console.error('Teklif belge detayları yüklenirken bir hata oluştu: ' + err.message);
        }
      };
      fetchDetails();
    }
  }, [isOpen, masterBelgeGirisNo, fetchSalesOfferDetailByBelgeNo]);

  const renderMasterDetails = () => {
    return masterDetail ? (
      <div className="modal-offer__master">
        <h3 className="modal-offer__master-title">
          Müşteri: {masterDetail.musteri_kod} - {masterDetail.musteri_ad}
        </h3>
        <p className="modal-offer__master-info">Teklif No: {masterDetail.sip_no}</p>
        <p className="modal-offer__master-info">Belge Tarihi: {masterDetail.belge_tarihi}</p>
        <p className="modal-offer__master-info">Sevk Adresi: {masterDetail.sevk_adresi}</p>
      </div>
    ) : null;
  };

  const renderModalContent = () => {
    if (loading) return <div>Yükleniyor...</div>;
    if (error) return <div>Hata: {error}</div>;
    if (offerDocDetails && offerDocDetails.length > 0) {
      return (
        <>
          {renderMasterDetails()}
          <table className="modal-offer__table">
            <thead className="modal-offer__table-head">
              <tr>
                <th className="modal-offer__table-header">No</th>
                <th className="modal-offer__table-header">Kalem Kodu</th>
                <th className="modal-offer__table-header">Kalem Tanımı</th>
                <th className="modal-offer__table-header modal-offer__table-header--numeric">Miktar</th>
                <th className="modal-offer__table-header modal-offer__table-header--numeric">Fiyat DPB</th>
                <th className="modal-offer__table-header modal-offer__table-header--numeric">İsk. Oran</th>
                <th className="modal-offer__table-header modal-offer__table-header--numeric">Brut SPB</th>
                <th className="modal-offer__table-header modal-offer__table-header--numeric">Net SPB</th>
              </tr>
            </thead>
            <tbody>
              {offerDocDetails.map((detail, index) => (
                <tr key={index} className="modal-offer__table-row">
                  <td className="modal-offer__table-cell">{detail.satir_no}</td>
                  <td className="modal-offer__table-cell">{detail.kalem_kod}</td>
                  <td className="modal-offer__table-cell">{detail.kalem_tanimi}</td>
                  <td className="modal-offer__table-cell modal-offer__table-cell--numeric">
                    <FormatNumber value={detail.siparis_miktari} />
                  </td>
                  <td className="modal-offer__table-cell modal-offer__table-cell--numeric">
                    <FormatNumber value={detail.liste_fiyat_dpb} />
                  </td>
                  <td className="modal-offer__table-cell modal-offer__table-cell--numeric">
                    <FormatNumber value={detail.iskonto_oran} />
                  </td>
                  <td className="modal-offer__table-cell modal-offer__table-cell--numeric">
                    <FormatNumber value={detail.brut_tutar_spb} />
                  </td>
                  <td className="modal-offer__table-cell modal-offer__table-cell--numeric">
                    <FormatNumber value={detail.net_tutar_spb} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      );
    }
    return <div>Detay bilgisi bulunamadı.</div>;
  };

  return (
    <Modal
      isOpen={isOpen}
      onRequestClose={onRequestClose}
      contentLabel="Teklif Detayları"
      className="modal-offer"
      overlayClassName="modal-offer__overlay"
    >
      <div className="modal-offer__header">
        <h2 className="modal-offer__title">Satış Teklif Detayları</h2>
      </div>
      <div className="modal-offer__content">
        {renderModalContent()}
      </div>
      <div className="modal-offer__footer">
        <button onClick={onRequestClose} className="modal-offer__button modal-offer__button--close">
          Kapat
        </button>
      </div>
    </Modal>
  );
};

export default ShowModalOfferDocDetail;