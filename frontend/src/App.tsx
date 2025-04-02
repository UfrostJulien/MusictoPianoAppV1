import React, { useState, useEffect } from 'react';
import { Box, Container, Typography, CircularProgress, Tabs, Tab, Paper } from '@mui/material';
import './App.css';
import AudioUploader from './components/AudioUploader';
import YouTubeInput from './components/YouTubeInput';
import SheetMusicViewer from './components/SheetMusicViewer';

// Dynamic backend URL detection
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 
                   (window.location.hostname === 'localhost' ? 
                    'http://localhost:5000' : 
                    'https://musictopianoappbackend.onrender.com');

function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [sheetMusicUrl, setSheetMusicUrl] = useState('');
  const [tabValue, setTabValue] = useState(0);
  const [apiStatus, setApiStatus] = useState('checking');

  useEffect(() => {
    // Check if the backend API is available
    const checkApiStatus = async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/api/health`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        
        if (response.ok) {
          setApiStatus('online');
        } else {
          setApiStatus('offline');
        }
      } catch (err) {
        console.error('Error checking API status:', err);
        setApiStatus('offline');
      }
    };

    checkApiStatus();
  }, []);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleFileUpload = async (file: File) => {
    setLoading(true);
    setError('');
    setSheetMusicUrl('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${BACKEND_URL}/api/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setSheetMusicUrl(data.sheet_music_url);
    } catch (err) {
      console.error('Error uploading file:', err);
      setError(`Error uploading file: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setLoading(false);
    }
  };

  const handleYouTubeSubmit = async (url: string) => {
    setLoading(true);
    setError('');
    setSheetMusicUrl('');

    try {
      const response = await fetch(`${BACKEND_URL}/api/youtube`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setSheetMusicUrl(data.sheet_music_url);
    } catch (err) {
      console.error('Error processing YouTube URL:', err);
      setError(`Error processing YouTube URL: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom align="center">
          Music Transcription App
        </Typography>
        <Typography variant="subtitle1" gutterBottom align="center">
          Generate piano sheet music from audio files or YouTube links
        </Typography>

        {apiStatus === 'checking' && (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
            <CircularProgress />
            <Typography sx={{ ml: 2 }}>Checking API status...</Typography>
          </Box>
        )}

        {apiStatus === 'offline' && (
          <Box sx={{ mt: 4, p: 2, bgcolor: '#ffebee', borderRadius: 1 }}>
            <Typography color="error">
              The backend API is currently offline or unreachable. Please try again later.
            </Typography>
          </Box>
        )}

        {apiStatus === 'online' && (
          <Paper sx={{ mt: 4, p: 3 }}>
            <Tabs value={tabValue} onChange={handleTabChange} centered sx={{ mb: 3 }}>
              <Tab label="Upload Audio File" />
              <Tab label="YouTube Link" />
            </Tabs>

            {tabValue === 0 && (
              <AudioUploader onUpload={handleFileUpload} loading={loading} />
            )}

            {tabValue === 1 && (
              <YouTubeInput onSubmit={handleYouTubeSubmit} loading={loading} />
            )}

            {loading && (
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                <CircularProgress />
              </Box>
            )}

            {error && (
              <Box sx={{ mt: 4, p: 2, bgcolor: '#ffebee', borderRadius: 1 }}>
                <Typography color="error">{error}</Typography>
              </Box>
            )}

            {sheetMusicUrl && !loading && (
              <Box sx={{ mt: 4 }}>
                <SheetMusicViewer pdfUrl={sheetMusicUrl} />
              </Box>
            )}
          </Paper>
        )}
      </Box>
    </Container>
  );
}

export default App;
