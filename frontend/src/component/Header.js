import React from 'react';

function Header() {
  return (
    <header className="navbar navbar-light bg-light border-bottom">
      <div className="container-fluid">
        <button className="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span className="navbar-toggler-icon"></span>
        </button>
        <h1 className="h1">vinyAsa</h1>
        <div className="ms-auto">
          <button className="btn btn-secondary me-2" id="download-results">Download results</button>
          <button className="btn btn-secondary" id="reset-demo">Reset demo</button>
        </div>
      </div>
    </header>
  );
}

export default Header;