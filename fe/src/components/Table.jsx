import React, { useState, useEffect } from 'react';
import LoadingSpinner from './LoadingSpinner';
import Badge from './Badge';
import { formatDate, truncate, getTreatmentStatus } from '../utils/helpers';

const Table = ({
  columns,
  data,
  loading = false,
  isResponsive = true,
  onRowClick,
  actions,
}) => {
  if (loading) {
    return <LoadingSpinner size="md" fullHeight={false} />;
  }

  if (data.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No data available</p>
      </div>
    );
  }

  // Desktop view
  if (!isResponsive || window.innerWidth >= 768) {
    return (
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 bg-gray-50">
              {columns.map((col) => (
                <th
                  key={col.key}
                  className="px-6 py-3 text-left text-sm font-semibold text-gray-900"
                >
                  {col.label}
                </th>
              ))}
              {actions && <th className="px-6 py-3 text-right text-sm font-semibold text-gray-900">Actions</th>}
            </tr>
          </thead>
          <tbody>
            {data.map((row, idx) => (
              <tr
                key={row.id || idx}
                className="border-b border-gray-100 hover:bg-gray-50 transition-smooth cursor-pointer"
                onClick={() => onRowClick?.(row)}
              >
                {columns.map((col) => (
                  <td key={col.key} className="px-6 py-4 text-sm text-gray-700">
                    {col.render ? col.render(row[col.key], row) : row[col.key]}
                  </td>
                ))}
                {actions && (
                  <td className="px-6 py-4 text-right">
                    {actions(row)}
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  // Mobile view - Cards
  return (
    <div className="space-y-4">
      {data.map((row, idx) => (
        <div
          key={row.id || idx}
          className="card cursor-pointer"
          onClick={() => onRowClick?.(row)}
        >
          {columns.map((col) => (
            <div key={col.key} className="flex justify-between pb-2 last:pb-0">
              <span className="font-medium text-gray-600">{col.label}</span>
              <span className="text-gray-900">
                {col.render ? col.render(row[col.key], row) : row[col.key]}
              </span>
            </div>
          ))}
          {actions && (
            <div className="flex gap-2 mt-4 border-t border-gray-200 pt-4">
              {actions(row)}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default Table;
