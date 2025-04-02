import React, { useState } from 'react';
import { Box, Button, Typography, CircularProgress } from '@mui/material';

interface AudioUploaderProps {
  onUpload: (file: File) => void;
  loading: boolean;
}

const AudioUploader: React.FC<AudioUploaderProps> = ({ onUpload, loading }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      
      // Check file type
      const validTypes = ['audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/flac', 'audio/mp4'];
      if (!validTypes.includes(file.type)) {
        setError('Please select a valid audio file (MP3, WAV, OGG, FLAC, M4A)');
        setSelectedFile(null);
        return;
      }
      
      // Check file size (max 50MB)
      if (file.size > 50 * 1024 * 1024) {
        setError('File size exceeds 50MB limit');
        setSelectedFile(null);
        return;
      }
      
      setSelectedFile(file);
      setError('');
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      setError('Please select an audio file');
      return;
    }
    
    onUpload(selectedFile);
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
      <Typography variant="h6" gutterBottom>
        Upload Audio File
      </Typography>
      
      <Box sx={{ 
        border: '2px dashed #ccc', 
        borderRadius: 2, 
        p: 3, 
        textAlign: 'center',
        mb: 2,
        backgroundColor: '#f8f8f8'
      }}>
        <input
          accept="audio/*"
          style={{ display: 'none' }}
          id="audio-file-upload"
          type="file"
          onChange={handleFileChange}
          disabled={loading}
        />
        <label htmlFor="audio-file-upload">
          <Button
            variant="contained"
            component="span"
            disabled={loading}
          >
            Select Audio File
          </Button>
        </label>
        
        {selectedFile && (
          <Typography variant="body1" sx={{ mt: 2 }}>
            Selected file: {selectedFile.name}
          </Typography>
        )}
        
        {error && (
          <Typography color="error" sx={{ mt: 1 }}>
            {error}
          </Typography>
        )}
      </Box>
      
      <Button 
        variant="contained" 
        color="primary" 
        type="submit" 
        disabled={!selectedFile || loading}
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

export default AudioUploader;
