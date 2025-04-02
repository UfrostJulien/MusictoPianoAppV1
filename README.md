# Music Transcription App

A web application that transcribes music from audio files or YouTube links and generates piano sheet music.

## Project Structure

This repository is organized into two main directories:

- `backend/`: Flask API for audio processing, transcription, and sheet music generation
- `frontend/`: React application for the user interface

## Features

- Upload audio files (MP3, WAV, OGG, FLAC, M4A)
- Process YouTube links
- Transcribe audio to detect melody and chorus
- Generate piano sheet music optimized for beginners and intermediate players
- Download sheet music as PDF

## Deployment Instructions

### Backend Deployment on Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Select the `backend` directory as the root directory
4. Use the following settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn run:app`
   - Environment: Python 3
5. Add the following environment variables:
   - `PORT`: 5000
   - `SECRET_KEY`: (generate a random string)

### Frontend Deployment on Render

1. Create a new Static Site on Render
2. Connect your GitHub repository
3. Select the `frontend` directory as the root directory
4. Use the following settings:
   - Build Command: `npm install && npm run build`
   - Publish Directory: `build`

## Local Development

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python run.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Run the development server:
   ```
   npm start
   ```

## Technical Details

- **Backend**: Flask API with Librosa for audio analysis
- **Frontend**: React with Material UI components
- **Audio Processing**: Uses Librosa for audio analysis and feature extraction
- **Sheet Music Generation**: Custom implementation for piano arrangements

## Fixed Issues

This repository includes fixes for the following issues:

1. Module structure issues (changed relative imports to absolute imports)
2. SSL configuration issues (removed adhoc SSL certificates)
3. Hardcoded backend URL (implemented dynamic URL detection)
4. Frontend structure issues (created proper React application structure)

These fixes resolve the "failed to fetch" errors that were occurring when uploading audio files or using YouTube links.
