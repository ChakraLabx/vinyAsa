import React from 'react';
import { Box, Typography, Select, MenuItem, Input, FormLabel, FormControl } from '@mui/material';

function DocumentControls({ handleFileChange, handleDocumentChange, documentName, selectedFile, sampleDocuments }) {
  return (
    <Box 
      id="document-controls"
      sx={{
        display: 'flex',
        justifyContent: 'space-between',
        marginTop: '20px'
      }}
    >
      <Box 
        className="doc-left-section"
        sx={{
          width: '40%'
        }}
      >
        <FormControl fullWidth>
          <FormLabel 
            sx={{
              display: 'block',
              marginBottom: '5px'
            }}
          >
            Choose a sample document:
          </FormLabel>
          <Select
            fullWidth
            value={documentName}
            onChange={handleDocumentChange}
            sx={{
              border: '1px solid #ccc',
              borderRadius: '4px'
            }}
          >
            {sampleDocuments.map(doc => (
              <MenuItem key={doc} value={doc}>
                {doc}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>
      
      <Box 
        className="doc-right-section"
        sx={{
          width: '55%',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        <Box className="upload-section">
          <Typography variant="h3" sx={{ fontSize: '1.25rem', marginBottom: '10px' }}>
            Upload document
          </Typography>
          
          <Box component="form" id="upload-form" sx={{ display: 'flex', flexDirection: 'column' }}>
            <Box 
              sx={{
                position: 'relative',
                marginBottom: '10px'
              }}
            >
              <Input
                type="file"
                id="file-upload"
                name="file"
                accept="image/jpeg,image/png,application/pdf"
                onChange={handleFileChange}
                sx={{ display: 'none' }}
              />
              <label htmlFor="file-upload">
                <Box 
                  component="span"
                  sx={{
                    display: 'inline-block',
                    padding: '8px 12px',
                    cursor: 'pointer',
                    backgroundColor: '#f0ad4e',
                    color: 'white',
                    borderRadius: '4px'
                  }}
                >
                  Choose document
                </Box>
              </label>
              
              <Typography 
                variant="body2" 
                sx={{ 
                  marginLeft: '10px', 
                  display: 'inline-block' 
                }}
              >
                {selectedFile ? selectedFile.name : ''}
              </Typography>
            </Box>
            
            <Typography 
              variant="body2" 
              sx={{
                fontSize: '0.8em',
                color: '#666',
                marginTop: '5px'
              }}
            >
              Documents must be fewer than 11 pages, smaller than 5 MB, and one of the following formats: JPEG, PNG, or PDF.
            </Typography>
          </Box>
        </Box>
      </Box>
    </Box>
  );
}

export default DocumentControls;