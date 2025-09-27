// frontend/src/components/salesorder/containers/SalesOrderTable.js
import React, { useMemo } from 'react';
import { useTable, useSortBy, useFilters, usePagination } from 'react-table';
import Pagination from '../utils/Pagination';

// Props olarak salesOrders, loading ve error ekleyin
const SalesOrderTable = ({ salesOrders, loading, error }) => {
  const columns = useMemo(
    () => [
      { Header: 'Satıcı', accessor: 'satici' },
      { Header: 'Belge Türü', accessor: 'belge_tur' },
      { Header: 'Onay1 Durumu', accessor: 'onay1_status' },
      { Header: 'Onay2 Durumu', accessor: 'onay2_status' },
      { Header: 'Belge Tarihi', accessor: 'belge_tarihi' },
      { Header: 'Belge Onay', accessor: 'belge_onay' },
      { Header: 'Müşteri Kodu', accessor: 'musteri_kod' },
      { Header: 'Müşteri Adı', accessor: 'musteri_ad' },
      // Diğer model alanlarınızı da bu şekilde ekleyebilirsiniz.
    ],
    []
  );

  const data = useMemo(() => salesOrders, [salesOrders]);

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    prepareRow,
    page,
    canPreviousPage,
    canNextPage,
    pageCount,
    gotoPage,
    nextPage,
    previousPage,
    setPageSize,
    state: { pageIndex, pageSize },
  } = useTable(
    { columns, data, initialState: { pageIndex: 0 } },
    useFilters,
    useSortBy,
    usePagination
  );

  // Yükleme ve hata durumlarını yönetin
  if (loading) return <div>Yükleniyor...</div>;
  if (error) return <div>Hata: {error.message}</div>;

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
      <table {...getTableProps()}>
        <thead>
          {headerGroups.map(headerGroup => (
            <tr {...headerGroup.getHeaderGroupProps()}>
              {headerGroup.headers.map(column => (
                <th {...column.getHeaderProps()}>{column.render('Header')}</th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody {...getTableBodyProps()}>
          {page.map(row => {
            prepareRow(row);
            return (
              <tr {...row.getRowProps()}>
                {row.cells.map(cell => (
                  <td {...cell.getCellProps()}>{cell.render('Cell')}</td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </>
  );
};

export default SalesOrderTable;

