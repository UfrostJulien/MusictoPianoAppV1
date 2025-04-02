import React from 'react';
import { Box, Typography, Button } from '@mui/material';

interface SheetMusicViewerProps {
  pdfUrl: string;
}

const SheetMusicViewer: React.FC<SheetMusicViewerProps> = ({ pdfUrl }) => {
  return (
    <Box sx={{ width: '100%', textAlign: 'center' }}>
      <Typography variant="h6" gutterBottom>
        Sheet Music Generated!
      </Typography>
      
      <Box sx={{ 
        border: '1px solid #ccc', 
        borderRadius: 2, 
        p: 2, 
        mb: 2,
        height: '500px',
        overflow: 'hidden'
      }}>
        <iframe 
          src={pdfUrl} 
          width="100%" 
          height="100%" 
          style={{ border: 'none' }}
          title="Sheet Music PDF"
        />
      </Box>
      
      <Button 
        variant="contained" 
        color="primary" 
        href={pdfUrl} 
        target="_blank"
        rel="noopener noreferrer"
      >
        Download PDF
      </Button>
    </Box>
  );
};

export default SheetMusicViewer;
