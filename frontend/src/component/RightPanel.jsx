import React, { useState, useEffect } from 'react';
import { Box, Button, Typography, CircularProgress } from '@mui/material';
import TabContent from './TabContent';
import ModelToggleButton from './ModelToggleButton';

function RightPanel({ activeTab, setActiveTab, modelChange, processedData, currentPage, onTextHighlight, processing }) {
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
      if (activeTab === 'Raw-text' || activeTab === 'Layout') {
        const pageData = processedData[activeTab][currentPage]?.at(0);
        console.log("Page data:", pageData);
        
        if (pageData) {
          setCurrentPageData(pageData.map((data) => ({
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
          })));
        } else {
          setCurrentPageData(null);
        }
      } else {
        setCurrentPageData(processedData[activeTab]);
      }
    } else {
      setCurrentPageData(null);
    }
  }, [activeTab, processedData, currentPage]);

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

    if (!currentPageData) {
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
  
    if ((activeTab === 'Raw-text' || activeTab === 'Layout') && Array.isArray(currentPageData)) {
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
      
      if (activeTab === 'Layout') {
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
          "Equation"
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
          <ModelToggleButton onModelChange={modelChange} />
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