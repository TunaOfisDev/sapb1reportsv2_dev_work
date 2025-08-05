// path: frontend/src/components/formforgeapi/components/page-level/FormSchemaListScreen.jsx
import React from "react";
import { Link } from "react-router-dom";
import useFormForgeApi from "../../hooks/useFormForgeApi";
import styles from "../../css/FormSchemaListScreen.module.css"; // CSS-Module (BEM)

const FormSchemaListScreen = () => {
  const { forms, handleDeleteForm, handleEditForm } = useFormForgeApi();

  return (
    <section className={styles["form-schema-list"]}>
      {/* ---------- TITLE ---------- */}
      <h2 className={styles["form-schema-list__title"]}>Form Schemas</h2>

      {/* ---------- LIST ---------- */}
      <ul className={styles["form-schema-list__list"]}>
        {Array.isArray(forms) &&
          forms.map((form) => (
            <li key={form.id} className={styles["form-schema-list__item"]}>
              {/* Başlık linki */}
              <Link
                to={`/formforgeapi/builder/${form.id}`}
                className={styles["form-schema-list__link"]}
              >
                {form.title}
              </Link>

              {/* Actions */}
              <div className={styles["form-schema-list__actions"]}>
                <button
                  type="button"
                  onClick={() => handleEditForm(form.id)}
                  className={`${styles["form-schema-list__button"]} ${styles["form-schema-list__button--primary"]}`}
                >
                  Edit
                </button>

                <button
                  type="button"
                  onClick={() => handleDeleteForm(form.id)}
                  className={`${styles["form-schema-list__button"]} ${styles["form-schema-list__button--danger"]}`}
                >
                  Delete
                </button>

                <Link
                  to={`/formforgeapi/fill/${form.id}`}
                  className={`${styles["form-schema-list__button"]} ${styles["form-schema-list__button--secondary"]}`}
                >
                  Fill Form
                </Link>

                <Link
                  to={`/formforgeapi/data/${form.id}`}
                  className={`${styles["form-schema-list__button"]} ${styles["form-schema-list__button--secondary"]}`}
                >
                  View Data
                </Link>
              </div>
            </li>
          ))}
      </ul>

      {/* ---------- CREATE NEW ---------- */}
      <Link
        to="/formforgeapi/builder"
        className={`${styles["form-schema-list__button"]} ${styles["form-schema-list__button--primary"]}`}
        style={{ alignSelf: "flex-start" }}
      >
        Create New Form
      </Link>
    </section>
  );
};

export default FormSchemaListScreen;
