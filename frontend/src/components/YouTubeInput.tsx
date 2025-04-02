import React, { useState } from 'react';
import { Box, Typography, TextField, Button } from '@mui/material';

interface YouTubeInputProps {
  onSubmit: (url: string) => void;
  loading: boolean;
}

const YouTubeInput: React.FC<YouTubeInputProps> = ({ onSubmit, loading }) => {
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Simple validation
    if (!url.trim()) {
      setError('Please enter a YouTube URL');
      return;
    }
    
    if (!url.includes('youtube.com/') && !url.includes('youtu.be/')) {
      setError('Please enter a valid YouTube URL');
      return;
    }
    
    setError('');
    onSubmit(url);
  };

  return (
    <Box component="form" onSubmit={handleSubmit}>
      <Typography variant="subtitle1" gutterBottom>
        Enter a YouTube URL
      </Typography>
      <TextField
        fullWidth
        label="YouTube URL"
        variant="outlined"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        error={!!error}
        helperText={error}
        disabled={loading}
        sx={{ mb: 2 }}
        placeholder="https://www.youtube.com/watch?v=..."
      />
      <Button 
        type="submit" 
        variant="contained" 
        disabled={loading}
      >
        Process YouTube URL
      </Button>
    </Box>
  );
};

export default YouTubeInput;
