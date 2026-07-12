import { useState } from 'react';
import { XMarkIcon, ArrowDownTrayIcon, DocumentIcon, CheckCircleIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';
import api from '../services/api';

export default function BulkUploadModal({ isOpen, onClose, onImportComplete }) {
  const [file, setFile] = useState(null);
  const [importing, setImporting] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleDownloadTemplate = async () => {
    try {
      const response = await api.get('/api/members/bulk-upload/template', {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'member_import_template.xlsx');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Failed to download template:', err);
      setError('Failed to download template. Please try again.');
    }
  };

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      const validExtensions = ['.xlsx', '.xls'];
      const fileExtension = selectedFile.name.substring(selectedFile.name.lastIndexOf('.')).toLowerCase();
      
      if (!validExtensions.includes(fileExtension)) {
        setError('Please upload a valid Excel file (.xlsx or .xls)');
        setFile(null);
        return;
      }

      setFile(selectedFile);
      setError('');
      setResult(null);
    }
  };

  const handleImport = async () => {
    if (!file) {
      setError('Please select a file to upload');
      return;
    }

    setImporting(true);
    setError('');
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);

    console.log('DEBUG: Starting bulk upload');
    console.log('DEBUG: File:', file.name, file.size, file.type);
    console.log('DEBUG: FormData entries:');
    for (let [key, value] of formData.entries()) {
      console.log(`  ${key}:`, value);
    }

    try {
      console.log('DEBUG: Sending POST request to /api/members/bulk-upload');
      const response = await api.post('/api/members/bulk-upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      console.log('DEBUG: Response received:', response.status, response.data);
      setResult(response.data);
      if (response.data.success_count > 0) {
        onImportComplete();
      }
    } catch (err) {
      console.error('DEBUG: Import failed with error:', err);
      console.error('DEBUG: Error response:', err.response);
      console.error('DEBUG: Error data:', err.response?.data);
      console.error('DEBUG: Error message:', err.message);
      
      const errorMsg = err.response?.data?.error || err.response?.data?.message || err.message || 'Import failed. Please try again.';
      console.error('DEBUG: Displaying error to user:', errorMsg);
      setError(errorMsg);
      if (err.response?.data) {
        setResult(err.response.data);
      }
    } finally {
      setImporting(false);
    }
  };

  const handleDownloadErrorReport = async () => {
    if (!result || !result.error_report_url) return;

    try {
      const response = await api.get(result.error_report_url, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'import_errors.csv');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Failed to download error report:', err);
    }
  };

  const handleClose = () => {
    setFile(null);
    setError('');
    setResult(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white border border-gray-200 rounded-2xl p-6 max-w-2xl w-full shadow-lg max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-900">Bulk Upload Members</h2>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            disabled={importing}
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>

        {/* Step 1: Download Template */}
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">Step 1: Download Template</h3>
          <button
            onClick={handleDownloadTemplate}
            className="flex items-center gap-2 bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            <ArrowDownTrayIcon className="w-4 h-4" />
            Download Excel Template
          </button>
          <p className="text-xs text-gray-500 mt-2">
            Fill the template with member details before uploading
          </p>
        </div>

        {/* Step 2: Upload File */}
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">Step 2: Upload Excel File</h3>
          <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center hover:border-orange-400 transition-colors">
            <input
              type="file"
              id="file-upload"
              accept=".xlsx,.xls"
              onChange={handleFileSelect}
              disabled={importing}
              className="hidden"
            />
            <label
              htmlFor="file-upload"
              className={`cursor-pointer ${importing ? 'pointer-events-none opacity-50' : ''}`}
            >
              {file ? (
                <div className="flex flex-col items-center">
                  <DocumentIcon className="w-12 h-12 text-green-500 mb-2" />
                  <p className="text-sm font-medium text-gray-900">{file.name}</p>
                  <p className="text-xs text-gray-500">{(file.size / 1024).toFixed(2)} KB</p>
                </div>
              ) : (
                <div className="flex flex-col items-center">
                  <ArrowDownTrayIcon className="w-12 h-12 text-gray-400 mb-2" />
                  <p className="text-sm font-medium text-gray-900">Click to upload or drag and drop</p>
                  <p className="text-xs text-gray-500 mt-1">.xlsx or .xls files only (Max 500 members)</p>
                </div>
              )}
            </label>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-xl p-4">
            <div className="flex items-start gap-3">
              <ExclamationTriangleIcon className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm font-medium text-red-900">Error</p>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Result Display */}
        {result && (
          <div className="mb-6">
            <div className={`border rounded-xl p-4 ${
              result.success_count > 0 ? 'bg-green-50 border-green-200' : 'bg-yellow-50 border-yellow-200'
            }`}>
              <div className="flex items-start gap-3">
                {result.success_count > 0 ? (
                  <CheckCircleIcon className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                ) : (
                  <ExclamationTriangleIcon className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                )}
                <div className="flex-1">
                  <p className="text-sm font-semibold text-gray-900">
                    {result.success_count > 0 ? 'Import Completed' : 'Import Failed'}
                  </p>
                  <div className="mt-2 space-y-1">
                    <p className="text-sm text-gray-700">Total Records: {result.total_records}</p>
                    <p className="text-sm text-green-700">Successfully Imported: {result.success_count}</p>
                    {result.failed_count > 0 && (
                      <p className="text-sm text-red-700">Failed: {result.failed_count}</p>
                    )}
                  </div>
                  
                  {/* Display detailed validation errors */}
                  {result.errors && result.errors.length > 0 && (
                    <div className="mt-4 max-h-48 overflow-y-auto">
                      <p className="text-sm font-semibold text-gray-900 mb-2">Validation Errors:</p>
                      <div className="space-y-2">
                        {result.errors.map((err, idx) => (
                          <div key={idx} className="bg-red-50 border border-red-200 rounded-lg p-2 text-xs">
                            <p className="font-medium text-red-900">Row {err.row}: {err.name || 'Unknown'}</p>
                            <p className="text-red-700">{err.error}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {result.failed_count > 0 && result.error_report_url && (
                    <button
                      onClick={handleDownloadErrorReport}
                      className="mt-3 text-sm text-orange-600 hover:text-orange-700 font-medium"
                    >
                      Download Error Report
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3">
          <button
            onClick={handleImport}
            disabled={!file || importing}
            className="flex-1 bg-orange-500 hover:bg-orange-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white px-6 py-3 rounded-xl font-medium transition-colors flex items-center justify-center gap-2"
          >
            {importing ? (
              <>
                <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Importing...
              </>
            ) : (
              'Import Members'
            )}
          </button>
          <button
            onClick={handleClose}
            disabled={importing}
            className="bg-gray-100 hover:bg-gray-200 disabled:bg-gray-50 disabled:cursor-not-allowed text-gray-700 px-6 py-3 rounded-xl font-medium transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
