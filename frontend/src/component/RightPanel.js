import React, { useState, useEffect } from 'react';
import TabContent from './TabContent';

function RightPanel({ activeTab, setActiveTab, processedData, currentPage }) {
  const [currentPageData, setCurrentPageData] = useState(null);

  const tabs = [
    'Raw-text', 'Layout', 'Forms', 'Tables', 'Queries', 'Signatures'
  ];

  useEffect(() => {
    if (processedData[activeTab]) {
      if (activeTab === 'Raw-text') {
        setCurrentPageData(processedData[activeTab][currentPage] || []);
      } else if (activeTab === 'Layout') {
        setCurrentPageData(processedData[activeTab].filter(item => item.page_no === currentPage));
      } else {
        setCurrentPageData(processedData[activeTab]);
      }
    } else {
      setCurrentPageData(null); 
    }
  }, [activeTab, processedData, currentPage]);

  const getCurrentTabContent = () => {
    if (!currentPageData) {
      return "No data available";
    }
    return JSON.stringify(currentPageData, null, 2);
  };

  return (
    <div id="right-panel" className="flex-grow-1 p-3">
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