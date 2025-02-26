import React, { useState, useMemo } from 'react';
import axios from 'axios';
import Header from './component/Header';
import LeftPanel from './component/LeftPanel';
import RightPanel from './component/RightPanel';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [activeTab, setActiveTab] = useState('Raw-text');
  const [modelName, setModelName] = useState("");
  const [message, setMessage] = useState("");
  const [processing, setProcessing] = useState(false);
  const [currentPage, setCurrentPage] = useState(0);
  const [highlightedText, setHighlightedText] = useState(null);

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

  const modelConfigByTab = useMemo(() => ({
    'Raw-text': [
      { num: 0, value: "RAGFLOW" },   
      { num: 1, value: "TESSERACT" }, 
      { num: 2, value: "PADDLE" },   
      { num: 3, value: "SURYA" },
      { num: 4, value: "EASY" },
      { num: 5, value: "RAPID" },
      { num: 6, value: "MM" },
    ],
    'Layout': [
      { num: 0, value: "RAGFLOW" },
      { num: 1, value: "SURYA" },
      { num: 2, value: "VINY"}
    ],
    'Queries': [
      { num: 0, value: "RAGFLOW" },
      { num: 1, value: "SURYA" }
    ],
    'Forms': [
      { num: 0, value: "VINY" },
    ],
    'Tables': [
      { num: 0, value: "RAGFLOW" },
      { num: 1, value: "SURYA" }
    ],
    'Signatures': [
      { num: 0, value: "VINY" }
    ]
  }), []);
  const currentModes = modelConfigByTab[activeTab];
  const [mode, setMode] = useState(currentModes[0]);

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
  };

  const processFile = async (file, tab, forceReprocess = false, model) => {
    if (tab === 'Queries' && (!message || !message.trim())) {
      console.warn('No query message provided. Skipping backend call for Queries tab.');
      return;
    }
  
    const formData = new FormData();
    formData.append('file', file);
    formData.append('tab', tab);
    formData.append('model_name', model || modelName);
    if (tab === 'Queries') {
      formData.append('query', message);
    }
    
    setProcessing(true);
    try {
      const response = await axios.post('http://127.0.0.1:7001/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      console.log(response.data);
  
      const processedResponse =
        tab === 'Raw-text'
          ? response.data.rawText
          : tab === 'Layout'
          ? response.data.layoutData
          : tab === 'Forms'
          ? response.data.formData
          : tab === 'Tables'
          ? response.data.tableHtml
          : tab === 'Queries'
          ? response.data.ragResponse
          : tab === 'Signatures'
          ? response.data.signature
          : response.data;
  
      setProcessedData(prevData => ({
        ...prevData,
        [tab]: {
          data: processedResponse,
          model: model || modelName,
        },
      }));
  
      if (response.data.labeledImages) {
        setLabeledImages(prevImages => ({
          ...prevImages,
          [tab]: response.data.labeledImages || [],
        }));
      }
    } catch (error) {
      console.error('Error processing file:', error);
    } finally {
      setProcessing(false);
    }
  };
  
  
  const handleModelChange = (newMode) => {
    if (newMode !== modelName) {
      setModelName(newMode);
      const currentTabData = processedData[activeTab];
      if (currentTabData?.model === newMode) {
        return;
      }
  
      if (selectedFile) {
        processFile(selectedFile, activeTab, false, newMode);
      }
    }
  };

  const handleFileChange = (file) => {
    if (file) {
      setSelectedFile(file);
      resetAllData();
      const newTab = 'Raw-text'
      const newModes = modelConfigByTab[newTab];
      const defaultMode = newModes[0]; 
      setModelName(defaultMode.value);
      setActiveTab(newTab);
      setMode(defaultMode);
      processFile(file, newTab, false, defaultMode.value);
    }
  };

  const handleTabChange = (newTab) => {
    const newModes = modelConfigByTab[newTab];
    const defaultMode = newModes[0]; 
    setModelName(defaultMode.value);
    setActiveTab(newTab);
    setMode(defaultMode);
    if (selectedFile && !processedData[newTab]) {
      processFile(selectedFile, newTab, false, defaultMode.value);
    }
  };

  const handleQuerySubmit = () => {
    if (selectedFile && message.trim()) {
      processFile(selectedFile, 'Queries', false, modelName);
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
      <Header processedData={processedData[activeTab]} resetAllData={resetAllData}/>
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
          setHighlightedText={setHighlightedText}
          activeTab={activeTab}
        />
        <RightPanel
          activeTab={activeTab}
          setActiveTab={handleTabChange}
          modelName={modelName}
          modelChange={handleModelChange}
          processedData={processedData}
          currentPage={currentPage}
          onTextHighlight={handleTextHighlight}
          processing={processing}
          message={message}
          setMessage={setMessage}
          onQuerySubmit={handleQuerySubmit}
          modelConfigByTab={modelConfigByTab}
          mode={mode}
          setMode={setMode}
        />
      </main>
    </div>
  );
}

export default App;