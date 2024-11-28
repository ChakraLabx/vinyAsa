import React, { useState, useRef, useEffect } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';
import 'react-pdf/dist/esm/Page/TextLayer.css';

pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

const DocumentView = ({ 
  documentName, 
  fileUrl, 
  fileType, 
  resetZoom, 
  labeledImages, 
  processing,
  currentPage,
  onPageChange,
  newFileUploaded,
  highlightedText
}) => {
  const [scale, setScale] = useState(1);
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [pageWidth, setPageWidth] = useState(null);
  const containerRef = useRef(null);
  const contentRef = useRef(null);

  const handleZoomIn = () => setScale(prevScale => Math.min(prevScale + 0.1, 3));
  const handleZoomOut = () => setScale(prevScale => Math.max(prevScale - 0.1, 0.5));
  const handleResetZoom = () => setScale(1);

  useEffect(() => {
    resetZoom(handleResetZoom);
  }, [resetZoom]);

  useEffect(() => {
    if (newFileUploaded) {
      setNumPages(null);
      setPageNumber(1);
      onPageChange(1);
    }
  }, [newFileUploaded, onPageChange]);

  const onDocumentLoadSuccess = ({ numPages }) => {
    setNumPages(numPages);
    setPageNumber(1);
    onPageChange(1);
  };

  const changePage = (offset) => {
    const newPage = Math.min(Math.max(pageNumber + offset, 1), numPages || (labeledImages && labeledImages.length) || 1);
    setPageNumber(newPage);
    onPageChange(newPage);
  };

  useEffect(() => {
    const updatePageWidth = () => {
      if (containerRef.current) {
        const containerWidth = containerRef.current.clientWidth;
        setPageWidth(containerWidth);
      }
    };

    updatePageWidth();
    window.addEventListener('resize', updatePageWidth);

    return () => window.removeEventListener('resize', updatePageWidth);
  }, []);

  useEffect(() => {
    if (containerRef.current && contentRef.current) {
      const container = containerRef.current;
      const content = contentRef.current;

      const scrollLeft = (content.scrollWidth * scale - container.clientWidth) / 2;
      const scrollTop = (content.scrollHeight * scale - container.clientHeight) / 2;

      container.scrollLeft = scrollLeft;
      container.scrollTop = scrollTop;
    }
  }, [scale]);

  useEffect(() => {
    setPageNumber(currentPage);
  }, [currentPage]);

  const renderDocument = () => {
    if (processing) {
      return renderOriginalDocument();
    }

    if (labeledImages && labeledImages.length > 0) {
      return (
        <div style={{ position: 'relative' }}>
        <img
          src={`data:image/jpeg;base64,${labeledImages[pageNumber - 1]}`}
          alt={`Labeled ${pageNumber}`}
          style={{maxWidth: '100%', height: '100%'}}
          ref={(img) => {
            if (img) {
              img.onload = () => {
                const naturalWidth = img.naturalWidth;
                const naturalHeight = img.naturalHeight;

                // Get the displayed image dimensions
                const { width: displayedWidth, height: displayedHeight } = img.getBoundingClientRect();

                // Calculate scaling factors
                const widthScaleFactor = displayedWidth / naturalWidth;
                const heightScaleFactor = displayedHeight / naturalHeight;

                if (highlightedText) {
                  const highlightBox = document.createElement('div');
                  highlightBox.style.position = 'absolute';
                  highlightBox.style.border = '2px solid red';

                  // Calculate position and size using natural image coordinates and display scaling
                  highlightBox.style.left = `${(highlightedText.x0 * widthScaleFactor / displayedWidth) * 100}%`;
                  highlightBox.style.top = `${(highlightedText.top * heightScaleFactor / displayedHeight) * 100}%`;
                  highlightBox.style.width = `${((highlightedText.x1 - highlightedText.x0) * widthScaleFactor / displayedWidth) * 100}%`;
                  highlightBox.style.height = `${((highlightedText.bottom - highlightedText.top) * heightScaleFactor / displayedHeight) * 100}%`;

                  highlightBox.style.pointerEvents = 'none';
                  highlightBox.style.zIndex = '10';
                  highlightBox.style.backgroundColor = 'rgba(255, 0, 0, 0.2)';

                  const existingHighlight = img.parentNode.querySelector('.text-highlight');
                  if (existingHighlight) {
                    existingHighlight.remove();
                  }

                  highlightBox.classList.add('text-highlight');
                  img.parentNode.appendChild(highlightBox);
                }
              };

              // Trigger onload if image is already loaded
              if (img.complete) {
                img.onload();
              }
            }
          }}
        />
   </div>
      );
    }

    return renderOriginalDocument();
  };

  const renderOriginalDocument = () => {
    if (fileUrl && fileType === 'pdf') {
      return (
        <Document
          file={fileUrl}
          onLoadSuccess={onDocumentLoadSuccess}
          onLoadError={console.error}
        >
          <Page
            pageNumber={pageNumber}
            width={pageWidth}
          />
        </Document>
      );
    } else if (fileUrl) {
      return <img src={fileUrl} alt="Uploaded Document" style={{ maxWidth: '100%', height: 'auto' }} />;
    } else {
      return <div>No document selected</div>;
    }
  };

  return (
    <>
      <div id="document-name-controls">
        <div className="h5" id="document-name">{documentName}</div>
        <div id="pagination">
          <button onClick={() => changePage(-1)} disabled={pageNumber <= 1}>
            <span aria-hidden="true">&laquo;</span>
          </button>
          <span>{pageNumber} / {numPages || (labeledImages && labeledImages.length) || 1}</span>
          <button onClick={() => changePage(1)} disabled={pageNumber >= (numPages || (labeledImages && labeledImages.length) || 1)}>
            <span aria-hidden="true">&raquo;</span>
          </button>
        </div>
        <div id="zoom-controls">
          <button onClick={handleZoomIn} disabled={scale >= 3}>+</button>
          <button onClick={handleZoomOut} disabled={scale <= 0.5}>-</button>
          <button onClick={handleResetZoom} disabled={scale === 1}>↺</button>
        </div>
      </div>
      <div id="document-container" ref={containerRef}>
        <div id="document-view" ref={contentRef} style={{ transform: `scale(${scale})` }}>
          {renderDocument()}
        </div>
      </div>
    </>
  );
};

export default DocumentView;