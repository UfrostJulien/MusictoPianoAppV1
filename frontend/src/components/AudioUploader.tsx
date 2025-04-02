import React from 'react';
import { Box, Typography, Button, Input } from '@mui/material';

interface AudioUploaderProps {
  onUpload: (file: File) => void;
  loading: boolean;
}

const AudioUploader: React.FC<AudioUploaderProps> = ({ onUpload, loading }) => {
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      onUpload(files[0]);
    }
  };

  return (
    <Box>
      <Typography variant="subtitle1" gutterBottom>
        Upload an audio file (MP3, WAV, OGG, FLAC, M4A)
      </Typography>
      <Box sx={{ display: 'flex', alignItems: 'center', mt: 2 }}>
        <Input
          type="file"
          inputProps={{
            accept: '.mp3,.wav,.ogg,.flac,.m4a',
            disabled: loading
          }}
          onChange={handleFileChange}
          sx={{ flexGrow: 1 }}
        />
      </Box>
    </Box>
  );
};

export default AudioUploader;
