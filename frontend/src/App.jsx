import React, { useState } from 'react';
import axios from 'axios';
import Header from './component/Header';
import LeftPanel from './component/LeftPanel';
import RightPanel from './component/RightPanel';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [activeTab, setActiveTab] = useState('Raw-text');
  const [processedData, setProcessedData] = useState({
    'Raw-text': null,
    'Layout': null,
    'Forms': null,
    'Tables': null,
    'Queries': null,
    'Signatures': null
  });
  const [labeledImages, setLabeledImages] = useState({
    'Raw-text': [],
    'Layout': [],
    'Forms': [],
    'Tables': [],
    'Queries': [],
    'Signatures': []
  });
  const [processing, setProcessing] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [highlightedText, setHighlightedText] = useState(null);

  const resetAllData = () => {
    setProcessedData({
      'Raw-text': null,
      'Layout': null,
      'Forms': null,
      'Tables': null,
      'Queries': null,
      'Signatures': null
    });
    setLabeledImages({
      'Raw-text': [],
      'Layout': [],
      'Forms': [],
      'Tables': [],
      'Queries': [],
      'Signatures': []
    });
    setCurrentPage(1);
  };

  const processFile = async (file, tab) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('tab', tab);
    setProcessing(true);
    try {
      const response = await axios.post('http://127.0.0.1:5000/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      if (tab === 'Raw-text') {
        setProcessedData(prevData => ({
          ...prevData,
          [tab]: response.data.rawText
        }));
      } else if (tab === 'Layout') {
        setProcessedData(prevData => ({
          ...prevData,
          [tab]: response.data.layoutData
        }));
      }
      setLabeledImages(prevImages => ({
        ...prevImages,
        [tab]: response.data.labeledImages || []
      }));
    } catch (error) {
      console.error(`Error processing file:`, error);
    } finally {
      setProcessing(false);
    }
  };

  const handleFileChange = (file) => {
    if (file) {
      setSelectedFile(file);
      resetAllData();
      setActiveTab("Raw-text");
      processFile(file, 'Raw-text');
    }
  };

  const handleTabChange = (newTab) => {
    setActiveTab(newTab);
    if (selectedFile && !processedData[newTab]) {
      processFile(selectedFile, newTab);
    }
  };

  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
  };

  const handleTextHighlight = (textData) => {
    setHighlightedText(textData);
  };

  return (
    <div className="d-flex flex-column vh-100">
      <Header />
      <main className="flex-grow-1 d-flex">
        <LeftPanel
          setSelectedFile={setSelectedFile}
          setActiveTab={setActiveTab}
          processFile={processFile}
          labeledImages={labeledImages[activeTab]}
          processing={processing}
          handleFileChange={handleFileChange}
          currentPage={currentPage}
          onPageChange={handlePageChange}
          highlightedText={highlightedText}
        />
        <RightPanel
          activeTab={activeTab}
          setActiveTab={handleTabChange}
          processedData={processedData}
          currentPage={currentPage}
          onTextHighlight={handleTextHighlight}
        />
      </main>
    </div>
  );
}

export default App;