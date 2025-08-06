// path: frontend/src/components/formforgeapi/api/FormForgeApiApi.js
/**
 * FormForge API Client
 * ---------------------------------------------------------
 * Tek sorumlu:  REST uç-noktalarına (Django DRF) istek atmak.
 * - axiosClient DI kullanır  (frontend/src/api/axiosconfig.js).
 * - Hiçbir iş mantığı barındırmaz, sade HTTP katmanı.
 */

import axiosClient from "../../../api/axiosconfig";

/*----------------------------------------------------------
| 1) URL Tanımları
*---------------------------------------------------------*/
const MODULE = "formforgeapi";

const urls = {
  // Department
  departments:        () => `${MODULE}/departments/`,
  departmentDetail:   (id) => `${MODULE}/departments/${id}/`,

  // Form
  forms:              (params) => `${MODULE}/forms/`, // Parametreleri desteklemek için güncellendi
  formDetail:         (id) => `${MODULE}/forms/${id}/`,
  
  // YENİ EKLENEN FORM EYLEMLERİ (ACTIONS)
  archiveForm:        (id) => `${MODULE}/forms/${id}/archive/`,
  unarchiveForm:      (id) => `${MODULE}/forms/${id}/unarchive/`, // YENİ URL
  createFormVersion:  (id) => `${MODULE}/forms/${id}/create_version/`,

  // FormField
  formFields:         () => `${MODULE}/form_fields/`,
  formFieldDetail:    (id) => `${MODULE}/form_fields/${id}/`,
  formFieldUpdateOrd: () => `${MODULE}/form_fields/update_order/`,

  // Submission / Value
  submissions:        () => `${MODULE}/form_submissions/`,
  submissionDetail:   (id) => `${MODULE}/form_submissions/${id}/`,
  values:             () => `${MODULE}/submission_values/`,
  valueDetail:        (id) => `${MODULE}/submission_values/${id}/`,
};

/*----------------------------------------------------------
| 2) Genel API Yardımcı Fonksiyonları (Generic Helpers)
*---------------------------------------------------------*/
const list   = (url, params)     => axiosClient.get(url, { params });
const detail = (url)             => axiosClient.get(url);
const create = (url, data)       => axiosClient.post(url, data);
const update = (url, data)       => axiosClient.put(url, data);
const remove = (url)             => axiosClient.delete(url);

/*----------------------------------------------------------
| 3) Dışa Aktarılan API Nesnesi
*---------------------------------------------------------*/
const FormForgeApiApi = {
  /* Department */
  getDepartments:      (params)   => list(urls.departments(), params),
  getDepartment:       (id)       => detail(urls.departmentDetail(id)),
  createDepartment:    (data)     => create(urls.departments(), data),
  updateDepartment:    (id, data) => update(urls.departmentDetail(id), data),
  deleteDepartment:    (id)       => remove(urls.departmentDetail(id)),

  /* Form */
  // GÜNCELLENDİ: getForms artık status gibi parametreleri destekliyor
  getForms:            (params)   => list(urls.forms(), params),
  getForm:             (id)       => detail(urls.formDetail(id)),
  createForm:          (data)     => create(urls.forms(), data),
  updateForm:          (id, data) => update(urls.formDetail(id), data),
  deleteForm:          (id)       => remove(urls.formDetail(id)), // Bu artık kullanılmayacak ama referans olarak kalabilir

  // YENİ EKLENEN FORM EYLEMLERİ
  archiveForm:         (id)       => create(urls.archiveForm(id), {}), // Arşivleme bir POST isteği
  unarchiveForm:       (id) => create(urls.unarchiveForm(id), {}), // YENİ METOD
  createFormVersion:   (id)       => create(urls.createFormVersion(id), {}), // Versiyonlama bir POST isteği

  /* FormField */
  getFormFields:       (params)   => list(urls.formFields(), params),
  getFormField:        (id)       => detail(urls.formFieldDetail(id)),
  createFormField:     (data)     => create(urls.formFields(), data),
  updateFormField:     (id, data) => update(urls.formFieldDetail(id), data),
  deleteFormField:     (id)       => remove(urls.formFieldDetail(id)),
  updateFormFieldOrder:(payload)  => create(urls.formFieldUpdateOrd(), payload),

  /* Submission */
  getFormSubmissions:  (params)   => list(urls.submissions(), params),
  getFormSubmission:   (id)       => detail(urls.submissionDetail(id)),
  createFormSubmission:(data)     => create(urls.submissions(), data),
  updateFormSubmission:(id, data) => update(urls.submissionDetail(id), data),
  deleteFormSubmission:(id)       => remove(urls.submissionDetail(id)),

  /* SubmissionValue (genellikle direkt kullanılmaz, submission üzerinden yönetilir) */
  getSubmissionValues: (params)   => list(urls.values(), params),
  getSubmissionValue:  (id)       => detail(urls.valueDetail(id)),
  createSubmissionValue:(data)    => create(urls.values(), data),
  updateSubmissionValue:(id, data)=> update(urls.valueDetail(id), data),
  deleteSubmissionValue:(id)      => remove(urls.valueDetail(id)),
};

export default FormForgeApiApi;