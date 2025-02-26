import React, { useState, useCallback, useEffect } from 'react';
import DocumentView from './DocumentView';
import DocumentControls from './DocumentControls';
import Box from '@mui/material/Box'; 

        
function LeftPanel({ setSelectedFile, labeledImages, processing, handleFileChange, currentPage, onPageChange, highlightedText, activeTab, setHighlightedText}) {
  // Defining sx styles inline
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

  const sampleDocuments = {
    'Receipts': { url: 'data/ASAD013-LOAD.pdf', type: 'pdf', name: 'ASAD013-LOAD.pdf' },
    'Form': { url: 'data/12572049.pdf', type: 'pdf', name: '12572049.pdf' },
    'Security and Exchange Commission Filing': { url: 'data/10-Q-Q3-2024-As-Filed.pdf', type: 'pdf', name: '10-Q-Q3-2024-As-Filed.pdf' },
    'Filing': { url: 'data/CKYC form.pdf', type: 'pdf', name: 'CKYC form.pdf' },
    'Vaccination Card': { url: 'data/certificate.pdf', type: 'pdf', name: 'certificate.pdf' },
  };
  
  const handleFileInputChange = useCallback((event) => {
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
  }, [handleFileChange, resetZoomFunction]);

  const handleDocumentChange = async (event) => {
    const selectedDoc = event.target.value;
    setDocumentName(selectedDoc);
    
    // Get the document info from sampleDocuments
    const doc = sampleDocuments[selectedDoc];
    setFileUrl(doc.url);
    setFileType(doc.type);
    resetZoomFunction();
    setNewFileUploaded(true);
  
    try {
      const response = await fetch(doc.url);
      const blob = await response.blob();
      const filename = doc.name || doc.url;
      const ext = filename.split('.').pop().toLowerCase();
      let mimeType;
      if (ext === 'pdf') {
        mimeType = 'application/pdf';
      } else if (ext === 'png') {
        mimeType = 'image/png';
      } else if (ext === 'jpg' || ext === 'jpeg') {
        mimeType = 'image/jpeg';
      } else {
        mimeType = blob.type;
      }
      
      const file = new File([blob], filename, { type: mimeType });
 
      setSelectedFile(file);
      handleFileChange(file);
    } catch (error) {
      console.error("Error fetching sample document:", error);
    }
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
    <Box 
      id="left-panel" 
      sx={sx.leftPanel}
    >
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