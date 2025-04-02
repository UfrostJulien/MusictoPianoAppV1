"""
Audio Processing Module - Handles audio analysis and chorus detection.
"""

import os
import numpy as np
import librosa
from typing import Dict, List, Optional, Tuple, Union


class AudioProcessingError(Exception):
    """Exception raised for errors in the AudioProcessing module."""
    pass


class AudioProcessor:
    """Class for processing audio files and detecting main/chorus sections."""
    
    def __init__(self, sample_rate: int = 22050):
        """
        Initialize the audio processor.
        
        Args:
            sample_rate: Target sample rate for audio processing
        """
        self.sample_rate = sample_rate
    
    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """
        Load audio file for processing.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Tuple of (audio_data, sample_rate)
            
        Raises:
            AudioProcessingError: If loading fails
        """
        try:
            audio_data, sr = librosa.load(file_path, sr=self.sample_rate, mono=True)
            return audio_data, sr
        except Exception as e:
            raise AudioProcessingError(f"Failed to load audio file: {str(e)}")
    
    def detect_chorus(self, audio_data: np.ndarray, sr: int) -> List[Dict]:
        """
        Detect chorus or main sections in the audio.
        
        This uses a combination of techniques:
        1. Structural segmentation to find repeated sections
        2. Energy analysis to identify high-energy segments
        3. Novelty detection to find significant changes
        
        Args:
            audio_data: Audio time series
            sr: Sample rate
            
        Returns:
            List of dictionaries containing:
                - start_time: Start time in seconds
                - end_time: End time in seconds
                - confidence: Confidence score (0-1)
        """
        try:
            # Calculate various features
            segments = self._detect_segments(audio_data, sr)
            energy_profile = self._calculate_energy_profile(audio_data, sr)
            
            # Find repeated segments (potential choruses)
            repeated_segments = self._find_repeated_segments(segments)
            
            # Score segments based on energy and repetition
            scored_segments = self._score_segments(repeated_segments, energy_profile, audio_data, sr)
            
            # Sort by confidence score
            scored_segments.sort(key=lambda x: x['confidence'], reverse=True)
            
            return scored_segments
        
        except Exception as e:
            raise AudioProcessingError(f"Failed to detect chorus: {str(e)}")
    
    def extract_segment(self, audio_data: np.ndarray, sr: int, start_time: float, end_time: float) -> np.ndarray:
        """
        Extract a segment of audio between start and end times.
        
        Args:
            audio_data: Audio time series
            sr: Sample rate
            start_time: Start time in seconds
            end_time: End time in seconds
            
        Returns:
            Audio segment as numpy array
        """
        start_sample = int(start_time * sr)
        end_sample = int(end_time * sr)
        
        # Ensure within bounds
        start_sample = max(0, start_sample)
        end_sample = min(len(audio_data), end_sample)
        
        return audio_data[start_sample:end_sample]
    
    def _detect_segments(self, audio_data: np.ndarray, sr: int) -> List[Dict]:
        """
        Detect structural segments in the audio.
        
        Args:
            audio_data: Audio time series
            sr: Sample rate
            
        Returns:
            List of segment dictionaries with start and end times
        """
        # Calculate MFCC features
        mfcc = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=13)
        
        # Detect segment boundaries using spectral clustering
        # Updated to match current librosa API
        k = 8  # Number of segments
        boundary_frames = librosa.segment.agglomerative(mfcc, k)
        boundary_times = librosa.frames_to_time(boundary_frames, sr=sr)
        
        # Create segment list
        segments = []
        for i in range(len(boundary_times) - 1):
            segments.append({
                'start_time': boundary_times[i],
                'end_time': boundary_times[i + 1]
            })
        
        return segments
    
    def _calculate_energy_profile(self, audio_data: np.ndarray, sr: int) -> np.ndarray:
        """
        Calculate energy profile of the audio.
        
        Args:
            audio_data: Audio time series
            sr: Sample rate
            
        Returns:
            Energy profile as numpy array
        """
        # Calculate RMS energy
        frame_length = 2048
        hop_length = 512
        
        # Get RMS energy for each frame
        energy = librosa.feature.rms(y=audio_data, frame_length=frame_length, hop_length=hop_length)[0]
        
        # Normalize
        energy = (energy - np.min(energy)) / (np.max(energy) - np.min(energy) + 1e-10)
        
        return energy
    
    def _find_repeated_segments(self, segments: List[Dict]) -> List[Dict]:
        """
        Find potentially repeated segments based on similarity.
        
        Args:
            segments: List of segment dictionaries
            
        Returns:
            List of repeated segment dictionaries
        """
        # For now, we'll just return all segments
        # In a more sophisticated implementation, we would analyze
        # the similarity between segments to find repetitions
        return segments
    
    def _score_segments(self, segments: List[Dict], energy_profile: np.ndarray, 
                        audio_data: np.ndarray, sr: int) -> List[Dict]:
        """
        Score segments based on energy and other features.
        
        Args:
            segments: List of segment dictionaries
            energy_profile: Energy profile of the audio
            audio_data: Audio time series
            sr: Sample rate
            
        Returns:
            List of scored segment dictionaries
        """
        hop_length = 512
        scored_segments = []
        
        for segment in segments:
            start_time = segment['start_time']
            end_time = segment['end_time']
            
            # Convert times to frames
            start_frame = librosa.time_to_frames(start_time, sr=sr, hop_length=hop_length)
            end_frame = librosa.time_to_frames(end_time, sr=sr, hop_length=hop_length)
            
            # Ensure within bounds
            start_frame = max(0, start_frame)
            end_frame = min(len(energy_profile), end_frame)
            
            if start_frame >= end_frame:
                continue
            
            # Calculate average energy for this segment
            avg_energy = np.mean(energy_profile[start_frame:end_frame])
            
            # Calculate segment duration
            duration = end_time - start_time
            
            # Score based on energy and duration
            # Prefer segments between 20-40 seconds (typical chorus length)
            duration_score = 1.0 - min(abs(duration - 30) / 30, 1.0)
            
            # Combine scores (energy is more important)
            confidence = 0.7 * avg_energy + 0.3 * duration_score
            
            scored_segments.append({
                'start_time': start_time,
                'end_time': end_time,
                'confidence': float(confidence),
                'duration': duration
            })
        
        return scored_segments


