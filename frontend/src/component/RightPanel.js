import React from 'react';
import TabContent from './TabContent';

function RightPanel({ rawText, layoutData, activeTab, setActiveTab }) {
  const tabs = [
    'Raw-text', 'Layout', 'Forms', 'Tables', 'Queries', 'Signatures'
  ];

  return (
    <div id="right-panel" className="flex-grow-1 p-3">
      <ul className="nav nav-tabs mb-3">
        {tabs.map(tab => (
          <li className="nav-item" key={tab}>
            <a
              className={`nav-link ${activeTab === tab ? 'active' : ''}`}
              href={`#${tab}`}
              onClick={() => setActiveTab(tab)}
            >
              {tab.replace('-', ' ')}
            </a>
          </li>
        ))}
      </ul>
      <div className="tab-content">
        <TabContent id="Raw-text" active={activeTab === 'Raw-text'} content={JSON.stringify(rawText, null, 2)} />
        <TabContent id="Layout" active={activeTab === 'Layout'} content={JSON.stringify(layoutData, null, 2)} />
        {tabs.slice(2).map(tab => (
          <TabContent key={tab} id={tab} active={activeTab === tab} content={`${tab} content will be displayed here.`} />
        ))}
      </div>
    </div>
  );
}

export default RightPanel;