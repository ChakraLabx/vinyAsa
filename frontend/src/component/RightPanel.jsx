import React, { useState, useEffect } from 'react';
import TabContent from './TabContent';
import ModelToggleButton from './ModelToggleButton';

function RightPanel({ activeTab, setActiveTab, processedData, currentPage, onTextHighlight }) {
  const [currentPageData, setCurrentPageData] = useState(null);
  const [selectedTextData, setSelectedTextData] = useState(null);
  const [mode, setMode] = useState(0);

  const tabs = [
    'Raw-text', 'Layout', 'Forms', 'Tables', 'Queries', 'Signatures'
  ];  

 
  useEffect(() => {
    if (processedData[activeTab]) {
      if (activeTab === 'Raw-text') {
        // Extract text data with coordinates
        setCurrentPageData(
          processedData[activeTab][currentPage]?.at(0).map((data) => ({
            text: data.text,
            x0: data.x0,
            x1: data.x1,
            top: data.top,
            bottom: data.bottom
          }))
        );
      } else if (activeTab === 'Layout') {
        setCurrentPageData(
          processedData[activeTab].filter(item => item.page_no === currentPage)
        );
      } else {
        setCurrentPageData(processedData[activeTab]);
      }
    } else {
      setCurrentPageData(null);
    }
  }, [activeTab, processedData, currentPage]);

  const handleTextClick = (textData) => {
    setSelectedTextData(textData);
    onTextHighlight && onTextHighlight(textData);
  };

  const getCurrentTabContent = () => {
    if (!currentPageData) {
      return "No data available";
    }
  
    if (activeTab === 'Raw-text' && Array.isArray(currentPageData)) {
      return (
        <div className="button-container">
          {currentPageData.map((data, ind) => (
            <button
              key={ind}
              onClick={() => handleTextClick(data)}
              className={`btn btn-light ${selectedTextData === data ? 'selected' : ''}`}
              
            
            >
              {data.text}
            </button>
          ))}
        </div>
      );
    }    
    
    return <pre>{JSON.stringify(currentPageData, null, 2)}</pre>;
  };

  const handleModeChange = (newMode) => {
    setMode(newMode);
    // You can add logic here to change theme, apply styles, etc. based on the mode
  };


  return (
    <div id="right-panel" className="flex-grow-1 p-3">
      <div className="togglebutton">
        <ModelToggleButton 
          mode={mode} 
          onModeChange={handleModeChange} 
        />
      </div>
      <ul className="nav nav-tabs mb-3">
        {tabs.map(tab => (
          <li className="nav-item" key={tab}>
            <a
              className={`nav-link ${activeTab === tab ? 'active' : ''}`}
              href={`#${tab}`}
              onClick={(e) => {
                e.preventDefault();
                setActiveTab(tab);
              }}
            >
              {tab.replace('-', ' ')}
            </a>
          </li>
        ))}
      </ul>
      <div className="tab-content">
        <TabContent
          id={activeTab}
          active={true}
          content={<pre>{getCurrentTabContent()}</pre>}
        />
      </div>
    </div>
  );
}

export default RightPanel;