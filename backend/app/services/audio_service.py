"""
Audio service for processing audio files and YouTube URLs
"""

import os
import subprocess
import uuid
from pydub import AudioSegment

def download_youtube_audio(url, output_dir):
    """
    Download audio from YouTube URL
    
    Args:
        url (str): YouTube URL
        output_dir (str): Directory to save audio file
        
    Returns:
        str: Path to downloaded audio file
    """
    # Generate output filename
    output_file = os.path.join(output_dir, f"youtube_audio_{uuid.uuid4().hex}.mp3")
    
    # Download audio using yt-dlp
    try:
        subprocess.run([
            'yt-dlp',
            '-x',  # Extract audio
            '--audio-format', 'mp3',  # Convert to mp3
            '--audio-quality', '0',  # Best quality
            '-o', output_file,  # Output file
            url  # YouTube URL
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        return output_file
    
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to download YouTube audio: {e.stderr.decode('utf-8')}")

def process_audio_file(file_path, output_dir):
    """
    Process audio file (normalize, convert to WAV if needed)
    
    Args:
        file_path (str): Path to audio file
        output_dir (str): Directory to save processed file
        
    Returns:
        str: Path to processed audio file
    """
    # Load audio file
    try:
        audio = AudioSegment.from_file(file_path)
    except Exception as e:
        raise Exception(f"Failed to load audio file: {str(e)}")
    
    # Normalize audio
    normalized_audio = audio.normalize()
    
    # Convert to WAV if not already
    output_file = os.path.join(output_dir, "processed_audio.wav")
    normalized_audio.export(output_file, format="wav")
    
    # Create status file
    with open(os.path.join(output_dir, 'status.txt'), 'w') as f:
        f.write('processed')
    
    return output_file
