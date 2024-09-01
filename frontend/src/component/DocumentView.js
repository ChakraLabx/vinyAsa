import React, { useState } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';
import 'react-pdf/dist/esm/Page/TextLayer.css';

pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

const DocumentView = ({ documentName, fileUrl, fileType }) => {
  const [scale, setScale] = useState(1);
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);

  const handleZoomIn = () => setScale(prevScale => Math.min(prevScale + 0.1, 3));
  const handleZoomOut = () => setScale(prevScale => Math.max(prevScale - 0.1, 0.5));
  const handleResetZoom = () => setScale(1);

  const onDocumentLoadSuccess = ({ numPages }) => {
    setNumPages(numPages);
    setPageNumber(1);
  };

  const changePage = (offset) => {
    setPageNumber(prevPageNumber => Math.min(Math.max(prevPageNumber + offset, 1), numPages));
  };

  const renderDocument = () => {
    if (fileUrl && fileType === 'pdf') {
      return (
        <Document
          file={fileUrl}
          onLoadSuccess={onDocumentLoadSuccess}
          onLoadError={console.error} // Add error handling
        >
          <Page pageNumber={pageNumber} scale={scale} />
        </Document>
      );
    } else if (fileUrl) {
      return <img src={fileUrl} alt="Uploaded Document" style={{ width: '100%' }} />;
    } else {
      return <img src={"sample_images/3M_INDIA_LTD-523395-MARCH-2023_3.pdf_1.jpg"} alt="Uploaded Document" style={{ width: '100%' }} />;
    }
  };

  return (
    <>
      <div id="document-name-controls">
        <div className="h5" id="document-name">{documentName}</div>
        {fileType === 'pdf' && (
          <div id="pagination">
            <button onClick={() => changePage(-1)} disabled={pageNumber <= 1}>
              <span aria-hidden="true">&laquo;</span>
            </button>
            <span>{pageNumber} / {numPages}</span>
            <button onClick={() => changePage(1)} disabled={pageNumber >= numPages}>
              <span aria-hidden="true">&raquo;</span>
            </button>
          </div>
        )}
        <div id="zoom-controls">
          <button onClick={handleZoomIn} disabled={scale >= 3}>+</button>
          <button onClick={handleZoomOut} disabled={scale <= 0.5}>-</button>
          <button onClick={handleResetZoom} disabled={scale === 1}>↺</button>
        </div>
      </div>
      <div id="document-container">
        <div id="document-view">
          {renderDocument()}
        </div>
      </div>
    </>
  );
};

export default DocumentView;
