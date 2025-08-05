// path: frontend/src/components/formforgeapi/components/page-level/FormBuilderScreen.jsx
import React from "react";
import { Link } from "react-router-dom";
import { Toaster, toast } from "react-hot-toast";
import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";
import useFormForgeApi from "../../hooks/useFormForgeApi";
import FormFieldCard from "../cards/FormFieldCard"; // ⬅️ Düzeltme: FormFieldCard import edildi
import styles from "../../css/FormBuilderScreen.module.css";

const FormBuilderScreen = () => {
  const {
    currentForm,
    handleFieldChange,
    handleOnDragEnd,
    handleAddFormField,
    handleDeleteFormField,
    isEditing,
    isSubmitting,
    handleSaveForm,
    departments,
    selectedDepartment,
    setSelectedDepartment,
    handleAddOption,
    handleOptionLabelChange,
    handleDeleteOption,
  } = useFormForgeApi();

  if (!currentForm) return <div>Loading...</div>;

  const handleSaveClick = async () => {
    const saving = toast.loading("Saving…");
    try {
      await handleSaveForm();
      toast.success("Saved!", { id: saving });
    } catch (e) {
      toast.error("Save failed!", { id: saving });
    }
  };

  return (
    <div className={styles["form-builder"]}>
      <Toaster position="top-right" />

      <header className={styles["form-builder__toolbar"]}>
        <div className={styles["form-builder__toolbar-left"]}>
          <h2>{isEditing ? "Edit Form" : "Create Form"}</h2>
          <Link
            to="/formforgeapi"
            className={`${styles["form-builder__button"]} ${styles["form-builder__button--home"]}`}
          >
            Home
          </Link>
        </div>

        <div className={styles["form-builder__toolbar-right"]}>
          <button
            type="button"
            onClick={handleAddFormField}
            className={`${styles["form-builder__button"]} ${styles["form-builder__button--secondary"]}`}
          >
            + Add Field
          </button>

          <button
            type="button"
            onClick={handleSaveClick}
            disabled={isSubmitting}
            className={`${styles["form-builder__button"]} ${styles["form-builder__button--primary"]}`}
          >
            {isSubmitting ? "Saving…" : "Save Form"}
          </button>
        </div>
      </header>

      <div className={styles["form-builder__field-wrapper"]}>
        <section className={styles["form-builder__field-wrapper"]}>
  <div className={styles["form-builder__meta-grid"]}>
    <label htmlFor="department-select">Department:</label>
    <select
      id="department-select"
      value={selectedDepartment}
      onChange={(e) => setSelectedDepartment(e.target.value)}
    >
      <option value="">Select a Department</option>
      {departments?.map((d) => (
        <option key={d.id} value={d.id}>
          {d.name}
        </option>
      ))}
    </select>

    <label htmlFor="form-title">Form Title:</label>
    <input
      id="form-title"
      type="text"
      name="title"
      value={currentForm.title}
      onChange={handleFieldChange}
    />

    <label htmlFor="form-desc">Description:</label>
    <textarea
      id="form-desc"
      name="description"
      value={currentForm.description}
      onChange={handleFieldChange}
    />
  </div>
</section>

        <DragDropContext onDragEnd={handleOnDragEnd}>
          <Droppable droppableId="form-fields">
            {(provided) => (
              <ul
                {...provided.droppableProps}
                ref={provided.innerRef}
                className={styles["form-builder__field-list"]}
              >
                {Array.isArray(currentForm.fields) &&
                  currentForm.fields.map((field, index) => (
                    <Draggable
                      key={field.id}
                      draggableId={field.id.toString()}
                      index={index}
                    >
                      {(prov, snap) => (
                        <FormFieldCard
                          field={field}
                          index={index}
                          provided={prov}
                          snapshot={snap}
                          handleFieldChange={handleFieldChange}
                          handleAddOption={handleAddOption}
                          handleOptionLabelChange={handleOptionLabelChange}
                          handleDeleteOption={handleDeleteOption}
                          handleDeleteFormField={handleDeleteFormField}
                        />
                      )}
                    </Draggable>
                  ))}
                {provided.placeholder}
              </ul>
            )}
          </Droppable>
        </DragDropContext>
      </div>
    </div>
  );
};

export default FormBuilderScreen;