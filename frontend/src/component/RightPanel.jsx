import React, { useState, useEffect } from 'react';
import { Box, Button, Typography, CircularProgress } from '@mui/material';
import TabContent from './TabContent';
import ModelToggleButton from './ModelToggleButton';

function RightPanel({ activeTab, setActiveTab, modelName, modelChange, processedData, currentPage, onTextHighlight, processing, message, setMessage, onQuerySubmit, modelConfigByTab, mode, setMode }) {
  const sx = {
    rightPanel: {
      flexGrow: 1,
      padding: '1rem',
      minWidth: '50%',
      overflowY: 'auto',
      height: 'calc(100vh - 80px)',
      '@media (max-width: 768px)': {
        display: 'none',
      },
    },
    loader: {
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100%',
      flexDirection: 'column',
      gap: '1rem'
    },
    queryInput: {
      width: '100%',
      padding: '10px 15px',
      border: '1px solid #ddd',
      borderRadius: '4px',
      fontSize: '14px',
      '&:focus': {
        outline: 'none',
        borderColor: '#0073bb'
      }
    },
    queryContainer: {
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      gap: '20px'
    },
    messageContainer: {
      flex: 1,
      overflowY: 'auto',
      padding: '20px',
      backgroundColor: '#f8f9fa',
      borderRadius: '8px'
    }
  };

  function GradientCircularProgress() {
    return (
      <React.Fragment>
        <svg width={0} height={0}>
          <defs>
            <linearGradient id="my_gradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#e01cd5" />
              <stop offset="100%" stopColor="#1CB5E0" />
            </linearGradient>
          </defs>
        </svg>
        <CircularProgress sx={{ 'svg circle': { stroke: 'url(#my_gradient)' } }} />
      </React.Fragment>
    );
  }

  const [currentPageData, setCurrentPageData] = useState(null);
  const [selectedTextData, setSelectedTextData] = useState(null);

  const tabs = [
    'Raw-text', 'Layout', 'Forms', 'Tables', 'Queries', 'Signatures'
  ];  

  useEffect(() => {
    if (processedData[activeTab]) {
      const currentProcessedData = processedData[activeTab];
      
      if (['Raw-text', 'Layout', 'Tables'].includes(activeTab)) {
        const pageData =  currentProcessedData.data?.[currentPage - 1];
  
        setCurrentPageData(
          pageData ? (
            activeTab === 'Tables' 
              ? [pageData] 
              : pageData.map(data => ({
                  text: data.text,
                  x0: data.x0,
                  x1: data.x1,
                  top: data.top,
                  bottom: data.bottom,
                  ...(activeTab === 'Layout' && {
                    layoutno: data.layoutno,
                    score: data.score,
                    type: data.type
                  })
                }))
          ) : null
        );
      } else if (activeTab === 'Queries') {
        setCurrentPageData(
          currentProcessedData.data 
            ? Array.isArray(currentProcessedData.data) 
              ? currentProcessedData.data 
              : [currentProcessedData.data] 
            : null
        );
      } else {
        setCurrentPageData(currentProcessedData.data);
      }
    } else {
      setCurrentPageData(null);
    }
  }, [activeTab, processedData, currentPage, modelName]);

  const handleTextClick = (textData) => {
    setSelectedTextData(textData);
    onTextHighlight && onTextHighlight(textData);
  };

  const getCurrentTabContent = () => {
    if (processing) {
      return (
        <Box sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '400px',
          gap: 2
        }}>
          <GradientCircularProgress />
          <Typography variant="body1" color="text.secondary">
            Processing {activeTab} data...
          </Typography>
        </Box>
      );
    }
  
    if (activeTab === 'Queries') {
      return (
        <Box sx={{
          display: 'flex',
          flexDirection: 'column',
          height: 'calc(100vh - 150px)',
          gap: '20px'
        }}>
          {/* Chat messages display area */}
          <Box sx={{
            flex: 1,
            backgroundColor: '#f8f9fa',
            borderRadius: '8px',
            padding: '20px',
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column',
            gap: '15px'
          }}>
            {currentPageData && (
              <Box sx={{
                alignSelf: 'flex-start',
                maxWidth: '100%',
                backgroundColor: 'white',
                padding: '15px',
                borderRadius: '10px',
                boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
                wordWrap: 'break-word', 
                overflowWrap: 'break-word',  
                whiteSpace: 'pre-wrap',
              }}>
                <Typography variant="body1" sx={{wordBreak: 'break-word'}}>
                  {currentPageData}
                </Typography>
              </Box>
            )}
          </Box>
  
          {/* Query input area */}
          <Box sx={{
            display: 'flex',
            gap: '10px',
            padding: '10px',
            backgroundColor: 'white',
            borderRadius: '8px',
            boxShadow: '0 -2px 10px rgba(0,0,0,0.05)'
          }}>
            <Box sx={{
              flex: 1,
              display: 'flex',
              alignItems: 'center',
              backgroundColor: '#f8f9fa',
              borderRadius: '8px',
              padding: '8px 15px'
            }}>
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Ask a question about the document..."
                style={{
                  width: '100%',
                  border: 'none',
                  backgroundColor: 'transparent',
                  outline: 'none',
                  fontSize: '14px'
                }}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    onQuerySubmit();
                  }
                }}
              />
            </Box>
            <Button
              onClick={onQuerySubmit}
              disabled={processing || !message.trim()}
              sx={{
                minWidth: '100px',
                backgroundColor: '#0073bb',
                color: 'white',
                '&:hover': {
                  backgroundColor: '#005c99'
                },
                '&:disabled': {
                  backgroundColor: '#cccccc',
                  color: '#666666'
                }
              }}
            >
              {processing ? (
                <CircularProgress size={24} sx={{ color: 'white' }} />
              ) : (
                'Send'
              )}
            </Button>
          </Box>
        </Box>
      );
    }
  
    else if (!currentPageData) {
      return (
        <Box sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '400px'
        }}>
          <Typography variant="body1" color="text.secondary">
            No data available for {activeTab}
          </Typography>
        </Box>
      );
    }
  
    if (['Raw-text', 'Layout', 'Tables', 'Queries'].includes(activeTab)) {
      if (activeTab === 'Raw-text') {
        return (
          <Box sx={{
            display: 'flex',
            gap: '10px',
            flexWrap: 'wrap',
            textAlign: 'start',
          }}>
            {currentPageData.map((data, ind) => (
              <Button
                key={ind}
                onClick={() => handleTextClick(data)}
                sx={{
                  backgroundColor: selectedTextData === data ? '#f1faff' : '#eaeded',
                  border: selectedTextData === data ? '1px solid #0073bb' : '1px solid transparent',
                  textTransform: 'none',
                  color: 'black',
                  borderRadius: '10px',
                  fontWeight: 500,
                  fontFamily: 'Poppins',
                  transition: 'all 0.5s',
                  padding: '8px 12px',
                  whiteSpace: 'normal',
                  textAlign: 'center',
                  maxWidth: '100%',
                  '&:hover': {
                    backgroundColor: selectedTextData === data ? '#f1faff' : '#eaeded',
                    marginLeft: selectedTextData === data ? 0 : '1.5px',
                    border: selectedTextData === data ? '1px solid #0073bb' : '1px solid #0073bb',
                  },
                  '&.active': {
                    border: '1px solid #0073bb',
                  }
                }}
              >
                {data.text}
              </Button>
            ))}
          </Box>
        );
      } 
      
      else if (activeTab === 'Layout') {
        const getColorMapList = (numClasses) => {
          const customColors = {
            'header': [168, 68, 1],
            'text': [104, 138, 232],
            'table': [128, 0, 128],
          };
        
          const colorMap = [];
          for (let i = 0; i < numClasses; i++) {
            if (i === 7) {
              colorMap.push(customColors['header']);
            } else if (i === 1) {
              colorMap.push(customColors['text']);
            } else if (i === 5) {
              colorMap.push(customColors['table']);
            } else {
              const r = (i * 100 + 50) % 255;
              const g = (i * 150 + 50) % 255;
              const b = (i * 200 + 50) % 255;
              colorMap.push([r, g, b]);
            }
          }
          return colorMap;
        };
        
        const labels = [
          "_background_",
          "Text",
          "Title",
          "Figure",
          "Figure caption",
          "Table",
          "Table caption",
          "Header",
          "Footer",
          "Reference",
          "Equation",
          "Caption", 
          "Footnote", 
          "Formula", 
          "List-item", 
          "Page-footer", 
          "Page-header", 
          "Picture", 
          "Section-header", 
          "Form", 
          "Table-of-contents", 
          "Handwriting", 
          "Text-inline-math"
      ];
        
        const colorMap = getColorMapList(labels.length);
        const clsid2color = Object.fromEntries(
          labels.map((label, i) => [label.toLowerCase(), colorMap[i]])
        );
        
        const rgbToHex = (rgb) => {
          if (!rgb || !Array.isArray(rgb)) return '#808080';
          return '#' + rgb.map(x => {
            const hex = x.toString(16);
            return hex.length === 1 ? '0' + hex : hex;
          }).join('');
        };
        
        const getColorForType = (type = "text") => {
          const rgb = clsid2color[type.toLowerCase()];
          return rgbToHex(rgb);
        };
        
        return (
          <Box sx={{
            display: 'flex',
            flexDirection: 'column',
            gap: '10px',
            padding: '20px',
          }}>
            {currentPageData.map((item, index) => (
              <Box key={index} sx={{
                display: 'flex',
                flexDirection: 'column',
                gap: '5px',
              }}>
                <Box sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                }}>
                  <Box sx={{
                    width: '15px',
                    height: '15px',
                    backgroundColor: item?.type ? getColorForType(item.type) : '#808080',
                    borderRadius: '3px',
                  }} />
                  <Typography sx={{
                    fontSize: '14px',
                    color: '#666',
                    fontWeight: 500,
                  }}>
                    {item?.layoutno ? `${item.layoutno}` : 'text'}
                  </Typography>
                  <Typography sx={{
                    fontSize: '12px',
                    color: '#888',
                  }}>
                    {`CL: ${Math.round((item.score || 0) * 100)}%`}
                  </Typography>
                </Box>
                <Button
                  onClick={() => handleTextClick(item)}
                  sx={{
                    backgroundColor: selectedTextData === item ? '#f1faff' : '#eaeded',
                    border: selectedTextData === item ? '1px solid #0073bb' : '1px solid transparent',
                    textTransform: 'none',
                    color: 'black',
                    borderRadius: '10px',
                    fontWeight: 500,
                    fontFamily: 'Poppins',
                    transition: 'all 0.5s',
                    padding: '8px 12px',
                    whiteSpace: 'normal',
                    textAlign: 'left',
                    maxWidth: '100%',
                    '&:hover': {
                      backgroundColor: selectedTextData === item ? '#f1faff' : '#eaeded',
                      border: selectedTextData === item ? '1px solid #0073bb' : '1px solid #0073bb',
                    },
                    '&.active': {
                      border: '1px solid #0073bb',
                    }
                  }}
                >
                  {item?.text || 'No text available'}
                </Button>
              </Box>
            ))}
          </Box>
        );
      }
      else if (activeTab === 'Queries') {
        return (
          <Box sx={{
            display: 'flex',
            flexDirection: 'column',
            height: 'calc(100vh - 200px)',
            gap: '20px'
          }}>
            {/* Chat messages display area */}
            <Box sx={{
              flex: 1,
              backgroundColor: '#f8f9fa',
              borderRadius: '8px',
              padding: '20px',
              overflowY: 'auto',
              display: 'flex',
              flexDirection: 'column',
              gap: '15px'
            }}>
              {processedData['Queries'] && (
                <Box sx={{
                  alignSelf: 'flex-start',
                  maxWidth: '80%',
                  backgroundColor: 'white',
                  padding: '15px',
                  borderRadius: '10px',
                  boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
                }}>
                  <Typography variant="body1">
                    {processedData['Queries']}
                  </Typography>
                </Box>
              )}
            </Box>
      
            {/* Query input area */}
            <Box sx={{
              display: 'flex',
              gap: '10px',
              padding: '10px',
              backgroundColor: 'white',
              borderRadius: '8px',
              boxShadow: '0 -2px 10px rgba(0,0,0,0.05)'
            }}>
              <Box sx={{
                flex: 1,
                display: 'flex',
                alignItems: 'center',
                backgroundColor: '#f8f9fa',
                borderRadius: '8px',
                padding: '8px 15px'
              }}>
                <input
                  type="text"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Ask a question about the document..."
                  style={{
                    width: '100%',
                    border: 'none',
                    backgroundColor: 'transparent',
                    outline: 'none',
                    fontSize: '14px'
                  }}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      onQuerySubmit();
                    }
                  }}
                />
              </Box>
              <Button
                onClick={onQuerySubmit}
                disabled={processing || !message.trim()}
                sx={{
                  minWidth: '100px',
                  backgroundColor: '#0073bb',
                  color: 'white',
                  '&:hover': {
                    backgroundColor: '#005c99'
                  },
                  '&:disabled': {
                    backgroundColor: '#cccccc',
                    color: '#666666'
                  }
                }}
              >
                {processing ? (
                  <CircularProgress size={24} sx={{ color: 'white' }} />
                ) : (
                  'Send'
                )}
              </Button>
            </Box>
          </Box>
        );
      }
      else if (activeTab === 'Tables') {
        return (
          <Box sx={{
            overflowX: 'auto',
            width: '100%',
            // height: '100%',
            display: 'flex',
            flexDirection: 'column',
            gap: '20px'
          }}>
            {currentPageData?.map((htmlContent, index) => (
              <Box key={index} sx={{
                backgroundColor: 'white',
                borderRadius: '8px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                overflow: 'hidden',
                border: '1px solid #e0e0e0',
              }}>
                <iframe
                  srcDoc={htmlContent}
                  style={{
                    width: '100%',
                    height: '650px',
                    border: 'none',
                    backgroundColor: 'white'
                  }}
                  title={`Table Content - Page ${currentPage + 1}`}
                />
              </Box>
            ))}
          </Box>
        );
      }
    }
    return <pre>{JSON.stringify(currentPageData, null, 2)}</pre>;
  };

  return (
    <Box id="right-panel" sx={sx.rightPanel}>
      <ul className="nav nav-tabs mb-3">
        {tabs.map(tab => (
          <li className="nav-item" key={tab}>
            <a
              className={`nav-link ${activeTab === tab ? 'active' : ''}`}
              href={`#${tab}`}
              onClick={(e) => {
                e.preventDefault();
                setActiveTab(tab);
                onTextHighlight(null);
              }}
            >
              {tab.replace('-', ' ')}
            </a>
          </li>
        ))}
        <li className="nav-item model-toggle ms-auto">
          <ModelToggleButton 
            onModelChange={modelChange} 
            activeTab={activeTab}
            modelConfigByTab={modelConfigByTab} 
            mode={mode}
            setMode={setMode}
          />
        </li>
      </ul>
      <Box>
        <TabContent
          id={activeTab}
          active={true}
          content={getCurrentTabContent()}
        />
      </Box>
    </Box>
  );
}

export default RightPanel;