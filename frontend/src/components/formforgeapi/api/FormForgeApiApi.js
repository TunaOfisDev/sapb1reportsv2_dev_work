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
  departments:       () => `${MODULE}/departments/`,
  departmentDetail:  (id) => `${MODULE}/departments/${id}/`,

  // Form
  forms:             (params) => `${MODULE}/forms/`,
  formDetail:        (id) => `${MODULE}/forms/${id}/`,
  
  // FORM EYLEMLERİ (ACTIONS)
  archiveForm:       (id) => `${MODULE}/forms/${id}/archive/`,
  unarchiveForm:     (id) => `${MODULE}/forms/${id}/unarchive/`,
  createFormVersion: (id) => `${MODULE}/forms/${id}/create-version/`,

  // FormField
  formFields:        () => `${MODULE}/form_fields/`,
  formFieldDetail:   (id) => `${MODULE}/form_fields/${id}/`,
  formFieldUpdateOrd:() => `${MODULE}/form_fields/update_order/`,

  // Submission / Value
  submissions:       () => `${MODULE}/form_submissions/`,
  submissionDetail:  (id) => `${MODULE}/form_submissions/${id}/`,
  submissionHistory:  (id) => `${MODULE}/form_submissions/${id}/history/`,
  values:            () => `${MODULE}/submission_values/`,
  valueDetail:       (id) => `${MODULE}/submission_values/${id}/`,
};

/*----------------------------------------------------------
| 2) Genel API Yardımcı Fonksiyonları (Generic Helpers)
*---------------------------------------------------------*/
const list   = (url, params)   => axiosClient.get(url, { params });
const detail = (url)           => axiosClient.get(url);
const create = (url, data)     => axiosClient.post(url, data);
const update = (url, data)     => axiosClient.put(url, data);
const remove = (url)           => axiosClient.delete(url);

/*----------------------------------------------------------
| 3) Dışa Aktarılan API Nesnesi
*---------------------------------------------------------*/
const FormForgeApiApi = {
  /* Department */
  getDepartments:   (params)   => list(urls.departments(), params),
  getDepartment:    (id)       => detail(urls.departmentDetail(id)),
  createDepartment: (data)     => create(urls.departments(), data),
  updateDepartment: (id, data) => update(urls.departmentDetail(id), data),
  deleteDepartment: (id)       => remove(urls.departmentDetail(id)),

  /* Form */
  getForms:          (params)   => list(urls.forms(), params),
  getForm:           (id)       => detail(urls.formDetail(id)),
  createForm:        (data)     => create(urls.forms(), data),
  updateForm:        (id, data) => update(urls.formDetail(id), data),
  deleteForm:        (id)       => remove(urls.formDetail(id)),

  // FORM EYLEMLERİ
  archiveForm:       (id) => create(urls.archiveForm(id), {}),
  unarchiveForm:     (id) => create(urls.unarchiveForm(id), {}),
  createFormVersion: (id) => create(urls.createFormVersion(id), {}),

  /* FormField */
  getFormFields:        (params)   => list(urls.formFields(), params),
  getFormField:         (id)       => detail(urls.formFieldDetail(id)),
  createFormField:      (data)     => create(urls.formFields(), data),
  updateFormField:      (id, data) => update(urls.formFieldDetail(id), data),
  deleteFormField:      (id)       => remove(urls.formFieldDetail(id)),
  updateFormFieldOrder: (payload)  => create(urls.formFieldUpdateOrd(), payload),

  /* Submission */
  getFormSubmissions:   (params)   => list(urls.submissions(), params),
  getFormSubmission:    (id)       => detail(urls.submissionDetail(id)),
  createFormSubmission: (data)     => create(urls.submissions(), data),
  // GÜNCELLEME: Bu fonksiyon, backend'deki yeni versiyonlama mantığını tetikleyecektir.
  updateFormSubmission: (id, data) => update(urls.submissionDetail(id), data),
  getSubmissionHistory: (id)       => detail(urls.submissionHistory(id)),
  deleteFormSubmission: (id)       => remove(urls.submissionDetail(id)),

  /* SubmissionValue */
  getSubmissionValues: (params)   => list(urls.values(), params),
  getSubmissionValue:  (id)       => detail(urls.valueDetail(id)),
  createSubmissionValue:(data)    => create(urls.values(), data),
  updateSubmissionValue:(id, data)=> update(urls.valueDetail(id), data),
  deleteSubmissionValue:(id)      => remove(urls.valueDetail(id)),
};

export default FormForgeApiApi;