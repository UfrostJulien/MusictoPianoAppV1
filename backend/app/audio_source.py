"""
Audio Source Module - Handles extraction of audio from various sources.
"""

import os
import tempfile
from typing import Dict, Optional, Tuple

import yt_dlp
from pydub import AudioSegment


class AudioSourceError(Exception):
    """Exception raised for errors in the AudioSource module."""
    pass


class YouTubeExtractor:
    """Class for extracting audio from YouTube videos."""
    
    def __init__(self, output_dir: Optional[str] = None, format: str = "wav"):
        """
        Initialize the YouTube extractor.
        
        Args:
            output_dir: Directory to save extracted audio files. If None, uses a temporary directory.
            format: Audio format to save (wav, mp3, etc.)
        """
        self.output_dir = output_dir or tempfile.gettempdir()
        self.format = format
        os.makedirs(self.output_dir, exist_ok=True)
    
    def extract_audio(self, youtube_url: str) -> Dict:
        """
        Extract audio from a YouTube URL.
        
        Args:
            youtube_url: URL of the YouTube video
            
        Returns:
            Dictionary containing:
                - file_path: Path to the extracted audio file
                - title: Title of the video
                - duration: Duration in seconds
                - sample_rate: Sample rate of the audio
        
        Raises:
            AudioSourceError: If extraction fails
        """
        try:
            # Create a unique filename based on video ID
            video_id = self._extract_video_id(youtube_url)
            output_file = os.path.join(self.output_dir, f"{video_id}.{self.format}")
            
            # Configure yt-dlp options
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': self.format,
                    'preferredquality': '192',
                }],
                'outtmpl': output_file.replace(f".{self.format}", ""),
                'quiet': True,
                'no_warnings': True,
            }
            
            # Extract audio
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)
                
            # Get audio properties
            audio = AudioSegment.from_file(output_file)
            
            return {
                'file_path': output_file,
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'sample_rate': audio.frame_rate,
                'channels': audio.channels,
                'format': self.format
            }
            
        except Exception as e:
            raise AudioSourceError(f"Failed to extract audio from YouTube: {str(e)}")
    
    def _extract_video_id(self, youtube_url: str) -> str:
        """
        Extract the video ID from a YouTube URL.
        
        Args:
            youtube_url: URL of the YouTube video
            
        Returns:
            Video ID as a string
        """
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                return info['id']
        except Exception as e:
            raise AudioSourceError(f"Failed to extract video ID: {str(e)}")


class AudioFileLoader:
    """Class for loading audio from local files."""
    
    def __init__(self, target_format: str = "wav", target_sample_rate: int = 44100):
        """
        Initialize the audio file loader.
        
        Args:
            target_format: Format to convert audio to
            target_sample_rate: Sample rate to convert audio to
        """
        self.target_format = target_format
        self.target_sample_rate = target_sample_rate
    
    def load_audio(self, file_path: str) -> Dict:
        """
        Load audio from a file and normalize format.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Dictionary containing:
                - file_path: Path to the processed audio file
                - duration: Duration in seconds
                - sample_rate: Sample rate of the audio
        
        Raises:
            AudioSourceError: If loading fails
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                raise AudioSourceError(f"File not found: {file_path}")
            
            # Load audio file
            audio = AudioSegment.from_file(file_path)
            
            # Convert to target format and sample rate if needed
            if audio.frame_rate != self.target_sample_rate:
                audio = audio.set_frame_rate(self.target_sample_rate)
            
            # If the input file is not in the target format, convert it
            file_name, file_ext = os.path.splitext(file_path)
            if file_ext[1:].lower() != self.target_format:
                output_file = f"{file_name}.{self.target_format}"
                audio.export(output_file, format=self.target_format)
            else:
                output_file = file_path
            
            return {
                'file_path': output_file,
                'title': os.path.basename(file_name),
                'duration': len(audio) / 1000.0,  # Convert ms to seconds
                'sample_rate': audio.frame_rate,
                'channels': audio.channels,
                'format': self.target_format
            }
            
        except Exception as e:
            raise AudioSourceError(f"Failed to load audio file: {str(e)}")


def get_audio_from_source(source: str, output_dir: Optional[str] = None) -> Dict:
    """
    Unified function to get audio from either YouTube or local file.
    
    Args:
        source: YouTube URL or path to local file
        output_dir: Directory to save extracted audio
        
    Returns:
        Dictionary with audio information
        
    Raises:
        AudioSourceError: If extraction fails
    """
    # Check if source is a YouTube URL
    if "youtube.com" in source or "youtu.be" in source:
        extractor = YouTubeExtractor(output_dir=output_dir)
        return extractor.extract_audio(source)
    
    # Otherwise treat as local file
    else:
        loader = AudioFileLoader()
        return loader.load_audio(source)
