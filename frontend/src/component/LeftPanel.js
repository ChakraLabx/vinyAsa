import React, { useState } from 'react';
import axios from 'axios';
import DocumentView from './DocumentView';
import DocumentControls from './DocumentControls';

function LeftPanel({ setRawText, setLayoutData }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [documentName, setDocumentName] = useState("Receipts");
  const [fileUrl, setFileUrl] = useState('');
  const [fileType, setFileType] = useState('pdf');

  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      const url = URL.createObjectURL(file);
      setFileUrl(url);
      setFileType(file.type.includes('pdf') ? 'pdf' : 'image');
      setDocumentName(file.name);

      // Process the file
      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await axios.post('/api/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        setRawText(response.data.rawText);
        setLayoutData(response.data.layoutData);
      } catch (error) {
        console.error('Error processing file:', error);
      }
    }
  };

  const handleDocumentChange = (event) => {
    setDocumentName(event.target.value);
    setSelectedFile(null);
    setFileUrl('');
    setFileType('pdf');
    // You might want to load sample data here
  };

  return (
    <div id="left-panel" className="flex-grow-1 p-3 border-end">
      <DocumentView documentName={documentName} fileUrl={fileUrl} fileType={fileType} />
      <DocumentControls
        documentName={documentName}
        handleDocumentChange={handleDocumentChange}
        selectedFile={selectedFile}
        handleFileChange={handleFileChange}
      />
    </div>
  );
}

export default LeftPanel;