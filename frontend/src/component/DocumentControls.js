import axios from 'axios';
import React from 'react';

function DocumentControls({ handleFileChange, handleDocumentChange, documentName, selectedFile }) {
  const sampleDocuments = [
    'Receipts',
    'Form',
    'Security and Exchange Commission Filing',
    'Filing',
    'Vaccination Card'
  ];

  const UploadDoc = async () => {
     axios.post("/route",{
      data:""
     }).then((res) => {

     }).catch((err)=> {
      
     })
  }

  return (
    <div id="document-controls">
      <div className="doc-left-section">
        <label htmlFor="sample-selector" className="form-label">Choose a sample document:</label>
        <select
          className="form-control"
          id="sample-selector"
          value={documentName}
          onChange={handleDocumentChange}
        >
          {sampleDocuments.map(doc => (
            <option key={doc} value={doc}>{doc}</option>
          ))}
        </select>
      </div>
      <div className="doc-right-section">
        <div className="upload-section">
          <h3>Upload document</h3>
          <form id="upload-form" encType="multipart/form-data">
            <label htmlFor="file-upload" className="single-file-upload">
              Choose document
            </label>
            <input
              type="file"
              id="file-upload"
              name="file"
              accept="image/jpeg,image/png,application/pdf"
              onChange={handleFileChange}
            />
            <span id="file-name">{selectedFile ? selectedFile.name : ''}</span>
            <p className="upload-info">Documents must be fewer than 11 pages, smaller than 5 MB, and one of the following formats: JPEG, PNG, or PDF.</p>
          </form>
        </div>
      </div>
    </div>
  );
}

export default DocumentControls;