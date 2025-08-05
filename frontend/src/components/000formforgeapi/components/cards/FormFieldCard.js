// path: frontend/src/components/formforgeapi/components/cards/FormFieldCard.jsx
import React from "react";
import { FIELD_TYPE_OPTIONS } from "../constants";
import styles from "../../css/FormFieldCard.module.css";   /* ⬅️ yeni CSS-Module */

const FormFieldCard = ({
  field,
  index,
  provided,
  snapshot,
  handleFieldChange,
  handleAddOption,
  handleOptionLabelChange,
  handleDeleteOption,
  handleDeleteFormField,
}) => (
  <li
    ref={provided.innerRef}
    {...provided.draggableProps}
    {...provided.dragHandleProps}
    className={`${styles["form-field-card"]} ${
      snapshot.isDragging ? styles["form-field-card--dragging"] : ""
    }`}
  >
    {/* ===== LABEL ===== */}
    <input
      className={styles["form-field-card__input"]}
      type="text"
      placeholder="Label"
      name="label"
      value={field.label}
      onChange={(e) => handleFieldChange(e, field.id)}
    />

    {/* ===== FIELD TYPE ===== */}
    <select
      className={styles["form-field-card__select"]}
      name="field_type"
      value={field.field_type}
      onChange={(e) => handleFieldChange(e, field.id)}
    >
      {FIELD_TYPE_OPTIONS.map((opt) => (
        <option key={opt.value} value={opt.value}>
          {opt.label}
        </option>
      ))}
    </select>

    {/* ===== IS_MASTER ===== */}
    <label className={styles["form-field-card__checkbox"]}>
      <input
        type="checkbox"
        name="is_master"
        checked={field.is_master || false}
        onChange={(e) => handleFieldChange(e, field.id)}
      />
      Ana Alan
    </label>

    {/* ===== IS_REQUIRED ===== */}
    <label className={styles["form-field-card__checkbox"]}>
      <input
        type="checkbox"
        name="is_required"
        checked={field.is_required || false}
        onChange={(e) => handleFieldChange(e, field.id)}
      />
      Zorunlu
    </label>

    {/* ===== ORDER BADGE ===== */}
    <span className={styles["form-field-card__order-badge"]}>
      #{index + 1}
    </span>

    {/* ===== OPTIONS (single / multi select) ===== */}
    {(field.field_type === "singleselect" ||
      field.field_type === "multiselect") && (
      <div className={styles["form-field-card__options"]}>
        {field.options?.map((opt) => (
          <div
            key={opt.id}
            className={styles["form-field-card__option-item"]}
          >
            <input
              type="text"
              value={opt.label}
              placeholder="Option label"
              onChange={(e) =>
                handleOptionLabelChange(field.id, opt.id, e.target.value)
              }
              className={styles["form-field-card__input"]}
            />
            <button
              type="button"
              onClick={() => handleDeleteOption(field.id, opt.id)}
              className={`${styles["form-field-card__button"]} ${styles["form-field-card__button--danger"]}`}
              title="Seçeneği sil"
            >
              ×
            </button>
          </div>
        ))}

        <button
          type="button"
          onClick={() => handleAddOption(field.id)}
          className={`${styles["form-field-card__button"]} ${styles["form-field-card__button--secondary"]}`}
        >
          + Add Option
        </button>
      </div>
    )}

    {/* ===== DELETE FIELD ===== */}
    <button
      type="button"
      onClick={() => handleDeleteFormField(field.id)}
      className={`${styles["form-field-card__button"]} ${styles["form-field-card__button--danger"]}`}
    >
      Delete
    </button>
  </li>
);

export default FormFieldCard;
