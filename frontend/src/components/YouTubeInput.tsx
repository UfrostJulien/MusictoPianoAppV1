import React, { useState } from 'react';
import { Box, Button, Typography, CircularProgress, TextField } from '@mui/material';

interface YouTubeInputProps {
  onSubmit: (url: string) => void;
  loading: boolean;
}

const YouTubeInput: React.FC<YouTubeInputProps> = ({ onSubmit, loading }) => {
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Basic validation
    if (!url) {
      setError('Please enter a YouTube URL');
      return;
    }

    // Simple YouTube URL validation
    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$/;
    if (!youtubeRegex.test(url)) {
      setError('Please enter a valid YouTube URL');
      return;
    }

    setError('');
    onSubmit(url);
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
      <Typography variant="h6" gutterBottom>
        Enter YouTube URL
      </Typography>
      
      <TextField
        fullWidth
        label="YouTube URL"
        variant="outlined"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        disabled={loading}
        error={!!error}
        helperText={error}
        placeholder="https://www.youtube.com/watch?v=..."
        sx={{ mb: 2 }}
      />
      
      <Button 
        variant="contained" 
        color="primary" 
        type="submit" 
        disabled={loading}
        sx={{ mt: 1 }}
      >
        {loading ? (
          <>
            <CircularProgress size={24} sx={{ mr: 1 }} color="inherit" />
            Processing...
          </>
        ) : (
          'Generate Sheet Music'
        )}
      </Button>
    </Box>
  );
};

export default YouTubeInput;
