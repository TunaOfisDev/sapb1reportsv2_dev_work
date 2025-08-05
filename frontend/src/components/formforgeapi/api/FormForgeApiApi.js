// path: frontend/src/components/formforgeapi/api/FormForgeApiApi.js
/**
 * FormForge API Client
 * ---------------------------------------------------------
 * Tek sorumlu:  REST uç-noktalarına (Django DRF) istek atmak.
 * - axiosClient DI kullanır  (frontend/src/api/axiosconfig.js).
 * - Hiçbir iş mantığı barındırmaz, sade HTTP katmanı.
 *
 * NOT:  “sections / grid” ön-yüz iyileştirmeleri backend
 *       veri modelini değiştirmedi; mevcut uç-noktalar korunur.
 */

import axiosClient from "../../../api/axiosconfig";

/*----------------------------------------------------------
| 1) URL’ler
*---------------------------------------------------------*/
const MODULE = "formforgeapi";

const urls = {
  // Department
  departments:        () => `${MODULE}/departments/`,
  departmentDetail:   (id) => `${MODULE}/departments/${id}/`,

  // Form
  forms:              () => `${MODULE}/forms/`,
  formDetail:         (id) => `${MODULE}/forms/${id}/`,

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
| 2) Generic CRUD helpers
*---------------------------------------------------------*/
const list   = (url, params)     => axiosClient.get(url, { params });
const detail = (url)             => axiosClient.get(url);
const create = (url, data)       => axiosClient.post(url, data);
const update = (url, data)       => axiosClient.put(url, data);
const remove = (url)             => axiosClient.delete(url);

/*----------------------------------------------------------
| 3) Dışa Aktarılan API nesnesi
*---------------------------------------------------------*/
const FormForgeApiApi = {
  /* Department */
  getDepartments:      (p)        => list  (urls.departments(), p),
  getDepartment:       (id)       => detail(urls.departmentDetail(id)),
  createDepartment:    (d)        => create(urls.departments(), d),
  updateDepartment:    (id, d)    => update(urls.departmentDetail(id), d),
  deleteDepartment:    (id)       => remove(urls.departmentDetail(id)),

  /* Form */
  getForms:            (p)        => list  (urls.forms(), p),
  getForm:             (id)       => detail(urls.formDetail(id)),
  createForm:          (d)        => create(urls.forms(), d),
  updateForm:          (id, d)    => update(urls.formDetail(id), d),
  deleteForm:          (id)       => remove(urls.formDetail(id)),

  /* FormField */
  getFormFields:       (p)        => list  (urls.formFields(), p),
  getFormField:        (id)       => detail(urls.formFieldDetail(id)),
  createFormField:     (d)        => create(urls.formFields(), d),
  updateFormField:     (id, d)    => update(urls.formFieldDetail(id), d),
  deleteFormField:     (id)       => remove(urls.formFieldDetail(id)),
  updateFormFieldOrder:(payload)  => create(urls.formFieldUpdateOrd(), payload),

  /* Submission */
  getFormSubmissions:  (p)        => list  (urls.submissions(), p),
  getFormSubmission:   (id)       => detail(urls.submissionDetail(id)),
  createFormSubmission:(d)        => create(urls.submissions(), d),
  updateFormSubmission:(id, d)    => update(urls.submissionDetail(id), d),
  deleteFormSubmission:(id)       => remove(urls.submissionDetail(id)),

  /* SubmissionValue */
  getSubmissionValues: (p)        => list  (urls.values(), p),
  getSubmissionValue:  (id)       => detail(urls.valueDetail(id)),
  createSubmissionValue:(d)       => create(urls.values(), d),
  updateSubmissionValue:(id, d)   => update(urls.valueDetail(id), d),
  deleteSubmissionValue:(id)      => remove(urls.valueDetail(id)),
};

export default FormForgeApiApi;
