// path: frontend/src/components/NexusCore/containers/ReportPlayground/index.jsx

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styles from './ReportPlayground.module.scss';

// --- GÜNCELLENMİŞ VE YENİ IMPORTLAR ---
import { useApi } from '../../hooks/useApi';
import { useNotifications } from '../../hooks/useNotifications';
// Artık virtualTablesApi.execute'ye ihtiyacımız yok, DataApp'i çekmemiz lazım.
import * as dataAppsApi from '../../api/dataAppsApi'; 
import * as reportTemplatesApi from '../../api/reportTemplatesApi';

import Spinner from '../../components/common/Spinner/Spinner';
import Button from '../../components/common/Button/Button';
import Input from '../../components/common/Input/Input';
import DetailBuilder from './DetailBuilder';
import PivotBuilder from './PivotBuilder';

// Boş bir konfigürasyon şablonu (Bu aynı kalır)
const EMPTY_CONFIG = {
    report_type: 'detail',
    columns: [],
    pivot_config: { rows: [], columns: [], values: [], filters: [] },
};

const ReportPlayground = () => {
    // 1. GÜNCELLENMİŞ ROTA (ROUTE) VE MOD YÖNETİMİ
    // Artık :virtualTableId değil, :appId bekliyoruz.
    const { appId, reportId } = useParams();
    const isEditMode = Boolean(reportId); 

    const navigate = useNavigate();
    const { addNotification } = useNotifications();

    // 2. GÜNCELLENMİŞ API KANCALARI
    // Kaynak veriyi (DataApp) meta verisini çekmek için yeni hook:
    const { data: sourceDataApp, loading: appLoading, error: appError, request: getSourceApp } = useApi(dataAppsApi.getDataAppById);
    
    // Mevcut şablonu (Edit moduysa) çekmek için hook (Bu aynı):
    const { data: existingTemplate, loading: templateLoading, request: getTemplate } = useApi(reportTemplatesApi.getReportTemplateById);
    
    // Kaydetme/Güncelleme hook'u (Bu da aynı):
    const { loading: isSaving, request: saveReportApi } = useApi(
        isEditMode ? reportTemplatesApi.updateReportTemplate : reportTemplatesApi.createReportTemplate
    );
    // ESKİ executeSourceQuery hook'u kaldırıldı.

    // 3. GÜNCELLENMİŞ STATE YÖNETİMİ
    const [reportTitle, setReportTitle] = useState('');
    const [reportType, setReportType] = useState('detail');
    const [configuration, setConfiguration] = useState(EMPTY_CONFIG);
    // Ana kaynağımız artık bir App ID.
    const [currentAppId, setCurrentAppId] = useState(appId || null);

    // 4. TAMAMEN YENİLENMİŞ VERİ YÜKLEME MANTIĞI (useEffect)
    useEffect(() => {
        const fetchTemplateAndApp = async (id) => {
            const { success, data: templateData } = await getTemplate(id);
            if (success) {
                // Şablondan state'i doldur
                setReportTitle(templateData.title);
                const config = templateData.configuration_json || EMPTY_CONFIG;
                setConfiguration(config);
                setReportType(config.report_type || 'detail');
                
                // EN ÖNEMLİSİ: Şablonun hangi DataApp'e bağlı olduğunu state'e kaydet
                const loadedAppId = templateData.source_data_app;
                setCurrentAppId(loadedAppId);
                
                // Şimdi o DataApp'in meta verisini (kolon listesi için) çek
                getSourceApp(loadedAppId);

            } else {
                addNotification('Mevcut rapor yüklenirken hata oluştu.', 'error');
                navigate('/nexus/reports');
            }
        };

        if (isEditMode && reportId) {
            // DÜZENLEME MODU: Önce şablonu çek, şablon bize hangi App'i çekeceğimizi söylesin.
            fetchTemplateAndApp(reportId);
        } else if (appId) {
            // YENİ KAYIT MODU: App ID'si URL'den geliyor, doğrudan App meta verisini çek.
            setCurrentAppId(appId);
            getSourceApp(appId);
        }
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [isEditMode, reportId, appId, getTemplate, getSourceApp, navigate, addNotification]);
    // Not: Eski veri çekme (executeSourceQuery) effect'i tamamen kaldırıldı.


    // --- 5. YOL HARİTASI MADDE 2'NİN TAM KARŞILIĞI: KOLON BİRLEŞTİRME (MERGE) ---
    // Gelen DataApp verisinden (tüm ilişkili tabloların metadata'sını içeren)
    // tek, benzersiz (unique) ve düz (flat) bir kolon listesi üretiyoruz.
    const sourceColumns = useMemo(() => {
        const allColumns = new Set();
        if (!sourceDataApp || !sourceDataApp.virtual_table_details) {
            return [];
        }
        
        // DataApp içindeki her bir 'VirtualTable' detayında dön
        for (const table of sourceDataApp.virtual_table_details) {
            if (table.column_metadata) {
                // O tablonun metadata'sındaki her bir kolon adını (key) al
                for (const columnKey of Object.keys(table.column_metadata)) {
                    allColumns.add(columnKey); // Set sayesinde otomatik olarak benzersiz olur
                }
            }
        }
        
        return Array.from(allColumns); // Set'i tekrar Array'e çevir
    }, [sourceDataApp]); // Sadece sourceDataApp değiştiğinde yeniden hesapla.


    // Konfigürasyon değişim callback'leri (Bunlar aynı kaldı)
    const handlePivotChange = useCallback((pivotConfig) => {
        setConfiguration(prev => ({ ...prev, pivot_config: pivotConfig }));
    }, []); 

    const handleDetailConfigChange = useCallback((detailConfig) => {
        setConfiguration(detailConfig);
    }, []);

    // 6. GÜNCELLENMİŞ KAYDETME FONKSİYONU
    const handleSave = async () => {
        if (!reportTitle) {
            addNotification('Lütfen rapora bir başlık verin.', 'error');
            return;
        }
        // KRİTİK GÜNCELLEME: source_virtual_table_id YERİNE source_data_app_id gönderiyoruz.
        const payload = {
            title: reportTitle,
            source_data_app_id: currentAppId, // <-- DEĞİŞTİ
            configuration_json: { ...configuration, report_type: reportType },
            sharing_status: existingTemplate?.sharing_status || 'PRIVATE',
        };

        const { success } = await (isEditMode ? saveReportApi(reportId, payload) : saveReportApi(payload));

        if (success) {
            addNotification(`Rapor başarıyla ${isEditMode ? 'güncellendi' : 'kaydedildi'}!`, 'success');
            navigate('/nexus/reports');
        } else {
            addNotification('Rapor kaydedilirken bir hata oluştu.', 'error');
        }
    };


    // 7. GÜNCELLENMİŞ RENDER MANTIĞI
    // Artık sourceLoading değil, appLoading ve templateLoading bekliyoruz
    if (appLoading || templateLoading) return <Spinner size="lg" />;
    if (appError) return <div className={styles.error}>Veri modeli yüklenirken bir hata oluştu: {appError.message}</div>;
    
    // sourceColumns artık useMemo'dan gelen birleşik (merged) listedir.
    
    return (
        <div className={styles.pageContainer}>
            <header className={styles.pageHeader}>
                {/* Başlık ve Butonlar (Aynı kaldı) */}
                <Input 
                    id="report-title"
                    label="Rapor Başlığı"
                    value={reportTitle} 
                    onChange={(e) => setReportTitle(e.target.value)}
                    placeholder="Örn: Aylık Müşteri Risk Analizi"
                />
                <div className={styles.modeSwitcher}>
                    <button className={`${styles.modeButton} ${reportType === 'detail' ? styles.active : ''}`} onClick={() => setReportType('detail')}>
                        Detay Tablo
                    </button>
                    <button className={`${styles.modeButton} ${reportType === 'pivot' ? styles.active : ''}`} onClick={() => setReportType('pivot')}>
                        Özet (Pivot) Tablo
                    </button>
                </div>
                <Button onClick={handleSave} variant="primary" disabled={isSaving}>
                    {isSaving ? 'Kaydediliyor...' : (isEditMode ? 'Raporu Güncelle' : 'Raporu Kaydet')}
                </Button>
            </header>
            
            <div className={styles.playgroundContainer}>
                {reportType === 'detail' ? (
                    <DetailBuilder 
                        // NOT: DetailBuilder artık canlı veri önizlemesi alamaz.
                        // Onu da sadece kolon listesinden (sourceColumns) seçim yapacak
                        // ve konfigürasyonu yönetecek şekilde güncellememiz gerekecek.
                        // Şimdilik sadece kolon listesini yolluyoruz.
                        sourceColumns={sourceColumns}
                        config={configuration}
                        setConfig={handleDetailConfigChange} 
                    />
                ) : (
                    // sourceColumns'un dolu olduğundan emin ol (artık useMemo'dan geliyor)
                    sourceColumns.length > 0 && (
                        <PivotBuilder 
                            sourceColumns={sourceColumns} // BİRLEŞTİRİLMİŞ KOLON LİSTESİ
                            initialConfig={configuration.pivot_config || {}}
                            onChange={handlePivotChange} 
                            
                            // ### STRATEJİK DEĞİŞİKLİK ###
                            // Bu Playground artık CANLI VERİ ÖNİZLEMESİ yapamaz,
                            // çünkü birden fazla tabloyu frontend'de JOIN edemeyiz.
                            // Playground artık sadece bir "konfigürasyon aracıdır".
                            // Bu yüzden 'data' prop'unu kaldırıyoruz veya boş yolluyoruz.
                            // PivotBuilder'ın data olmadan da çalışabilmesi gerekir.
                            data={{ columns: [], rows: [] }} // Boş veri yolla
                        />
                    )
                )}
            </div>
        </div>
    );
};

export default ReportPlayground;