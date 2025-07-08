// frontend/src/components/EduVideo/containers/EduVideo.js
import React, { useState } from 'react';
import VideoListItem from './VideoListItem';
import useVideos from '../hooks/useVideos';
import VideoModal from '../utils/showVideoModal';
import Pagination from '../utils/Pagination';
import SearchBar from '../utils/SearchBar';
import '../css/EduVideo.css';

const VideoListContainer = () => {
  const { videos, loading, error } = useVideos();
  const [modalVideoId, setModalVideoId] = useState(null);
  const [searchResults, setSearchResults] = useState([]);
  const [pageIndex, setPageIndex] = useState(0);
  const [pageSize, setPageSize] = useState(10);

  const handleVideoClick = videoId => {
    // Sadece geçerli bir videoId varsa modalVideoId'yi set et
    if (videoId) {
      setModalVideoId(videoId);
    } else {
      console.error('Invalid videoId:', videoId);
      // Burada uygun bir kullanıcı bildirimi yapılabilir.
    }
  };

  const handleCloseModal = () => {
    setModalVideoId(null);
  };

  const handleSearch = searchTerm => {
    const filteredVideos = videos.filter(video =>
      video.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (video.description && video.description.toLowerCase().includes(searchTerm.toLowerCase()))
    );
    setSearchResults(filteredVideos);
  };

  const displayedVideos = searchResults.length > 0 ? searchResults : videos;
  const paginatedVideos = displayedVideos.slice(pageIndex * pageSize, (pageIndex + 1) * pageSize);

  const handlePageChange = newPageIndex => {
    setPageIndex(newPageIndex);
  };

  const handlePageSizeChange = newSize => {
    setPageSize(newSize);
    setPageIndex(0);
  };

  return (
    <div className="video-list-container">
      <div className="flex-container">
      <SearchBar onSearch={handleSearch} />
      <Pagination
        canPreviousPage={pageIndex > 0}
        canNextPage={pageIndex < Math.ceil(displayedVideos.length / pageSize) - 1}
        pageIndex={pageIndex}
        pageCount={Math.ceil(displayedVideos.length / pageSize)}
        gotoPage={handlePageChange}
        pageSize={pageSize}
        setPageSize={handlePageSizeChange}
      />
      </div>
      {loading ? (
        <p>Yükleniyor...</p>
      ) : error ? (
        <p>Hata: {error}</p>
      ) : (
        <ul className="video-list-container__list">
          {paginatedVideos.map((video, index) => (
            <VideoListItem
              key={video.id}
              video={video}
              onVideoSelect={handleVideoClick}
              lineNum={pageIndex * pageSize + index + 1} // `lineNum` prop'u burada ekleniyor
            />
          ))}
        </ul>
      )}
      {modalVideoId && <VideoModal videoId={modalVideoId} onClose={handleCloseModal} />}
    </div>
  );
};

export default VideoListContainer;