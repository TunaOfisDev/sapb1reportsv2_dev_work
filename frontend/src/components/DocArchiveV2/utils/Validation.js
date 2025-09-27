// frontend/src/components/DocArchiveV2/utils/Validation.js
/**
 * Validate the document data including file upload.
 * @param {Object} data - The document data to validate, including file.
 * @returns {Object} An object containing any errors found.
 */
const validateDocumentData = (data) => {
    let errors = {};

    // Validate document name
    if (!data.name) {
        errors.name = "Belge adı boş bırakılamaz.";
    } else if (data.name.length < 3) {
        errors.name = "Belge adı en az 3 karakter olmalıdır.";
    }

    // Validate owner name
    if (!data.owner) {
        errors.owner = "Sahip adı boş bırakılamaz.";
    }

    // Validate department
    if (!data.department) {
        errors.department = "Departman seçimi yapılmalıdır.";
    }

    // Validate file
    if (!data.file) {
        errors.file = "Dosya yüklemek zorunludur."; // Ensure file is uploaded
    }

    // Validate comments
    if (data.comments && data.comments.length > 500) {
        errors.comments = "Açıklama 500 karakterden uzun olmamalıdır.";
    }

    return errors;
};

export { validateDocumentData };

