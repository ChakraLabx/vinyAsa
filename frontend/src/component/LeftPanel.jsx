import React, { useState, useCallback, useEffect } from 'react';
import DocumentView from './DocumentView';
import DocumentControls from './DocumentControls';

function LeftPanel({ setSelectedFile, labeledImages, processing, handleFileChange, currentPage, onPageChange, highlightedText }) {
  const [documentName, setDocumentName] = useState("Receipts");
  const [fileUrl, setFileUrl] = useState('');
  const [fileType, setFileType] = useState('pdf');
  const [resetZoomFunction, setResetZoomFunction] = useState(() => {});
  const [newFileUploaded, setNewFileUploaded] = useState(false);

  const sampleDocuments = {
    'Receipts': { url: 'data/pdfs/ASAD013-LOAD.pdf', type: 'pdf' },
    'Form': { url: 'data/chitra/09-7012530-003.jpg', type: 'image' },
    'Security and Exchange Commission Filing': { url: 'data/pdfs/10-Q-Q3-2024-As-Filed.pdf', type: 'pdf' },
    'Filing': { url: 'data/pdfs/10-Q-Q3-2024-As-Filed.pdf', type: 'pdf' },
    'Vaccination Card': { url: 'data/pdfs/certificate.pdf', type: 'pdf' }
  };

  const handleFileInputChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      const url = URL.createObjectURL(file);
      setFileUrl(url);
      setFileType(file.type.includes('pdf') ? 'pdf' : 'image');
      setDocumentName(file.name);
      resetZoomFunction();
      handleFileChange(file);
      setNewFileUploaded(true);
    }
  };

  const handleDocumentChange = (event) => {
    const selectedDoc = event.target.value;
    setDocumentName(selectedDoc);
    setSelectedFile(null);
    setFileUrl(sampleDocuments[selectedDoc].url);
    setFileType(sampleDocuments[selectedDoc].type);
    resetZoomFunction();
    setNewFileUploaded(true);
  };

  const resetZoom = useCallback((resetFunction) => {
    setResetZoomFunction(() => resetFunction);
  }, []);

  useEffect(() => {
    if (newFileUploaded) {
      setNewFileUploaded(false);
    }
  }, [newFileUploaded]);

  return (
    <div id="left-panel" className="flex-grow-1 p-3 border-end">
      <DocumentView
        documentName={documentName}
        fileUrl={fileUrl || sampleDocuments[documentName].url}
        fileType={fileType || sampleDocuments[documentName].type}
        resetZoom={resetZoom}
        labeledImages={labeledImages}
        processing={processing}
        currentPage={currentPage}
        onPageChange={onPageChange}
        newFileUploaded={newFileUploaded}
        highlightedText={highlightedText}
      />
      <DocumentControls
        documentName={documentName}
        handleDocumentChange={handleDocumentChange}
        handleFileChange={handleFileInputChange}
        sampleDocuments={Object.keys(sampleDocuments)}
      />
    </div>
  );
}

export default LeftPanel;