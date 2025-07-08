// frontend/src/components/SalesOrderDocSum/utils/ShowModalOrderDocDetail.js
import React, { useState, useEffect } from 'react';
import Modal from 'react-modal';
import useSalesOrderDocSum from '../hooks/useSalesOrderDocSum';
import FormatNumber from '../utils/FormatNumber';
import '../css/ShowModalOrderDocDetail.css';

Modal.setAppElement('#root');

const ShowModalOrderDocDetail = ({ masterBelgeGirisNo, isOpen, onRequestClose }) => {
  const { fetchSalesOrderDetailByBelgeNo, loading, error } = useSalesOrderDocSum();
  const [orderDocDetails, setOrderDocDetails] = useState([]);
  const [masterDetail, setMasterDetail] = useState(null);

  useEffect(() => {
    if (isOpen) {
      const fetchDetails = async () => {
        try {
          const data = await fetchSalesOrderDetailByBelgeNo(masterBelgeGirisNo);
          setOrderDocDetails(data);
          if (data.length > 0) {
            setMasterDetail({
              musteri_ad: data[0].musteri_ad,
              sip_no: data[0].belge_no,
              belge_tarihi: data[0].belge_tarih
            });
          }
        } catch (err) {
          console.error('Sipariş belge detayları yüklenirken bir hata oluştu: ' + err.message);
        }
      };
      fetchDetails();
    }
  }, [isOpen, masterBelgeGirisNo, fetchSalesOrderDetailByBelgeNo]);

  const renderMasterDetails = () => {
    return masterDetail ? (
      <div className="ShowModalOrderDocDetail__master-detail">
        <h3 className="ShowModalOrderDocDetail__master-detail-title">Müşteri Ad: {masterDetail.musteri_ad}</h3>
        <p className="ShowModalOrderDocDetail__master-detail-info">Sipariş No: {masterDetail.sip_no}</p>
        <p className="ShowModalOrderDocDetail__master-detail-info">Belge Tarihi: {masterDetail.belge_tarihi}</p>
      </div>
    ) : null;
  };

  const renderModalContent = () => {
    if (loading) return <div>Yükleniyor...</div>;
    if (error) return <div>Hata: {error}</div>;
    if (orderDocDetails && orderDocDetails.length > 0) {
      return (
        <>
          {renderMasterDetails()}
          <table className="ShowModalOrderDocDetail__table">
            <thead>
              <tr>
                <th>No</th>
                <th>KalemKodu</th>
                <th>KalemTanimi</th>
                <th>Miktar</th>
                <th>Fiyat(DPB)</th>
                <th>IskOran</th>
                <th>NetTutar(SPB)</th>
              </tr>
            </thead>
            <tbody>
              {orderDocDetails.map((detail, index) => (
                <tr key={index}>
                  <td>{detail.satir_no}</td>
                  <td>{detail.kalem_kod}</td>
                  <td>{detail.kalem_tanimi}</td>
                  <td className="ShowModalOrderDocDetail__table .numeric-cell"><FormatNumber value={detail.siparis_miktari} /></td>
                  <td className="ShowModalOrderDocDetail__table .numeric-cell"><FormatNumber value={detail.liste_fiyat_dpb} /></td>
                  <td className="ShowModalOrderDocDetail__table .numeric-cell"><FormatNumber value={detail.iskonto_oran} /></td>
                  <td className="ShowModalOrderDocDetail__table .numeric-cell"><FormatNumber value={detail.net_tutar_spb} /></td>
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
      contentLabel="Sipariş Detayları"
      className="ShowModalOrderDocDetail"
      overlayClassName="ShowModalOrderDocDetail__overlay"
    >
      <div className="ShowModalOrderDocDetail__header">
        <h2 className="ShowModalOrderDocDetail__header-title">Sipariş Detayları</h2>
      </div>
      <div className="ShowModalOrderDocDetail__content">
        {renderModalContent()}
      </div>
      <button onClick={onRequestClose} className="ShowModalOrderDocDetail__close-button">
        Kapat
      </button>
    </Modal>
  );
};

export default ShowModalOrderDocDetail;




