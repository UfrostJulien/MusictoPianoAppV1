import React from 'react';
import { Box, Typography } from '@mui/material';

interface SheetMusicViewerProps {
  pdfUrl: string;
}

const SheetMusicViewer: React.FC<SheetMusicViewerProps> = ({ pdfUrl }) => {
  return (
    <Box sx={{ width: '100%', height: '500px', overflow: 'hidden' }}>
      <Typography variant="subtitle1" gutterBottom>
        Sheet Music Preview
      </Typography>
      <Box 
        component="iframe"
        src={pdfUrl}
        sx={{ 
          width: '100%', 
          height: '450px', 
          border: '1px solid #ccc',
          borderRadius: '4px'
        }}
        title="Sheet Music PDF"
      />
    </Box>
  );
};

export default SheetMusicViewer;
