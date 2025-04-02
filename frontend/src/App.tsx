import React, { useState } from 'react';
import { 
  Container, Typography, Box, Stepper, Step, StepLabel, 
  Button, Paper, CircularProgress, Divider
} from '@mui/material';
import AudioUploader from './components/AudioUploader';
import YouTubeInput from './components/YouTubeInput';
import SheetMusicViewer from './components/SheetMusicViewer';
import './App.css';

const steps = ['Select Audio Source', 'Process Audio', 'Generate Sheet Music', 'Download Result'];

// Get the backend URL from environment or use a relative URL for Render deployment
// This will be updated with the actual Render URL after deployment
const BACKEND_URL = window.location.origin.includes('localhost') 
  ? 'http://localhost:5000' 
  : window.location.origin;

function App() {
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [audioSource, setAudioSource] = useState<string>('file'); // 'file' or 'youtube'

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleReset = () => {
    setActiveStep(0);
    setJobId(null);
    setPdfUrl(null);
    setError(null);
  };

  const handleAudioSourceChange = (source: string) => {
    setAudioSource(source);
  };

  const handleFileUpload = async (file: File) => {
    setLoading(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      console.log('Uploading file to:', `${BACKEND_URL}/api/audio/upload`);
      
      const response = await fetch(`${BACKEND_URL}/api/audio/upload`, {
        method: 'POST',
        body: formData,
        mode: 'cors',
        credentials: 'omit',
        headers: {
          'Accept': 'application/json',
        }
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Failed to upload file');
      }
      
      setJobId(data.job_id);
      handleNext();
    } catch (err: any) {
      console.error('File upload error:', err);
      setError(err.message || 'An error occurred during file upload');
    } finally {
      setLoading(false);
    }
  };

  const handleYouTubeSubmit = async (url: string) => {
    setLoading(true);
    setError(null);
    
    try {
      console.log('Submitting YouTube URL to:', `${BACKEND_URL}/api/audio/youtube`);
      
      const response = await fetch(`${BACKEND_URL}/api/audio/youtube`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        mode: 'cors',
        credentials: 'omit',
        body: JSON.stringify({ url }),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Failed to process YouTube URL');
      }
      
      setJobId(data.job_id);
      handleNext();
    } catch (err: any) {
      console.error('YouTube URL error:', err);
      setError(err.message || 'An error occurred while processing YouTube URL');
    } finally {
      setLoading(false);
    }
  };

  const handleTranscribe = async () => {
    setLoading(true);
    setError(null);
    
    try {
      console.log('Transcribing audio with job ID:', jobId);
      
      const response = await fetch(`${BACKEND_URL}/api/transcription/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        mode: 'cors',
        credentials: 'omit',
        body: JSON.stringify({ 
          job_id: jobId,
          options: {
            detect_chorus_only: true,
            simplify_arrangement: true,
            difficulty: 'beginner'
          }
        }),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Failed to transcribe audio');
      }
      
      handleNext();
    } catch (err: any) {
      console.error('Transcription error:', err);
      setError(err.message || 'An error occurred during transcription');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateSheetMusic = async () => {
    setLoading(true);
    setError(null);
    
    try {
      console.log('Generating sheet music with job ID:', jobId);
      
      const response = await fetch(`${BACKEND_URL}/api/sheet-music/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        mode: 'cors',
        credentials: 'omit',
        body: JSON.stringify({ 
          job_id: jobId,
          options: {
            title: 'Transcribed Music',
            composer: 'Music Transcription App',
            difficulty: 'beginner',
            include_chords: true
          }
        }),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Failed to generate sheet music');
      }
      
      setPdfUrl(`${BACKEND_URL}/api/sheet-music/download/pdf/${jobId}`);
      handleNext();
    } catch (err: any) {
      console.error('Sheet music generation error:', err);
      setError(err.message || 'An error occurred during sheet music generation');
    } finally {
      setLoading(false);
    }
  };

  const getStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Box sx={{ mt: 2 }}>
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Select Audio Source
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Button 
                  variant={audioSource === 'file' ? 'contained' : 'outlined'} 
                  onClick={() => handleAudioSourceChange('file')}
                  sx={{ mr: 1 }}
                >
                  Upload Audio File
                </Button>
                <Button 
                  variant={audioSource === 'youtube' ? 'contained' : 'outlined'} 
                  onClick={() => handleAudioSourceChange('youtube')}
                >
                  YouTube URL
                </Button>
              </Box>
              
              <Divider sx={{ my: 2 }} />
              
              {audioSource === 'file' ? (
                <AudioUploader onUpload={handleFileUpload} loading={loading} />
              ) : (
                <YouTubeInput onSubmit={handleYouTubeSubmit} loading={loading} />
              )}
            </Paper>
          </Box>
        );
      case 1:
        return (
          <Box sx={{ mt: 2 }}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Process Audio
              </Typography>
              <Typography paragraph>
                The audio is being processed to detect the main melody and chorus.
              </Typography>
              <Box sx={{ display: 'flex', justifyContent: 'center', my: 3 }}>
                {loading ? (
                  <CircularProgress />
                ) : (
                  <Button variant="contained" onClick={handleTranscribe}>
                    Transcribe Audio
                  </Button>
                )}
              </Box>
            </Paper>
          </Box>
        );
      case 2:
        return (
          <Box sx={{ mt: 2 }}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Generate Sheet Music
              </Typography>
              <Typography paragraph>
                The audio has been transcribed. Now you can generate the sheet music.
              </Typography>
              <Box sx={{ display: 'flex', justifyContent: 'center', my: 3 }}>
                {loading ? (
                  <CircularProgress />
                ) : (
                  <Button variant="contained" onClick={handleGenerateSheetMusic}>
                    Generate Sheet Music
                  </Button>
                )}
              </Box>
            </Paper>
          </Box>
        );
      case 3:
        return (
          <Box sx={{ mt: 2 }}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Download Result
              </Typography>
              <Typography paragraph>
                Your sheet music has been generated successfully!
              </Typography>
              
              {pdfUrl && (
                <Box sx={{ my: 3 }}>
                  <SheetMusicViewer pdfUrl={pdfUrl} />
                </Box>
              )}
              
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
                <Button 
                  variant="contained" 
                  color="primary" 
                  href={pdfUrl || '#'} 
                  target="_blank"
                  disabled={!pdfUrl}
                >
                  Download PDF
                </Button>
              </Box>
            </Paper>
          </Box>
        );
      default:
        return 'Unknown step';
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Music Transcription App
        </Typography>
        <Typography variant="subtitle1" align="center" color="text.secondary" paragraph>
          Generate piano sheet music from audio files or YouTube links
        </Typography>
        
        <Stepper activeStep={activeStep} sx={{ pt: 3, pb: 5 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
        
        {error && (
          <Paper sx={{ p: 2, mb: 2, bgcolor: 'error.light' }}>
            <Typography color="error.dark">{error}</Typography>
          </Paper>
        )}
        
        {getStepContent(activeStep)}
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
          <Button
            disabled={activeStep === 0 || loading}
            onClick={handleBack}
          >
            Back
          </Button>
          
          {activeStep === steps.length - 1 ? (
            <Button onClick={handleReset} variant="contained">
              Start New Transcription
            </Button>
          ) : null}
        </Box>
      </Box>
    </Container>
  );
}

export default App;
