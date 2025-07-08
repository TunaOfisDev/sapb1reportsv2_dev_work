// frontend/src/components/DynamicReport/main/DynamicTable.js
import React, { useEffect, useMemo, useState } from 'react';
import { useTable, useFilters, useSortBy, usePagination } from 'react-table';
import { getManualHeadersTypesByTableName, getAlignmentInfoByTableName } from '../../../api/dynamicreport';
import DynamicFilters from '../utils/DynamicFilters';
import DynamicPagination from '../utils/DynamicPagination';
import '../css/DynamicTable.css';

const DynamicTable = ({ data, selectedTableName }) => {
  const [columnTypes, setColumnTypes] = useState([]);
  const [alignmentIndexes, setAlignmentIndexes] = useState([]);

  useEffect(() => {
    const fetchColumnHeadersTypes = async () => {
      try {
        if (selectedTableName) {
          const columnsData = await getManualHeadersTypesByTableName(selectedTableName);
          const types = columnsData.map((item) => ({
            header_name: item.header_name,
            type: typeof item.type === 'string' ? item.type.toLowerCase() : 'unknown',
          }));
          setColumnTypes(types);
          console.log('Başlık ve Tip Bilgileri:', types);
        }
      } catch (error) {
        console.error('Kolon tiplerini alma hatası:', error);
      }
    };

    fetchColumnHeadersTypes();
  }, [selectedTableName]);

  useEffect(() => {
    const fetchAlignmentIndexes = async () => {
      try {
        if (selectedTableName) {
          const alignmentData = await getAlignmentInfoByTableName(selectedTableName);
          console.log("API'den Alınan Alignment Data:", alignmentData);
          if (alignmentData && alignmentData.alignment_indexes) {
            setAlignmentIndexes(alignmentData.alignment_indexes);
          }
        }
      } catch (error) {
        console.error('Alignment index bilgileri alınırken hata:', error);
      }
    };

    fetchAlignmentIndexes();
  }, [selectedTableName]);

  const columns = useMemo(() => {
    if (data && data.columns) {
      if (data.columns.length === 1) {
        return [
          {
            Header: data.columns[0],
            accessor: 'mergedData',
          },
        ];
      }
      return data.columns.map((col, index) => {
        return {
          Header: col,
          accessor: col,
          type: columnTypes[index] ? columnTypes[index].type : 'default',
        };
      });
    }
    return [];
  }, [data, columnTypes]);

  const tableData = useMemo(() => {
    if (data && data.columns) {
      if (data.columns.length === 1) {
        return data.rows.map((row) => {
          return { mergedData: row.join(', ') };
        });
      }
      return data.rows.map((row) => {
        return Object.fromEntries(columns.map((col, i) => [col.accessor, row[i]]));
      });
    }
    return [];
  }, [data, columns]);

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    prepareRow,
    state,
    setFilter,
    canPreviousPage,
    canNextPage,
    pageOptions,
    pageCount,
    gotoPage,
    nextPage,
    previousPage,
    page,
    setPageSize,
  } = useTable(
    {
      columns,
      data: tableData,
      initialState: { pageIndex: 0, pageSize: 10 },
    },
    useFilters,
    useSortBy,
    usePagination
  );

  if (!data || !data.columns || !data.rows) {
    return <div>Lütfen Rapor Seçin ve oluşturmak için buton basın</div>;
  }

  const handlePageSizeChange = (pageSize) => {
    setPageSize(pageSize);
  };

  return (
    <div className="dynamic-table">
      <DynamicPagination
        canPreviousPage={canPreviousPage}
        canNextPage={canNextPage}
        pageOptions={pageOptions}
        pageCount={pageCount}
        gotoPage={gotoPage}
        nextPage={nextPage}
        previousPage={previousPage}
        pageIndex={state.pageIndex}
        pageSize={state.pageSize}
        setPageSize={handlePageSizeChange}
      />

      <table {...getTableProps()}>
        <thead>
          {headerGroups.map((headerGroup) => (
            <tr {...headerGroup.getHeaderGroupProps()} className="dynamic-table__header">
              {headerGroup.headers.map((column) => (
                <th {...column.getHeaderProps(column.getSortByToggleProps())}>
                  {column.render('Header')}
                  <span className={`dynamic-table__icon--sort-${column.isSortedDesc ? 'desc' : 'asc'}`}>
                  {column.isSorted ? (column.isSortedDesc ? ' ↓' : ' ↑') : ''}
                  </span>
                </th>
              ))}
            </tr>
          ))}
          <DynamicFilters columns={headerGroups[0].headers} setFilter={setFilter} />
        </thead>
        <tbody {...getTableBodyProps()}>
          {page.map((row, index) => {
            prepareRow(row);
            return (
              <tr
                {...row.getRowProps()}
                className={`dynamic-table__row ${index % 2 === 0 ? 'dynamic-table__row--even' : ''}`}
              >
                {row.cells.map((cell, cellIndex) => {
                  const isLongText = String(cell.value).length > 100;
                  const dynamicWidth = `${String(cell.value).length * 8}px`;
                  let additionalStyles = {};
                  if (alignmentIndexes.includes(cellIndex)) {
                    additionalStyles = { textAlign: 'right' };
                  }

                  return (
                    <td
                      {...cell.getCellProps({
                        style: {
                          width: dynamicWidth,
                          ...additionalStyles,
                        },
                      })}
                      className={`dynamic-table__cell ${isLongText ? 'dynamic-table__cell--overflow' : ''}`}
                    >
                      {cell.render('Cell')}
                    </td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>

        <tfoot></tfoot>
      </table>
    </div>
  );
};

export default DynamicTable;
