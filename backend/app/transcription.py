"""
Transcription Module - Handles melody extraction and MIDI conversion.
"""

import os
import tempfile
import numpy as np
from typing import Dict, List, Optional, Tuple, Union

from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH
import mido
from mido import Message, MidiFile, MidiTrack, MetaMessage


class TranscriptionError(Exception):
    """Exception raised for errors in the Transcription module."""
    pass


class MelodyExtractor:
    """Class for extracting melody from audio using Basic Pitch."""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the melody extractor.
        
        Args:
            model_path: Path to the Basic Pitch model. If None, uses default.
        """
        self.model_path = model_path or ICASSP_2022_MODEL_PATH
    
    def extract_melody(self, audio_data: np.ndarray, sr: int, 
                       min_frequency: float = 50.0, 
                       max_frequency: float = 1000.0) -> Dict:
        """
        Extract melody from audio data.
        
        Args:
            audio_data: Audio time series
            sr: Sample rate
            min_frequency: Minimum frequency to consider (Hz)
            max_frequency: Maximum frequency to consider (Hz)
            
        Returns:
            Dictionary containing:
                - model_output: Raw model output
                - midi_data: MIDI data
                - note_events: List of note events
        """
        try:
            # Save audio to temporary file (Basic Pitch requires a file path)
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, "temp_audio.wav")
            
            import soundfile as sf
            sf.write(temp_file, audio_data, sr)
            
            # Extract melody using Basic Pitch
            # Updated to match current Basic Pitch API
            model_output, midi_data, note_events = predict(
                temp_file,
                onset_threshold=0.5,
                frame_threshold=0.3
            )
            
            # Clean up temporary file
            os.remove(temp_file)
            
            return {
                'model_output': model_output,
                'midi_data': midi_data,
                'note_events': note_events
            }
            
        except Exception as e:
            raise TranscriptionError(f"Failed to extract melody: {str(e)}")


class PianoArrangementSimplifier:
    """Class for simplifying arrangements for piano."""
    
    def __init__(self, max_polyphony_right: int = 3, max_polyphony_left: int = 2):
        """
        Initialize the arrangement simplifier.
        
        Args:
            max_polyphony_right: Maximum simultaneous notes for right hand
            max_polyphony_left: Maximum simultaneous notes for left hand
        """
        self.max_polyphony_right = max_polyphony_right
        self.max_polyphony_left = max_polyphony_left
    
    def simplify_arrangement(self, note_events: List[Dict]) -> List[Dict]:
        """
        Simplify the arrangement for beginner/intermediate piano players.
        
        Args:
            note_events: List of note events from Basic Pitch
            
        Returns:
            List of simplified note events
        """
        if not note_events:
            return []
        
        # Sort notes by start time
        sorted_notes = sorted(note_events, key=lambda x: x['start_time'])
        
        # Assign notes to right or left hand based on pitch
        right_hand_notes = []
        left_hand_notes = []
        
        for note in sorted_notes:
            # Higher notes go to right hand, lower to left
            if note['pitch'] >= 60:  # Middle C and above
                right_hand_notes.append(note)
            else:
                left_hand_notes.append(note)
        
        # Simplify each hand
        simplified_right = self._simplify_hand(right_hand_notes, self.max_polyphony_right, is_right_hand=True)
        simplified_left = self._simplify_hand(left_hand_notes, self.max_polyphony_left, is_right_hand=False)
        
        # Combine and sort by start time
        simplified = simplified_right + simplified_left
        simplified.sort(key=lambda x: x['start_time'])
        
        return simplified
    
    def _simplify_hand(self, notes: List[Dict], max_polyphony: int, is_right_hand: bool) -> List[Dict]:
        """
        Simplify notes for one hand.
        
        Args:
            notes: List of note events
            max_polyphony: Maximum simultaneous notes
            is_right_hand: Whether this is the right hand
            
        Returns:
            List of simplified note events
        """
        if not notes:
            return []
        
        # Group notes by start time
        notes_by_time = {}
        for note in notes:
            start_time = note['start_time']
            if start_time not in notes_by_time:
                notes_by_time[start_time] = []
            notes_by_time[start_time].append(note)
        
        # Simplify each group
        simplified_notes = []
        for start_time, note_group in notes_by_time.items():
            # If we have more notes than allowed, keep only the most important ones
            if len(note_group) > max_polyphony:
                # For right hand, prioritize highest notes (melody)
                if is_right_hand:
                    # Sort by pitch (descending) and keep top notes
                    note_group.sort(key=lambda x: x['pitch'], reverse=True)
                    selected_notes = note_group[:max_polyphony]
                # For left hand, keep root notes for harmony
                else:
                    # Sort by pitch (ascending) and keep bottom notes
                    note_group.sort(key=lambda x: x['pitch'])
                    selected_notes = note_group[:max_polyphony]
            else:
                selected_notes = note_group
            
            simplified_notes.extend(selected_notes)
        
        # Add hand information to notes
        for note in simplified_notes:
            note['hand'] = 'right' if is_right_hand else 'left'
        
        return simplified_notes


class MIDIGenerator:
    """Class for generating MIDI files from note events."""
    
    def __init__(self, tempo: int = 120):
        """
        Initialize the MIDI generator.
        
        Args:
            tempo: Tempo in BPM
        """
        self.tempo = tempo
    
    def create_midi(self, note_events: List[Dict], output_file: str) -> None:
        """
        Create a MIDI file from note events.
        
        Args:
            note_events: List of note events
            output_file: Path to save the MIDI file
            
        Returns:
            None
        """
        try:
            # Create MIDI file with two tracks (right and left hand)
            mid = MidiFile()
            right_track = MidiTrack()
            left_track = MidiTrack()
            mid.tracks.append(right_track)
            mid.tracks.append(left_track)
            
            # Add tempo
            tempo_in_microseconds = mido.bpm2tempo(self.tempo)
            right_track.append(MetaMessage('set_tempo', tempo=tempo_in_microseconds, time=0))
            
            # Add time signature (4/4)
            right_track.append(MetaMessage('time_signature', numerator=4, denominator=4, time=0))
            
            # Add track names
            right_track.append(MetaMessage('track_name', name='Right Hand', time=0))
            left_track.append(MetaMessage('track_name', name='Left Hand', time=0))
            
            # Sort notes by start time
            sorted_notes = sorted(note_events, key=lambda x: x['start_time'])
            
            # Separate notes by hand
            right_hand_notes = [n for n in sorted_notes if n.get('hand', 'right') == 'right']
            left_hand_notes = [n for n in sorted_notes if n.get('hand', 'left') == 'left']
            
            # Convert to MIDI events
            self._add_notes_to_track(right_hand_notes, right_track)
            self._add_notes_to_track(left_hand_notes, left_track)
            
            # Save MIDI file
            mid.save(output_file)
            
        except Exception as e:
            raise TranscriptionError(f"Failed to create MIDI file: {str(e)}")
    
    def _add_notes_to_track(self, notes: List[Dict], track: MidiTrack) -> None:
        """
        Add notes to a MIDI track.
        
        Args:
            notes: List of note events
            track: MIDI track to add notes to
            
        Returns:
            None
        """
        if not notes:
            return
        
        # Convert seconds to ticks
        ticks_per_beat = 480  # Standard MIDI resolution
        ticks_per_second = ticks_per_beat * self.tempo / 60
        
        # Sort by start time
        notes.sort(key=lambda x: x['start_time'])
        
        # Add note events
        last_time = 0
        for note in notes:
            # Calculate timings in ticks
            start_time_ticks = int(note['start_time'] * ticks_per_second)
            end_time_ticks = int(note['end_time'] * ticks_per_second)
            duration_ticks = end_time_ticks - start_time_ticks
            
            # Calculate delta time (time since last event)
            delta_time = start_time_ticks - last_time
            
            # Add note on event
            track.append(Message('note_on', note=note['pitch'], velocity=64, time=delta_time))
            
            # Update last time
            last_time = start_time_ticks
            
            # Add note off event
            track.append(Message('note_off', note=note['pitch'], velocity=64, time=duration_ticks))
            
            # Update last time
            last_time = end_time_ticks


def transcribe_audio(audio_data: np.ndarray, sr: int, output_midi_file: Optional[str] = None) -> Dict:
    """
    Transcribe audio to MIDI.
    
    Args:
        audio_data: Audio time series
        sr: Sample rate
        output_midi_file: Path to save MIDI file (optional)
        
    Returns:
        Dictionary with transcription results
    """
    try:
        # Extract melody
        extractor = MelodyExtractor()
        melody_result = extractor.extract_melody(audio_data, sr)
        
        # Simplify arrangement
        simplifier = PianoArrangementSimplifier()
        simplified_notes = simplifier.simplify_arrangement(melody_result['note_events'])
        
        # Generate MIDI if output file is specified
        if output_midi_file:
            generator = MIDIGenerator()
            generator.create_midi(simplified_notes, output_midi_file)
        
        return {
            'note_events': simplified_notes,
            'midi_data': melody_result['midi_data'] if not output_midi_file else output_midi_file
        }
        
    except Exception as e:
        raise TranscriptionError(f"Failed to transcribe audio: {str(e)}")
