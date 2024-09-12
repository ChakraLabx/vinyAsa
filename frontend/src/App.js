import React, { useState } from 'react';
import Header from './component/Header';
import LeftPanel from './component/LeftPanel';
import RightPanel from './component/RightPanel';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css'

function App() {
  const [rawText, setRawText] = useState('');
  const [layoutData, setLayoutData] = useState({});
  const [activeTab, setActiveTab] = useState('Raw-text');

  return (
    <div className="d-flex flex-column vh-100">
      <Header />
      <main className="flex-grow-1 d-flex">
        <LeftPanel 
          setRawText={setRawText} 
          setLayoutData={setLayoutData} 
          setActiveTab={setActiveTab}
        />
        <RightPanel 
        rawText={rawText} 
        layoutData={layoutData} 
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        />
      </main>
    </div>
  );
}

export default App;