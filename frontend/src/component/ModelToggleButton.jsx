import * as React from 'react';
import { styled } from '@mui/material/styles';
import Switch from '@mui/material/Switch';
import { useState } from 'react';

export default function ModelToggle({ onModelChange, activeTab, modelConfigByTab}) {
  const currentModes = modelConfigByTab[activeTab] || [{ num: 0, value: "RAGFLOW" }];
  const [mode, setMode] = useState(currentModes[0]);

  const handleModelChange = () => {
    const currentIndex = currentModes.findIndex(m => m.value === mode.value);
    const nextModeIndex = (currentIndex + 1) % currentModes.length;
    const newMode = currentModes[nextModeIndex];
    
    setMode(newMode);
    onModelChange(newMode.value);
    console.log(newMode.value)
  };

  // Updated model icons to match the new configurations
  const modelIcons = {
    'RAGFLOW': `url('/icons/ragflow_logo.svg')`,
    'TESSERACT': `url('/icons/tesseractocr_logo.svg')`,
    'PADDLE': `url('/icons/paddlepaddle_logo.svg')`,
    'SURYA': `url('/icons/suryaocr_logo.svg')`,
    'EASY': `url('/icons/easycr_logo.svg')`,
    'RAPID': `url('/icons/rapidAI_logo.svg')`,
    'MM': `url('/icons/mmocr_logo.svg')`,
    'VINY': `url('/icons/chakra_logo.svg')`
  };

  if (currentModes.length <= 1) {
    return null;
  }

  const ModelSwitch = styled(Switch)(({ theme }) => ({
    width: 90,
    height: 34,
    padding: 7,
    '& .MuiSwitch-switchBase': {
      margin: 1,
      padding: 0,
      transform: 'translateX(6px)',
      '&.Mui-checked': {
        color: '#fff',
        '&[data-state="0"]': { transform: 'translateX(6px)' },
        '&[data-state="1"]': { transform: 'translateX(30px)' },
        '&[data-state="2"]': { transform: 'translateX(54px)' },
        '&[data-state="3"]': { transform: 'translateX(30px)' },  
        '&[data-state="4"]': { transform: 'translateX(6px)' },    
        '&[data-state="5"]': { transform: 'translateX(30px)' },
        '&[data-state="6"]': { transform: 'translateX(54px)' },
        '& + .MuiSwitch-track': {
          opacity: 1,
          backgroundColor: '#aab4be',
          ...theme.applyStyles('light', {
            backgroundColor: '#aab4be',
          }),
        },
      },
    },
    '& .MuiSwitch-thumb': {
      backgroundColor: '#aab4be',
      width: 32,
      height: 32,
      '&::before': {
        content: "''",
        position: 'absolute',
        width: '100%',
        height: '100%',
        left: 0,
        top: 0,
        backgroundRepeat: 'no-repeat',
        backgroundPosition: 'center',
      },
      ...theme.applyStyles('dark', {
        backgroundColor: '#aab4be',
      }),
    },
    '& .MuiSwitch-track': {
      opacity: 1,
      backgroundColor: '#aab4be',
      borderRadius: 20 / 2,
      ...theme.applyStyles('dark', {
        backgroundColor: '#aab4be',
      }),
    },
  }));

  return (
    <ModelSwitch
      checked={mode.num > 0}
      data-state={mode.num}
      onChange={handleModelChange}
      sx={{
        '& .MuiSwitch-switchBase': {
          transform: `translateX(${mode.num * 10}px)`,
        },
        '& .MuiSwitch-thumb:before': {
          backgroundImage: modelIcons[mode.value]
        },
      }}
    />
  );
}