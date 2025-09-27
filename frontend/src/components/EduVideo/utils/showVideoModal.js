// frontend/src/components/EduVideo/utils/showVideoModal.js
import React from 'react';
import ReactDOM from 'react-dom';
import '../css/VideoModal.css';

const VideoModal = ({ videoId, onClose }) => {
  // Eğer videoId geçerliyse embedUrl oluştur, yoksa boş string döndür
  const embedUrl = videoId ? `https://www.youtube.com/embed/${videoId}?autoplay=1` : '';

  return ReactDOM.createPortal(
    <div className="video-modal-backdrop" onClick={onClose}>
      <div className="video-modal-content" onClick={e => e.stopPropagation()}>
        <iframe
          width="840"
          height="472"
          src={embedUrl}
          frameBorder="0"
          allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          title="Embedded YouTube video player"
        ></iframe>
      </div>
    </div>,
    document.body
  );
};

export default VideoModal;
