import React, { useState, useCallback, useEffect } from 'react';
import DocumentView from './DocumentView';
import DocumentControls from './DocumentControls';
import Box from '@mui/material/Box';

function LeftPanel({
  activeTab,
  processFile,
  processing,
  currentPage,
  onPageChange,
  highlightedText,
  setHighlightedText,
  resetAllData,
  setActiveTab
}) {
  const sx = {
    leftPanel: {
      flexGrow: 1,
      padding: '1rem',
      borderRight: '1px solid #dee2e6',
      minWidth: '50%', 
      overflowY: 'auto', 
      height: 'calc(100vh - 80px)',
      '@media (max-width: 768px)': {
        display: 'none',
      },
    }
  };

  const [documentName, setDocumentName] = useState("Receipts");
  const [fileUrl, setFileUrl] = useState('');
  const [fileType, setFileType] = useState('pdf');
  const [resetZoomFunction, setResetZoomFunction] = useState(() => {});
  const [newFileUploaded, setNewFileUploaded] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [labeledImages, setLabeledImages] = useState({
    'Raw-text': [],
    'Layout': [],
    'Forms': [],
    'Tables': [],
    'Queries': [],
    'Signatures': []
  });

  const sampleDocuments = {
    // ... (keep sampleDocuments same as before)
  };

  const handleFileInputChange = async (event) => {
    const file = event.target.files[0];
    if (file) {
      const url = URL.createObjectURL(file);
      setFileUrl(url);
      setFileType(file.type.includes('pdf') ? 'pdf' : 'image');
      setDocumentName(file.name);
      resetZoomFunction();
      setSelectedFile(file);
      resetAllData();
      setActiveTab("Raw-text");
      const images = await processFile(file, 'Raw-text');
      setLabeledImages(prev => ({ ...prev, 'Raw-text': images }));
      setNewFileUploaded(true);
    }
  };

  const handleDocumentChange = async (event) => {
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
    <Box id="left-panel" sx={sx.leftPanel}>
      <DocumentView
        documentName={documentName}
        fileUrl={fileUrl || sampleDocuments[documentName].url}
        fileType={fileType || sampleDocuments[documentName].type}
        resetZoom={resetZoom}
        labeledImages={labeledImages[activeTab]}
        processing={processing}
        currentPage={currentPage}
        onPageChange={onPageChange}
        newFileUploaded={newFileUploaded}
        highlightedText={highlightedText}
        setHighlightedText={setHighlightedText}
        activeTab={activeTab}
      />
      <DocumentControls
        documentName={documentName}
        handleDocumentChange={handleDocumentChange}
        handleFileChange={handleFileInputChange}
        sampleDocuments={Object.keys(sampleDocuments)}
      />
    </Box>
  );
}

export default LeftPanel;