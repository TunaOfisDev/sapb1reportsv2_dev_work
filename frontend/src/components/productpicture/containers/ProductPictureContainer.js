// frontend/src/components/productpicture/containers/ProductPictureContainer.js
import React, { Suspense, lazy } from 'react';
import useProductPictures from '../hooks/useProductPictures';
import useAuth from '../../../auth/useAuth';
import SkeletonLoader from '../utils/SkeletonLoader';
import ErrorMessage from '../utils/ErrorMessage';
import LoadingSpinner from '../utils/LoadingSpinner'; // Burada ekliyoruz
import '../css/ProductPictureContainer.css';

const ProductPictureTable = lazy(() => import('./ProductPictureTable'));

const ProductPictureContainer = () => {
  const { isAuthenticated } = useAuth();
  const { productPictures, loading, error, fetchInstantData, fetchLocalData } = useProductPictures();

  if (!isAuthenticated) {
    return <ErrorMessage message="Sayfayı görüntülemek için lütfen login olun." />;
  }

  // Eğer veri yükleniyorsa, LoadingSpinner'ı göster
  if (loading) {
    return <LoadingSpinner isLoading={loading} />;
  }

  if (error) {
    return <ErrorMessage message={error.message} />;
  }

  // Veri yüklendikten sonra, ProductPictureTable bileşenini göster
  return (
      <div className="product-picture-container">
      <h1 className="product-picture-container__title">Product Pictures</h1>
      <div className="product-picture-container__button-wrapper">
      <button className="product-picture-container__button" onClick={fetchInstantData}>Fetch Instant Data</button>
      <button className="product-picture-container__button" onClick={fetchLocalData}>Fetch Local Data</button>
      </div>

  <Suspense fallback={<SkeletonLoader />}>
    <ProductPictureTable productPictures={productPictures} />
  </Suspense>
</div>
);
};

export default ProductPictureContainer;
