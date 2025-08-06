// path: frontend/src/components/formforgeapi/utils/ViewSubmissionModal.jsx

import React from 'react';
import { Modal, ModalHeader, ModalBody, ModalFooter, Button } from 'reactstrap';

const ViewSubmissionModal = ({ isOpen, onClose, submission }) => {
    if (!submission) return null;

    return (
        <Modal isOpen={isOpen} toggle={onClose}>
            <ModalHeader toggle={onClose}>
                Form Gönderim Detayı (ID: {submission.id})
            </ModalHeader>
            <ModalBody>
                <dl className="row">
                    {submission.values.map(item => (
                        <React.Fragment key={item.form_field}>
                            <dt className="col-sm-4">{item.form_field_label || 'Alan'}</dt>
                            <dd className="col-sm-8">{item.value}</dd>
                        </React.Fragment>
                    ))}
                    <hr className="my-2"/>
                    <dt className="col-sm-4">Gönderen</dt>
                    {/* GÜNCELLEME: .username yerine .email kullanıyoruz. */}
                    <dd className="col-sm-8">{submission.created_by?.email}</dd>
                    <dt className="col-sm-4">Tarih</dt>
                    <dd className="col-sm-8">{new Date(submission.created_at).toLocaleString()}</dd>
                </dl>
            </ModalBody>
            <ModalFooter>
                <Button color="secondary" onClick={onClose}>
                    Kapat
                </Button>
            </ModalFooter>
        </Modal>
    );
};

export default ViewSubmissionModal;