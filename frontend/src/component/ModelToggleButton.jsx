import * as React from 'react';
import { styled } from '@mui/material/styles';
import Switch from '@mui/material/Switch';
import { useState } from 'react';

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

export default function ModelToggle({ onModelChange }) {
  const [mode, setMode] = useState({
    num: 0,
    value: "RAGFLOW",
  });

  const handleModelChange = () => {
    const modes = [
      { num: 0, value: "RAGFLOW" },   
      { num: 1, value: "TESSERACT" }, 
      { num: 2, value: "PADDLE" },   
      { num: 3, value: "SURYA" },
      { num: 4, value: "EASY" },
      { num: 5, value: "RAPID" },
      { num: 6, value: "MM" },
    ];

    const nextModeIndex = (mode.num + 1) % modes.length;
    const newMode = modes[nextModeIndex];

    setMode(newMode);
    onModelChange(newMode.value);
  };

  const modelIcons = [
    `url('/icons/ragflow_logo.svg')`,          
    `url('/icons/tesseractocr_logo.svg')`, 
    `url('/icons/paddlepaddle_logo.svg')`,    
    `url('/icons/suryaocr_logo.svg')`,   
    `url('/icons/easycr_logo.svg')`,   
    `url('/icons/rapidAI_logo.svg')`,  
    `url('/icons/mmocr_logo.svg')`, 
  ];

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
          backgroundImage: modelIcons[mode.num]
        },
      }}
    />
  );
}
