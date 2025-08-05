// path: frontend/src/components/formforgeapi/components/page-level/FormDataListScreen.jsx
import React from "react";
import { Link } from "react-router-dom";
import useFormForgeApi from "../../hooks/useFormForgeApi";
import DataTable from "../reusable/DataTable";
import styles from "../../css/FormDataListScreen.module.css"; // ⬅️ CSS-Module

const FormDataListScreen = () => {
  const { submissions, columns } = useFormForgeApi();

  return (
    <section className={styles["form-data-list"]}>
      <Link
        to="/formforgeapi"
        className={styles["form-data-list__home-button"]}
      >
        Home
      </Link>
      <h2 className={styles["form-data-list__title"]}>Form Data List</h2>

      {/* Tablo sarmalayıcı (mobil yatay kaydırma) */}
      <div className={styles["form-data-list__table-wrapper"]}>
        <DataTable
          columns={columns}
          data={submissions}
          className={styles["form-data-list__table"]} // tabloya BEM sınıfı
        />
      </div>
    </section>
  );
};

export default FormDataListScreen;
