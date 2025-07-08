// frontend/src/components/SalesOrderDocSum/utils/ShowModalOrderDocDetail.js
import React, { useState, useEffect, useCallback } from 'react';
import Modal from 'react-modal';
import { toast } from 'react-toastify';
import useSalesOrderDocSum from '../hooks/useSalesOrderDocSum';
import FormatNumber from '../utils/FormatNumber';
import CopyToExcel from '../utils/CopyToExcel';
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
          if (data && data.length > 0) {
            setOrderDocDetails(data);
            setMasterDetail({
              musteri_ad: data[0].musteri_ad,
              sip_no: data[0].belge_no,
              belge_tarihi: data[0].belge_tarih
            });
          } else {
            setOrderDocDetails([]);
            setMasterDetail(null);
          }
        } catch (err) {
          console.error('Sipariş belge detayları yüklenirken bir hata oluştu:', err);
          toast.error('Detaylar yüklenirken bir hata oluştu');
        }
      };
      fetchDetails();
    }
  }, [isOpen, masterBelgeGirisNo, fetchSalesOrderDetailByBelgeNo]);

  const handleExportToExcel = useCallback(() => {
    try {
      if (orderDocDetails?.length && masterDetail) {
        CopyToExcel.exportOrderDetails(orderDocDetails, masterDetail);
        toast.success('Excel dosyası başarıyla oluşturuldu');
      } else {
        toast.warning('Dışa aktarılacak veri bulunamadı');
      }
    } catch (error) {
      console.error('Excel export hatası:', error);
      toast.error('Excel dosyası oluşturulurken bir hata oluştu');
    }
  }, [orderDocDetails, masterDetail]);

  const renderMasterDetails = useCallback(() => {
    return masterDetail ? (
      <div className="ShowModalOrderDocDetail__master-detail">
        <h3 className="ShowModalOrderDocDetail__master-detail-title">
          Müşteri Ad: {masterDetail.musteri_ad}
        </h3>
        <p className="ShowModalOrderDocDetail__master-detail-info">
          Sipariş No: {masterDetail.sip_no}
        </p>
        <p className="ShowModalOrderDocDetail__master-detail-info">
          Belge Tarihi: {masterDetail.belge_tarihi}
        </p>
      </div>
    ) : null;
  }, [masterDetail]);

  

  const calculateTotals = useCallback(() => {
    if (!orderDocDetails?.length) return null;
  
    // Tüm satırların toplamını hesapla
    const totals = orderDocDetails.reduce((acc, curr) => {
      // Her bir değeri decimal olarak dönüştür
      const miktar = parseFloat(curr.siparis_miktari) || 0;
      const tutar = parseFloat(curr.net_tutar_spb) || 0;
  
      return {
        siparis_miktari: acc.siparis_miktari + miktar,
        net_tutar_spb: acc.net_tutar_spb + tutar
      };
    }, {
      // Başlangıç değerlerini tanımla
      siparis_miktari: 0,
      net_tutar_spb: 0
    });
  
    // Toplamları decimal hassasiyetinde tut
    totals.siparis_miktari = parseFloat(totals.siparis_miktari.toFixed(2));
    totals.net_tutar_spb = parseFloat(totals.net_tutar_spb.toFixed(2));
  
    return totals;
  }, [orderDocDetails]);



  const renderModalContent = () => {
    if (loading) return <div className="ShowModalOrderDocDetail__loading">Yükleniyor...</div>;
    if (error) return <div className="ShowModalOrderDocDetail__error">Hata: {error}</div>;
    
    if (orderDocDetails?.length > 0) {
      const totals = calculateTotals();

      return (
        <div className="ShowModalOrderDocDetail__content">
          {renderMasterDetails()}
          <div className="ShowModalOrderDocDetail__table-wrapper">
            <table className="ShowModalOrderDocDetail__table">
              <thead>
                <tr>
                  <th>No</th>
                  <th>Kalem Kodu</th>
                  <th>Kalem Tanımı</th>
                  <th>Miktar</th>
                  <th>Fiyat(DPB)</th>
                  <th>Isk.Oran</th>
                  <th>Net Tutar(SPB)</th>
                </tr>
              </thead>
              <tbody>
                {orderDocDetails.map((detail, index) => (
                  <tr key={index}>
                    <td>{detail.satir_no}</td>
                    <td>{detail.kalem_kod}</td>
                    <td>{detail.kalem_tanimi}</td>
                    <td className="numeric-cell">
                      <FormatNumber value={detail.siparis_miktari} />
                    </td>
                    <td className="numeric-cell">
                      <FormatNumber value={detail.liste_fiyat_dpb} />
                    </td>
                    <td className="numeric-cell">
                      <FormatNumber value={detail.iskonto_oran} />
                    </td>
                    <td className="numeric-cell">
                      <FormatNumber value={detail.net_tutar_spb} />
                    </td>
                  </tr>
                ))}
              </tbody>
              {totals && (
                <tfoot>
                  <tr>
                    <td colSpan="3" className="total-label">TOPLAM</td>
                    <td className="numeric-cell">
                      <FormatNumber value={totals.siparis_miktari} />
                    </td>
                    <td colSpan="2"></td>
                    <td className="numeric-cell">
                      <FormatNumber value={totals.net_tutar_spb} />
                    </td>
                  </tr>
                </tfoot>
              )}
            </table>
          </div>
        </div>
      );
    }

    return <div className="ShowModalOrderDocDetail__no-data">Detay bilgisi bulunamadı.</div>;
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
        <div className="ShowModalOrderDocDetail__header-actions">
          <button
            onClick={handleExportToExcel}
            className="ShowModalOrderDocDetail__export-button"
            disabled={!orderDocDetails?.length}
          >
            Excel'e Aktar
          </button>
          <button
            onClick={onRequestClose}
            className="ShowModalOrderDocDetail__close-button"
          >
            Kapat
          </button>
        </div>
      </div>
      {renderModalContent()}
    </Modal>
  );
};

export default React.memo(ShowModalOrderDocDetail);