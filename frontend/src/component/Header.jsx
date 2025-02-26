import React from 'react';

function Header({ processedData, resetAllData }) {
  const handleDownload = () => {
    if (!processedData) {
      alert('No data available to download');
      return;
    }

    const jsonData = JSON.stringify(processedData, null, 2);
    const blob = new Blob([jsonData], { type: 'application/json' });
    
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'processed_data.json';
    
    document.body.appendChild(link);
    link.click();

    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <header className="navbar navbar-light bg-light border-bottom">
      <div className="container-fluid">
        {/* <button 
          className="navbar-toggler border-0" 
          type="button" 
          data-bs-toggle="collapse" 
          data-bs-target="#navbarNav"
        >
          <span className="navbar-toggler-icon"></span>
        </button> */}
        <div className="d-flex align-items-center">
          <img
            src="favicon_io/apple-touch-icon.png"
            alt="Logo"
            style={{ height: '40px', marginRight: '10px' }}
          />
          <h1 className="h1 m-0">vinyAsa</h1>
        </div>
        <div className="ms-auto">
          <button 
            className="btn btn-secondary me-2" 
            onClick={handleDownload}
          >
            Download results
          </button>
          <button 
            className="btn btn-secondary" 
            onClick={resetAllData}
          >
            Reset demo
          </button>
        </div>
      </div>
    </header>
  );
}

export default Header;