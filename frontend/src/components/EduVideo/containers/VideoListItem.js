// frontend/src/components/EduVideo/containers/VideoListItem.js
import React from 'react';
import PropTypes from 'prop-types';
import '../css/VideoListItem.css';

const VideoListItem = ({ video, onVideoSelect, lineNum }) => {
  const { title, thumbnail_url, video_url, description } = video; 

  const videoId = getVideoId(video_url);

  // URL geçerliyse videoId'yi çıkar, yoksa null döndür
  function getVideoId(url) {
    try {
      const urlObj = new URL(url);
      return new URLSearchParams(urlObj.search).get('v');
    } catch {
      return null;
    }
  }
  return (
    <div className="video-list-item" onClick={() => videoId ? onVideoSelect(videoId) : console.error('Invalid videoId', videoId)}>
      <div>
        <h3>
          <span>{lineNum}. </span>{title}
        </h3>
      </div>
      <div>
        <img src={thumbnail_url} alt={`Video title: ${title}`} />
      </div>
      <a
        href={video_url} 
        target="_blank"
        rel="noopener noreferrer"
      >
        Watch Video
      </a>
      <p>{description}</p>
    </div>
  );
};

VideoListItem.propTypes = {
  video: PropTypes.shape({
    title: PropTypes.string.isRequired,
    thumbnail_url: PropTypes.string.isRequired,
    video_url: PropTypes.string.isRequired, // video_url'yi doğruluyoruz.
  }).isRequired,
  onVideoSelect: PropTypes.func.isRequired,
  lineNum: PropTypes.number,
  
};


export default VideoListItem;