class ChorusDetector:
    """Class specifically for detecting chorus/main parts in songs."""
    
    def __init__(self, min_duration: float = 10.0, max_duration: float = 45.0):
        """
        Initialize the chorus detector.
        
        Args:
            min_duration: Minimum duration for a valid chorus in seconds
            max_duration: Maximum duration for a valid chorus in seconds
        """
        self.processor = AudioProcessor()
        self.min_duration = min_duration
        self.max_duration = max_duration
    
    def detect_from_file(self, file_path: str) -> Dict:
        """
        Detect chorus from an audio file.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Dictionary with best chorus segment information
        """
        # Load audio
        audio_data, sr = self.processor.load_audio(file_path)
        
        # Detect chorus
        return self.detect(audio_data, sr)
    
    def detect(self, audio_data: np.ndarray, sr: int) -> Dict:
        """
        Detect chorus from audio data.
        
        Args:
            audio_data: Audio time series
            sr: Sample rate
            
        Returns:
            Dictionary with best chorus segment information
        """
        # Get all potential chorus segments
        segments = self.processor.detect_chorus(audio_data, sr)
        
        # Filter by duration
        valid_segments = [
            s for s in segments 
            if self.min_duration <= s['duration'] <= self.max_duration
        ]
        
        if not valid_segments:
            # If no valid segments, take the highest energy segment
            segments.sort(key=lambda x: x['confidence'], reverse=True)
            best_segment = segments[0]
            
            # Limit to max duration if needed
            if best_segment['duration'] > self.max_duration:
                mid_point = (best_segment['start_time'] + best_segment['end_time']) / 2
                half_max = self.max_duration / 2
                best_segment['start_time'] = mid_point - half_max
                best_segment['end_time'] = mid_point + half_max
                best_segment['duration'] = self.max_duration
        else:
            # Take the highest confidence valid segment
            best_segment = valid_segments[0]
        
        # Extract the audio segment
        segment_audio = self.processor.extract_segment(
            audio_data, sr, best_segment['start_time'], best_segment['end_time']
        )
        
        return {
            'start_time': best_segment['start_time'],
            'end_time': best_segment['end_time'],
            'confidence': best_segment['confidence'],
            'duration': best_segment['duration'],
            'audio_data': segment_audio,
            'sample_rate': sr
        }


def process_audio_file(file_path: str) -> Dict:
    """
    Process an audio file to extract the main/chorus part.
    
    Args:
        file_path: Path to the audio file
        
    Returns:
        Dictionary with processed audio information
    """
    detector = ChorusDetector()
    result = detector.detect_from_file(file_path)
    
    return result
