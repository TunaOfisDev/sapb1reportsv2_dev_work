// path: frontend/src/components/formforgeapi/components/page-level/FormFillScreen.jsx
import React from "react";
import { Link } from "react-router-dom";
import useFormForgeApi from "../../hooks/useFormForgeApi";
import styles from "../../css/FormFillScreen.module.css";

const FormFillScreen = () => {
  const { currentForm, register, handleSubmit, onSubmit, errors } =
    useFormForgeApi();

  if (!currentForm) return <div>Loading...</div>;

  return (
    <section className={styles["form-fill"]}>
      {/* ---------- HOME ---------- */}
      <Link to="/formforgeapi" className={styles["form-fill__home-button"]}>
        Home
      </Link>

      {/* ---------- TITLE ---------- */}
      <h2 className={styles["form-fill__title"]}>Fill Form: {currentForm.title}</h2>

      {/* ---------- FORM ---------- */}
      <form onSubmit={handleSubmit(onSubmit)} className={styles["form-fill__form"]}>
        {currentForm.fields.map((field) => (
          <div key={field.id} className={styles["form-fill__field"]}>
            <label htmlFor={field.label} className={styles["form-fill__label"]}>
              {field.label}
            </label>

            {/* Tekli seçim */}
            {field.field_type === "singleselect" && (
              <select
                id={field.label}
                className={styles["form-fill__select"]}
                {...register(field.label, { required: field.is_required })}
              >
                {field.options?.map((o) => (
                  <option key={o.id ?? o.label}>{o.label}</option>
                ))}
              </select>
            )}

            {/* Çoklu seçim */}
            {field.field_type === "multiselect" && (
              <select
                id={field.label}
                multiple
                /* En fazla 6 satır göster; seçenek sayısı daha azsa onu kullan */
                size={Math.min(field.options?.length || 4, 6)}
                className={styles["form-fill__select--multi"]}
                {...register(field.label, { required: field.is_required })}
              >
                {field.options?.map((o) => (
                  <option key={o.id ?? o.label}>{o.label}</option>
                ))}
              </select>
            )}

            {/* Diğer tipler */}
            {["text", "number", "email", "date", "textarea"].includes(field.field_type) && (
              <input
                id={field.label}
                type={field.field_type === "textarea" ? "text" : field.field_type}
                className={styles["form-fill__input"]}
                {...register(field.label, { required: field.is_required })}
              />
            )}

            {errors[field.label] && (
              <p className={styles["form-fill__error"]}>This field is required</p>
            )}
          </div>
        ))}

        {/* ---------- SUBMIT ---------- */}
        <button type="submit" className={styles["form-fill__submit-button"]}>
          Submit
        </button>
      </form>
    </section>
  );
};

export default FormFillScreen;
