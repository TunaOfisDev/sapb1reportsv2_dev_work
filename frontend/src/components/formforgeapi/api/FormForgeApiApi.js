// path: frontend/src/components/formforgeapi/api/FormForgeApiApi.js

import axiosClient from "../../../api/axiosconfig";

/*----------------------------------------------------------
| 1) URL Tanımları
*---------------------------------------------------------*/
const MODULE = "formforgeapi";

const urls = {
  departments:        () => `${MODULE}/departments/`,
  departmentDetail:   (id) => `${MODULE}/departments/${id}/`,
  forms:              (params) => `${MODULE}/forms/`,
  formDetail:         (id) => `${MODULE}/forms/${id}/`,
  archiveForm:        (id) => `${MODULE}/forms/${id}/archive/`,
  unarchiveForm:      (id) => `${MODULE}/forms/${id}/unarchive/`,
  createFormVersion:  (id) => `${MODULE}/forms/${id}/create-version/`,
  formFields:         () => `${MODULE}/form_fields/`,
  formFieldDetail:    (id) => `${MODULE}/form_fields/${id}/`,
  formFieldUpdateOrd: () => `${MODULE}/form_fields/update_order/`,
  formFieldAddOption: (fieldId) => `${MODULE}/form_fields/${fieldId}/add-option/`,
  submissions:        () => `${MODULE}/form_submissions/`,
  submissionDetail:   (id) => `${MODULE}/form_submissions/${id}/`,
  submissionHistory:  (id) => `${MODULE}/form_submissions/${id}/history/`,
  users:              () => `${MODULE}/users/`,
  values:             () => `${MODULE}/submission_values/`,
  valueDetail:        (id) => `${MODULE}/submission_values/${id}/`,
};

/*----------------------------------------------------------
| 2) Genel API Yardımcı Fonksiyonları
*---------------------------------------------------------*/
const list   = (url, params) => axiosClient.get(url, { params });
const detail = (url)         => axiosClient.get(url);
const create = (url, data)   => axiosClient.post(url, data); // POST isteği gönderir
const update = (url, data)   => axiosClient.put(url, data);   // PUT isteği gönderir
const remove = (url)         => axiosClient.delete(url);

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
  getForms:        (params)   => list(urls.forms(), params),
  getForm:         (id)       => detail(urls.formDetail(id)),
  createForm:      (data)     => create(urls.forms(), data),
  updateForm:      (id, data) => update(urls.formDetail(id), data),
  deleteForm:      (id)       => remove(urls.formDetail(id)),
  archiveForm:     (id)       => create(urls.archiveForm(id), {}),
  unarchiveForm:   (id)       => create(urls.unarchiveForm(id), {}),
  createFormVersion: (id)     => create(urls.createFormVersion(id), {}),

  /* FormField */
  getFormFields:      (params)   => list(urls.formFields(), params),
  getFormField:       (id)       => detail(urls.formFieldDetail(id)),
  addFormFieldOption: (fieldId, optionData) => create(urls.formFieldAddOption(fieldId), optionData),
  createFormField:    (data)     => create(urls.formFields(), data),
  updateFormField:    (id, data) => update(urls.formFieldDetail(id), data),
  deleteFormField:    (id)       => remove(urls.formFieldDetail(id)),
  
  // DÜZELTME: Backend'deki bağımsız UpdateFormFieldOrderView (APIView) 'POST' bekliyor.
  // Bu yüzden 'update' (PUT) yerine 'create' (POST) kullanmalıyız.
  updateFormFieldOrder: (payload)  => create(urls.formFieldUpdateOrd(), payload),

  /* Submission */
  getFormSubmissions:   (params)   => list(urls.submissions(), params),
  getFormSubmission:    (id)       => detail(urls.submissionDetail(id)),
  createFormSubmission: (data)     => create(urls.submissions(), data),
  updateFormSubmission: (id, data) => update(urls.submissionDetail(id), data),
  getSubmissionHistory: (id)       => detail(urls.submissionHistory(id)),
  getUsers:             (params)   => list(urls.users(), params),
  deleteFormSubmission: (id)       => remove(urls.submissionDetail(id)),

  /* SubmissionValue */
  getSubmissionValues: (params)   => list(urls.values(), params),
  getSubmissionValue:  (id)       => detail(urls.valueDetail(id)),
  createSubmissionValue:(data)    => create(urls.values(), data),
  updateSubmissionValue:(id, data)=> update(urls.valueDetail(id), data),
  deleteSubmissionValue:(id)      => remove(urls.valueDetail(id)),
};

export default FormForgeApiApi;