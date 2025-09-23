import React from 'react';

const DataTable = ({ 
  data = [], 
  columns = [], 
  className = '',
  onRowClick,
  loading = false 
}) => {
  if (loading) {
    return (
      <div className={`card ${className}`}>
        <div className="p-8 text-center">
          <div className="animate-spin text-blue">Loading...</div>
        </div>
      </div>
    );
  }

  if (!data.length) {
    return (
      <div className={`card ${className}`}>
        <div className="p-8 text-center text-secondary">
          No data available
        </div>
      </div>
    );
  }

  return (
    <div className={`card ${className}`}>
      <div className="overflow-x-auto">
        <table className="table">
          <thead>
            <tr>
              {columns.map((column, index) => (
                <th key={index} className={column.className || ''}>
                  {column.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, rowIndex) => (
              <tr 
                key={rowIndex} 
                className={onRowClick ? 'cursor-pointer' : ''}
                onClick={() => onRowClick?.(row)}
              >
                {columns.map((column, colIndex) => (
                  <td key={colIndex} className={column.className || ''}>
                    {column.render ? column.render(row[column.key], row) : row[column.key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DataTable;