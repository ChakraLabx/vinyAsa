import React from 'react';

function TabContent({ id, active, content }) {
  return (
    <div id={id} className={`tab-pane ${active ? 'active' : ''}`}>
      <pre>{content}</pre>
    </div>
  );
}

export default TabContent;