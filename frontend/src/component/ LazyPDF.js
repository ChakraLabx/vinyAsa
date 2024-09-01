// LazyPDF.js
import React from 'react';
import { Document, Page } from 'react-pdf';

const LazyPDF = ({ fileUrl, pageNumber, scale, onLoadSuccess, onLoadError }) => (
  <Document
    file={fileUrl}
    onLoadSuccess={onLoadSuccess}
    onLoadError={onLoadError}
  >
    <Page pageNumber={pageNumber} scale={scale} />
  </Document>
);

export default LazyPDF;