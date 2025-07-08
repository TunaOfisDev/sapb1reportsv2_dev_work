// frontend/src/components/SalesOrderDetail/utils/ShowDetail.js
import React, { useState, useEffect } from 'react';
import Modal from 'react-modal';
import salesOrderDetailApi from '../../../api/salesorderdetail';
import FormatNumber from '../utils/FormatNumber';
import '../css/ShowDetail.css';

Modal.setAppElement('#root');

const ShowDetail = ({ masterBelgeGirisNo }) => {
  const [salesOrderDetails, setSalesOrderDetails] = useState([]);
  const [masterDetail, setMasterDetail] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (modalVisible) {
      const fetchDetails = async () => {
        setLoading(true);
        try {
          const response = await salesOrderDetailApi.fetchSalesOrderDetailsByMasterBelgeGirisNo(masterBelgeGirisNo);
          setSalesOrderDetails(response.results);
          if (response.results.length > 0) {
            // Set master details from the first detail item
            setMasterDetail({
              musteri_ad: response.results[0].master_musteri_ad,
              sip_no: response.results[0].master_sip_no,
              belge_tarihi: response.results[0].master_belge_tarihi
            });
          }
        } catch (err) {
          setError('Satış sipariş detayları yüklenirken bir hata oluştu: ' + err.message);
        } finally {
          setLoading(false);
        }
      };
      fetchDetails();
    }
  }, [masterBelgeGirisNo, modalVisible]);

  const handleShowDetails = () => {
    setModalVisible(true);
  };

  const renderMasterDetails = () => {
    return masterDetail ? (
      <div className="master-detail-header">
        <h3>Müşteri Ad: {masterDetail.musteri_ad}</h3>
        <p>Sipariş No: {masterDetail.sip_no}</p>
        <p>Belge Tarihi: {masterDetail.belge_tarihi}</p>
      </div>
    ) : null;
  };

  const renderModalContent = () => {
    if (loading) return <div>Yükleniyor...</div>;
    if (error) return <div>Hata: {error}</div>;
    if (salesOrderDetails && salesOrderDetails.length > 0) {
      return (
        <>
          {renderMasterDetails()}
          <table className="detail-table">
            <thead>
              <tr>
                <th>Stok Kodu</th>
                <th>Miktar</th>
                <th>Fiyat(YPB)</th>
                <th>IskOran</th>
                <th>Net Tutar (YPB)</th>
              </tr>
            </thead>
            <tbody>
              {salesOrderDetails.map((detail, index) => (
                <tr key={index}>
                  <td>{detail.kalem_kod}</td>
                  <td className="numeric-cell"><FormatNumber value={detail.sip_miktar} /></td>
                  <td className="numeric-cell"><FormatNumber value={detail.liste_fiyat_ypb} /></td>
                  <td className="numeric-cell"><FormatNumber value={detail.iskonto_oran} /></td>
                  <td className="numeric-cell"><FormatNumber value={detail.net_tutar_ypb} /></td>
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
    <>
      <button onClick={handleShowDetails} className="show-detail__button">Detaylar</button>
      <Modal
        isOpen={modalVisible}
        onRequestClose={() => setModalVisible(false)}
        contentLabel="Sipariş Detayları"
        className="modal"
        overlayClassName="overlay"
      >
        <div className="modal-header">
          <h2>Sipariş Detayları</h2>
        </div>
        <div className="modal-content">
          {renderModalContent()}
        </div>
        <button onClick={() => setModalVisible(false)} className="close-button">
          Kapat
        </button>
      </Modal>
    </>
  );
};

export default ShowDetail;