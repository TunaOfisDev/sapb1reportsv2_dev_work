// path: frontend/src/components/formforgeapi/components/containers/FormForgeApiContainer.jsx
import React from 'react';
import { Routes, Route } from 'react-router-dom';
import FormBuilderScreen from '../components/page-level/FormBuilderScreen';
import FormSchemaListScreen from '../components/page-level/FormSchemaListScreen';
import FormDataListScreen from '../components/page-level/FormDataListScreen';
import FormFillScreen from '../components/page-level/FormFillScreen';

const FormForgeApiContainer = () => {
    return (
        <Routes>
            <Route path="/" element={<FormSchemaListScreen />} />
            <Route path="/create" element={<FormBuilderScreen />} />
            <Route path="/data/:formId" element={<FormDataListScreen />} />
            <Route path="/fill/:formId" element={<FormFillScreen />} />
            <Route path="/edit/:formId" element={<FormBuilderScreen />} /> {/* Düzenleme ekranı için FormBuilderScreen'i kullanabiliriz */}
        </Routes>
    );
};

export default FormForgeApiContainer;
