// path: frontend/src/components/formforgeapi/containers/FormForgeApiContainer.jsx
import React from "react";
import { Route, Routes } from "react-router-dom";
import FormSchemaListScreen from "../components/page-level/FormSchemaListScreen";
import FormBuilderScreen from "../components/page-level/FormBuilderScreen";
import FormFillScreen from "../components/page-level/FormFillScreen";
import FormDataListScreen from "../components/page-level/FormDataListScreen";

const FormForgeApiContainer = () => {
  return (
    <Routes>
      <Route path="/" element={<FormSchemaListScreen />} />
      <Route path="/builder" element={<FormBuilderScreen />} />
      <Route path="/builder/:id" element={<FormBuilderScreen />} />
      <Route path="/fill/:id" element={<FormFillScreen />} />
      <Route path="/data/:id" element={<FormDataListScreen />} />
    </Routes>
  );
};

export default FormForgeApiContainer;
