// path: frontend/src/components/formforgeapi/components/components/page-level/FormBuilderScreen.jsx
import React, { useState } from 'react';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { useForm, useFieldArray } from "react-hook-form";
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from "yup";
import styles from '../../../css/FormForgeAPI.module.css';

const schema = yup.object().shape({
    title: yup.string().required("Form başlığı zorunludur."),
    department: yup.number().required("Departman seçimi zorunludur."),
    fields: yup.array().of(
        yup.object().shape({
            label: yup.string().required("Etiket zorunludur."),
            field_type: yup.string().required("Alan tipi zorunludur."),
        })
    )
});

const FormBuilderScreen = () => {
    const { register, control, handleSubmit, formState: { errors } } = useForm({
        resolver: yupResolver(schema),
        defaultValues: {
            fields: [{ label: "", field_type: "text", is_required: false, is_master: false }]
        }
    });
    const { fields, append, remove, move } = useFieldArray({
        control,
        name: "fields"
    });

    const onSubmit = data => console.log(data);

    const handleOnDragEnd = (result) => {
        if (!result.destination) return;
        move(result.source.index, result.destination.index);
    }

    return (
        <form onSubmit={handleSubmit(onSubmit)}>
            <div>
                <label htmlFor="title">Form Başlığı</label>
                <input type="text" {...register("title")} />
                <p>{errors.title?.message}</p>
            </div>
            <div>
                <label htmlFor="department">Departman</label>
                <select {...register("department")}>
                    <option value="">Seçiniz</option>
                    {/* Departmanları backend'den çekip burada listeleyeceğiz */}
                    <option value="1">Departman 1</option>
                    <option value="2">Departman 2</option>
                </select>
                <p>{errors.department?.message}</p>
            </div>

            <DragDropContext onDragEnd={handleOnDragEnd}>
                <Droppable droppableId="fields">
                    {(provided) => (
                        <ul {...provided.droppableProps} ref={provided.innerRef}>
                            {fields.map((field, index) => (
                                <Draggable key={field.id} draggableId={field.id} index={index}>
                                    {(provided) => (
                                        <li {...provided.draggableProps} {...provided.dragHandleProps} ref={provided.innerRef}>
                                            <div>
                                                <label htmlFor={`fields.${index}.label`}>Etiket</label>
                                                <input type="text" {...register(`fields.${index}.label`)} />
                                                <p>{errors.fields?.[index]?.label?.message}</p>
                                            </div>
                                            <div>
                                                <label htmlFor={`fields.${index}.field_type`}>Alan Tipi</label>
                                                <select {...register(`fields.${index}.field_type`)}>
                                                    <option value="text">Metin</option>
                                                    <option value="number">Sayı</option>
                                                    <option value="date">Tarih</option>
                                                    {/* Diğer alan tipleri */}
                                                </select>
                                                <p>{errors.fields?.[index]?.field_type?.message}</p>
                                            </div>
                                            <div>
                                                <input type="checkbox" {...register(`fields.${index}.is_required`)} />
                                                <label htmlFor={`fields.${index}.is_required`}>Zorunlu</label>
                                            </div>
                                            <div>
                                                <input type="checkbox" {...register(`fields.${index}.is_master`)} />
                                                <label htmlFor={`fields.${index}.is_master`}>Ana Listede Göster</label>
                                            </div>
                                            <button type="button" onClick={() => remove(index)}>Alanı Kaldır</button>
                                        </li>
                                    )}
                                </Draggable>
                            ))}
                            {provided.placeholder}
                        </ul>
                    )}
                </Droppable>
            </DragDropContext>

            <button type="button" onClick={() => append({ label: "", field_type: "text", is_required: false, is_master: false })}>Alan Ekle</button>
            <input type="submit" />
        </form>
    );
};

export default FormBuilderScreen;
