// frontend/src/components/productpicture/containers/ProductPictureTable.js
import React, { useMemo, useState } from 'react';
import { useTable, useSortBy, useFilters, usePagination } from 'react-table';
import useProductPictures from '../hooks/useProductPictures';
import Pagination from '../utils/Pagination';
import PictureModal from '../utils/PictureModal';
import NumericSort  from '../utils/NumericSort';
import '../css/ProductPictureTable.css';

const DefaultColumnFilter = ({ column: { filterValue, preFilteredRows, setFilter } }) => {
  const count = preFilteredRows.length;
  return (
    <input
      value={filterValue || ''}
      onChange={e => setFilter(e.target.value || undefined)}
      placeholder={`Search ${count} records...`}
      className="product-picture-table__filter-input" 
    />
  );
};

const ProductPictureTable = () => {
  const { productPictures, loading, error} = useProductPictures();
//const defaultImagePath = process.env.REACT_APP_DEFAULT_IMAGE_PATH || 'http://10.130.212.112/backend_static/no_image.jpg';
  const defaultImagePath = process.env.REACT_APP_DEFAULT_IMAGE_PATH || `${process.env.REACT_APP_SERVER_HOST}/backend_static/no_image.jpg`;

  


  const [showModal, setShowModal] = useState(false);
  const [currentImageUrl, setCurrentImageUrl] = useState('');

  const openModal = (imageUrl) => {
    setCurrentImageUrl(imageUrl);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
  };
  

  // Manuel olarak sütun tanımları
  const columns = useMemo(() => [
    {
      Header: 'Image',
      accessor: 'picture_name',
      Cell: ({ row }) => {
        // Backend'den gelen doğru resim yolunu kullan
        const imageUrl = row.original.picture_path || defaultImagePath;
        
        return (
          <div style={{ width: '200px', height: '175px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <img 
              src={imageUrl} 
              alt={row.original.item_name || 'Product'}
              style={{ width: 'auto', height: 'auto', maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }}
              loading="lazy"
              onClick={() => openModal(imageUrl)} 
            />
          </div>
        );
      },
      disableFilters: true,
    },

    {
      Header: 'Item Code',
      accessor: 'item_code'
    },
    {
      Header: 'Item Name',
      accessor: 'item_name'
    },
    {
      Header: 'Group Name',
      accessor: 'group_name'
    },
    {
      Header: 'Price',
      accessor: 'price',
      sortType: NumericSort,
      Cell: ({ value }) => {
        return <div className="price-cell">{value}</div>;
      }
    },
    {
      Header: 'Currency',
      accessor: 'currency',
      Cell: ({ value }) => {
        return <div className="currency-cell">{value}</div>;
      }
    },  
          
  ], [defaultImagePath]);


  const data = useMemo(() => productPictures, [productPictures]);

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    prepareRow,
    page,
    canPreviousPage,
    canNextPage,
    nextPage,
    previousPage,
    gotoPage,
    pageCount,
    setPageSize,
    state: { pageIndex, pageSize }
  } = useTable(
    {
      columns,
      data,
      initialState: {
        pageIndex: 0,
        sortBy: [{ id: 'item_code', desc: false }] 
      },
      defaultColumn: { Filter: DefaultColumnFilter }
    },
    useFilters,
    useSortBy,
    usePagination
  );

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error.message}</div>;
  }

 
    return (
      <>

        <Pagination
          canNextPage={canNextPage}
          canPreviousPage={canPreviousPage}
          pageCount={pageCount}
          pageIndex={pageIndex}
          gotoPage={gotoPage}
          nextPage={nextPage}
          previousPage={previousPage}
          pageSize={pageSize}
          setPageSize={setPageSize}
        />

        
        <table {...getTableProps()} className="product-picture-table">
          <thead>
            {headerGroups.map(headerGroup => (
              <>
                <tr {...headerGroup.getHeaderGroupProps()}>
                  {headerGroup.headers.map(column => (
                    <th {...column.getHeaderProps(column.getSortByToggleProps())}>
                      {column.render('Header')}
                      <span>
                        {column.isSorted ? (column.isSortedDesc ? ' ▼' : ' ▲') : ''}
                      </span>

                    </th>
                  ))}
                </tr>
                <tr>
                  {headerGroup.headers.map(column => (
                    <th {...column.getHeaderProps()}>
                      {column.canFilter ? column.render('Filter') : null}
                    </th>
                  ))}
                </tr>
              </>
            ))}
          </thead>
          
          <tbody {...getTableBodyProps()}>
            {page.map((row) => {
              prepareRow(row);
              // Eğer 'item_code' her satır için benzersiz ise bu kullanılabilir.
              const rowKey = row.original.item_code; 
              return (
                <tr {...row.getRowProps()} key={rowKey}> 
                  {row.cells.map(cell => {
                    return (
                      <td {...cell.getCellProps()}>{cell.render('Cell')}</td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>

        </table>
        <PictureModal 
        showModal={showModal} 
        imageUrl={currentImageUrl} 
        closeModal={closeModal} 
      />
      </>
    );
  };
  
export default ProductPictureTable;
