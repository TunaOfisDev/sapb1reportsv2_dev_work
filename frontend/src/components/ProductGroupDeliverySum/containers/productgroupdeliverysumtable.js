// frontend/src/components/ProductGroupDeliverySum/containers/productgroupdeliverysumtable.js
import React from 'react';
import { useTable } from 'react-table';
import useUpperTotal from '../utils/UpperTotal';
import FormatNumber from '../utils/FormatNumber';
import '../css/productgroupdeliverysumtable.css';

const ProductGroupDeliverySumTable = ({ data = [], year }) => {
  // Toplamları hesapla
  const uptotals = useUpperTotal(data);

  // Tablonun kolonları
  const columns = React.useMemo(
    () => [
      {
        Header: 'Yıl-Ay',
        accessor: 'yil_ay',
      },
      {
        Header: (
          <>
            Teslimat Tutarı
            <div className="product-group-delivery-table__total">
              <FormatNumber value={uptotals.teslimat_tutar} />
            </div>
          </>
        ),
        accessor: 'teslimat_tutar',
        Cell: ({ value }) => <FormatNumber value={value} />,
        headerClassName: 'product-group-delivery-table__table-header--right',
        className: 'product-group-delivery-table__table-cell--right',
      },
      {
        Header: (
          <>
            Girsberger
            <div className="product-group-delivery-table__total">
              <FormatNumber value={uptotals.teslimat_girsberger} />
            </div>
          </>
        ),
        accessor: 'teslimat_girsberger',
        Cell: ({ value }) => <FormatNumber value={value} />,
        headerClassName: 'product-group-delivery-table__table-header--right',
        className: 'product-group-delivery-table__table-cell--right',
      },
      {
        Header: (
          <>
            Mamul
            <div className="product-group-delivery-table__total">
              <FormatNumber value={uptotals.teslimat_mamul} />
            </div>
          </>
        ),
        accessor: 'teslimat_mamul',
        Cell: ({ value }) => <FormatNumber value={value} />,
        headerClassName: 'product-group-delivery-table__table-header--right',
        className: 'product-group-delivery-table__table-cell--right',
      },
      {
        Header: (
          <>
            Ticari
            <div className="product-group-delivery-table__total">
              <FormatNumber value={uptotals.teslimat_ticari} />
            </div>
          </>
        ),
        accessor: 'teslimat_ticari',
        Cell: ({ value }) => <FormatNumber value={value} />,
        headerClassName: 'product-group-delivery-table__table-header--right',
        className: 'product-group-delivery-table__table-cell--right',
      },
      {
        Header: (
          <>
            Nakliye
            <div className="product-group-delivery-table__total">
              <FormatNumber value={uptotals.teslimat_nakliye} />
            </div>
          </>
        ),
        accessor: 'teslimat_nakliye',
        Cell: ({ value }) => <FormatNumber value={value} />,
        headerClassName: 'product-group-delivery-table__table-header--right',
        className: 'product-group-delivery-table__table-cell--right',
      },
      {
        Header: (
          <>
            Montaj
            <div className="product-group-delivery-table__total">
              <FormatNumber value={uptotals.teslimat_montaj} />
            </div>
          </>
        ),
        accessor: 'teslimat_montaj',
        Cell: ({ value }) => <FormatNumber value={value} />,
        headerClassName: 'product-group-delivery-table__table-header--right',
        className: 'product-group-delivery-table__table-cell--right',
      },
    ],
    [uptotals]
  );

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    rows,
    prepareRow,
  } = useTable({ columns, data });

  return (
    <div className="product-group-delivery-table">
      <table {...getTableProps()} className="product-group-delivery-table__table">
        <thead className="product-group-delivery-table__table-head">
          {headerGroups.map(headerGroup => (
            <tr {...headerGroup.getHeaderGroupProps()} className="product-group-delivery-table__table-row">
              {headerGroup.headers.map(column => (
                <th
                  {...column.getHeaderProps()}
                  className={column.headerClassName || 'product-group-delivery-table__table-header'}
                >
                  {column.render('Header')}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody {...getTableBodyProps()} className="product-group-delivery-table__table-body">
          {rows.map(row => {
            prepareRow(row);
            return (
              <tr {...row.getRowProps()} className="product-group-delivery-table__table-row">
                {row.cells.map(cell => (
                  <td
                    {...cell.getCellProps()}
                    className={cell.column.className || 'product-group-delivery-table__table-cell'}
                  >
                    {cell.render('Cell')}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default ProductGroupDeliverySumTable;