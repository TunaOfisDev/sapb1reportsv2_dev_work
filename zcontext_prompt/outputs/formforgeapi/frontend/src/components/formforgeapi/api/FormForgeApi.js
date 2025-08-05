// path: frontend/src/components/formforgeapi/api/FormForgeApi.js
import axiosClient from "../../../utils/axiosClient";

const formforgeapiApi = {
    getAllDepartments: (params) => {
        const url = '/formforgeapi/departments/';
        return axiosClient.get(url, { params });
    },
    getAllForms: (params) => {
        const url = '/formforgeapi/forms/';
        return axiosClient.get(url, { params });
    },
    getFormFields: (formId) => {
        const url = `/formforgeapi/form-fields/?form=${formId}`;
        return axiosClient.get(url);
    },
    createFormSubmission: (data) => {
        const url = '/formforgeapi/form-submissions/';
        return axiosClient.post(url, data);
    },
    getFormSubmissions: (formId, params) => {
      const url = `/formforgeapi/form-submissions/?form=${formId}`;
      return axiosClient.get(url, { params });
    },
    deleteForm: (formId) => {
        const url = `/formforgeapi/forms/${formId}/`;
        return axiosClient.delete(url);
    }
};

export { formforgeapiApi };

