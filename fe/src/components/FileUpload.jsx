import React, { useState } from 'react';
import Button from './Button';

const FileUpload = ({
  label,
  onUpload,
  accept = 'image/*',
  maxSize = 5242880, // 5MB
  previewEnabled = true,
  error,
  helperText,
}) => {
  const [preview, setPreview] = useState(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFile = (file) => {
    if (file.size > maxSize) {
      alert('File is too large');
      return;
    }

    if (previewEnabled) {
      const reader = new FileReader();
      reader.onload = (e) => setPreview(e.target.result);
      reader.readAsDataURL(file);
    }

    onUpload(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    handleFile(e.dataTransfer.files[0]);
  };

  return (
    <div className="mb-4">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label}
        </label>
      )}

      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-smooth cursor-pointer ${
          isDragging
            ? 'border-primary-500 bg-primary-50'
            : 'border-gray-300 bg-gray-50 hover:border-primary-300'
        }`}
      >
        <input
          type="file"
          accept={accept}
          onChange={(e) => handleFile(e.target.files[0])}
          className="hidden"
          id="file-upload"
        />
        <label htmlFor="file-upload" className="cursor-pointer">
          <p className="text-gray-600">Drag and drop or click to upload</p>
          <p className="text-sm text-gray-500 mt-1">{helperText}</p>
        </label>
      </div>

      {preview && (
        <div className="mt-4">
          <img src={preview} alt="Preview" className="max-h-48 rounded-lg mx-auto" />
        </div>
      )}

      {error && <p className="text-red-500 text-sm mt-1">{error}</p>}
    </div>
  );
};

export default FileUpload;
