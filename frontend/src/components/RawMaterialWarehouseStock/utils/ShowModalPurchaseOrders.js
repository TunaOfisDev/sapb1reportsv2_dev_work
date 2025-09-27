// frontend/src/components/RawMaterialWarehouseStock/utils/ShowModalPurchaseOrders.js
import React from 'react';
import Modal from 'react-modal';
import { useTable } from 'react-table';
import '../css/ShowModalPurchaseOrders.css';

const ShowModalPurchaseOrders = ({ isOpen, onRequestClose, purchaseOrders, itemCode, itemName, stockQuantity, orderQuantity }) => {
  const parsePurchaseOrders = (purchaseOrders) => {
    if (!purchaseOrders) return [];
    if (typeof purchaseOrders === 'string') {
      return purchaseOrders.split(', ').map(order => {
        const [date, supplier, comments] = order.split('-');
        return { DocDate: date, CardName: supplier, Comments: comments };
      });
    }
    return [];
  };

  const data = React.useMemo(() => parsePurchaseOrders(purchaseOrders), [purchaseOrders]);

  const columns = React.useMemo(
    () => [
      {
        Header: 'Tarih',
        accessor: 'DocDate',
      },
      {
        Header: 'Tedarikçi',
        accessor: 'CardName',
      },
      {
        Header: 'Yorumlar',
        accessor: 'Comments',
      },
    ],
    []
  );

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    rows,
    prepareRow,
  } = useTable({ columns, data });

  return (
    <Modal
      isOpen={isOpen}
      onRequestClose={onRequestClose}
      contentLabel="Verilen Siparişler"
      ariaHideApp={false}
      className="purchase-orders-modal"
      overlayClassName="purchase-orders-modal-overlay"
    >
      <h2>Verilen Siparişler</h2>
      <div className="modal-item-info">
        <div className="modal-item-row">
          <span className="modal-item-label">Kod|Tanım:</span>
          <span className="modal-item-value">{itemCode} | {itemName}</span>
        </div>
        <div className="modal-item-row">
          <span className="modal-item-label">Stok|Sipariş:</span>
          <span className="modal-item-value">{stockQuantity} | {orderQuantity}</span>
        </div>
      </div>
      <table {...getTableProps()} className="purchase-orders-table">
        <thead>
          {headerGroups.map(headerGroup => (
            <tr {...headerGroup.getHeaderGroupProps()}>
              {headerGroup.headers.map(column => (
                <th {...column.getHeaderProps()}>
                  {column.render('Header')}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody {...getTableBodyProps()}>
          {rows.map(row => {
            prepareRow(row);
            return (
              <tr {...row.getRowProps()}>
                {row.cells.map(cell => (
                  <td {...cell.getCellProps()}>
                    {cell.render('Cell')}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
      <button onClick={onRequestClose} className="close-modal-button">Kapat</button>
    </Modal>
  );
};

export default ShowModalPurchaseOrders;