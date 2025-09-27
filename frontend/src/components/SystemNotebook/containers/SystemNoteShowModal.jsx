// frontend/src/components/SystemNotebook/containers/SystemNoteShowModal.jsx

import React, { useEffect, useState } from 'react';
import { Modal, Input, Form, message } from 'antd';
import authService from '../../../auth/authService';

const { TextArea } = Input;

const SystemNoteShowModal = ({
  visible,
  onClose,
  onSave,
  onDelete,
  note = {},
  isNew = false,
}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const currentUserEmail = authService.getUserEmail();

  useEffect(() => {
    if (visible) {
      form.setFieldsValue({
        title: note?.title || '',
        content: note?.content || '',
      });
    }
  }, [visible, note, form]);

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);
      await onSave(
        {
          ...note,
          title: values.title.trim(),
          content: values.content.trim(),
          source: note?.source || 'admin',
        },
        note?.id || null
      );
      message.success(isNew ? 'Not oluşturuldu' : 'Not güncellendi');
      onClose();
    } catch (error) {
      console.error('Form Hatası:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = () => {
    if (note?.id && window.confirm("Bu notu silmek istediğinize emin misiniz?")) {
      onDelete(note.id);
    }
  };

  const isEditable = isNew || (note?.source === 'admin' && currentUserEmail === note?.created_by_email);

  return (
    <Modal
      open={visible}
      title={isNew ? 'Yeni Sistem Notu' : 'Sistem Notu Detayı'}
      onCancel={onClose}
      onOk={handleSubmit}
      okText={isNew ? 'Kaydet' : 'Güncelle'}
      cancelText="İptal"
      centered
      confirmLoading={loading}
      destroyOnClose
      getContainer={false}
      okButtonProps={{ disabled: !isEditable }}
    >
      <Form layout="vertical" form={form}>
        <Form.Item
          name="title"
          label="Başlık"
          rules={[{ required: true, message: 'Başlık boş olamaz' }]}
        >
          <Input placeholder="Not başlığı girin" disabled={!isEditable} />
        </Form.Item>

        <Form.Item
          name="content"
          label="İçerik"
          rules={[{ required: true, message: 'İçerik boş olamaz' }]}
        >
          <TextArea
            placeholder="Not içeriğini yazın"
            autoSize={{ minRows: 4, maxRows: 10 }}
            disabled={!isEditable}
          />
        </Form.Item>

        {!isNew && (
          <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: '#888' }}>
              Kaynak: <strong>{note?.source}</strong> · Kullanıcı: <strong>{note?.created_by_email}</strong>
            </span>

            {isEditable && (
              <button
                type="button"
                onClick={handleDelete}
                style={{
                  backgroundColor: '#e53935',
                  color: '#fff',
                  border: 'none',
                  padding: '6px 12px',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                Sil
              </button>
            )}
          </div>
        )}
      </Form>
    </Modal>
  );
};

export default SystemNoteShowModal;
