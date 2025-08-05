// path: frontend/src/components/formforgeapi/api/FormForgeApiApi.js
import axiosClient from "../../../api/axiosconfig"; 

const MODULE_PATH = "/formforgeapi";

const urls = {
  departmentList: `${MODULE_PATH}/departments/`,
  departmentDetail: (id) => `${MODULE_PATH}/departments/${id}/`,
  formList: `${MODULE_PATH}/forms/`,
  formDetail: (id) => `${MODULE_PATH}/forms/${id}/`,
  // BURADAKİ URL'LER GÜNCELLENMELİ
  formFieldList: `${MODULE_PATH}/form_fields/`,
  formFieldDetail: (id) => `${MODULE_PATH}/form_fields/${id}/`,
  formSubmissionList: `${MODULE_PATH}/form_submissions/`,
  formSubmissionDetail: (id) => `${MODULE_PATH}/form_submissions/${id}/`,
  submissionValueList: `${MODULE_PATH}/submission_values/`,
  submissionValueDetail: (id) => `${MODULE_PATH}/submission_values/${id}/`,
  updateFormFieldOrder: `${MODULE_PATH}/form_fields/update_order/`,
};

const FormForgeApiApi = {
  getDepartments: () => axiosClient.get(urls.departmentList),
  getDepartment: (id) => axiosClient.get(urls.departmentDetail(id)),
  createDepartment: (data) => axiosClient.post(urls.departmentList, data),
  updateDepartment: (id, data) =>
    axiosClient.put(urls.departmentDetail(id), data),
  deleteDepartment: (id) =>
    axiosClient.delete(urls.departmentDetail(id)),

  getForms: (params) => axiosClient.get(urls.formList, { params }),
  getForm: (id) => axiosClient.get(urls.formDetail(id)),
  createForm: (data) => axiosClient.post(urls.formList, data),
  updateForm: (id, data) =>
    axiosClient.put(urls.formDetail(id), data),
  deleteForm: (id) => axiosClient.delete(urls.formDetail(id)),

  getFormFields: (params) => axiosClient.get(urls.formFieldList, { params }),
  getFormField: (id) =>
    axiosClient.get(urls.formFieldDetail(id)),
  createFormField: (data) => axiosClient.post(urls.formFieldList, data),
  updateFormField: (id, data) =>
    axiosClient.put(urls.formFieldDetail(id), data),
  deleteFormField: (id) =>
    axiosClient.delete(urls.formFieldDetail(id)),
  updateFormFieldOrder: (data) =>
    axiosClient.post(urls.updateFormFieldOrder, data),

  getFormSubmissions: (params) => axiosClient.get(urls.formSubmissionList, { params }),
  getFormSubmission: (id) =>
    axiosClient.get(urls.formSubmissionDetail(id)),
  createFormSubmission: (data) => axiosClient.post(urls.formSubmissionList, data),
  updateFormSubmission: (id, data) =>
    axiosClient.put(urls.formSubmissionDetail(id), data),
  deleteFormSubmission: (id) =>
    axiosClient.delete(urls.formSubmissionDetail(id)),

  getSubmissionValues: (params) => axiosClient.get(urls.submissionValueList, { params }),
  getSubmissionValue: (id) =>
    axiosClient.get(urls.submissionValueDetail(id)),
  createSubmissionValue: (data) => axiosClient.post(urls.submissionValueList, data),
  updateSubmissionValue: (id, data) =>
    axiosClient.put(urls.submissionValueDetail(id), data),
  deleteSubmissionValue: (id) =>
    axiosClient.delete(urls.submissionValueDetail(id)),
};

export default FormForgeApiApi;