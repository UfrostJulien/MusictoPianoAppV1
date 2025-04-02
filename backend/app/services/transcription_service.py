"""
Transcription service for converting audio to musical notes
"""

import os
import numpy as np
import librosa
import json

def transcribe_audio(audio_file, start_time=None, end_time=None):
    """
    Transcribe audio file to musical notes
    
    Args:
        audio_file (str): Path to audio file
        start_time (float): Start time in seconds (optional)
        end_time (float): End time in seconds (optional)
        
    Returns:
        tuple: (notes, tempo)
            - notes: List of note events with pitch, start_time, duration
            - tempo: Detected tempo in BPM
    """
    # Load audio file
    y, sr = librosa.load(audio_file, sr=None)
    
    # Trim to specified section if provided
    if start_time is not None and end_time is not None:
        start_sample = int(start_time * sr)
        end_sample = int(end_time * sr)
        y = y[start_sample:end_sample]
    
    # Detect tempo
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    
    # Extract pitches using pitch detection
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    
    # Detect note onsets
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr, units='frames')
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)
    
    # Extract notes
    notes = []
    
    for i in range(len(onset_frames)):
        # Get current onset frame
        frame = onset_frames[i]
        
        # Find the highest magnitude pitch at this frame
        index = np.argmax(magnitudes[:, frame])
        pitch = pitches[index, frame]
        
        # Skip if no pitch detected
        if pitch == 0:
            continue
        
        # Convert frequency to MIDI note number
        midi_note = round(librosa.hz_to_midi(pitch))
        
        # Calculate duration (until next onset or end of audio)
        if i < len(onset_frames) - 1:
            duration = onset_times[i + 1] - onset_times[i]
        else:
            duration = (len(y) / sr) - onset_times[i]
        
        # Add note to list
        notes.append({
            'pitch': int(midi_note),
            'start_time': float(onset_times[i]),
            'duration': float(duration)
        })
    
    return notes, float(tempo)

def detect_chorus(audio_file):
    """
    Detect the chorus/main part of a song
    
    Args:
        audio_file (str): Path to audio file
        
    Returns:
        tuple: (start_time, end_time) in seconds
    """
    # Load audio file
    y, sr = librosa.load(audio_file, sr=None)
    
    # Compute chromagram
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    
    # Compute similarity matrix
    S = librosa.segment.recurrence_matrix(chroma, mode='affinity')
    
    # Find repeated sections (potential choruses)
    segments = librosa.segment.agglomerative(S, len(S))
    
    # Count occurrences of each segment
    segment_counts = np.bincount(segments)
    
    # Find the most common segment (likely the chorus)
    most_common_segment = np.argmax(segment_counts)
    
    # Find all frames belonging to this segment
    chorus_frames = np.where(segments == most_common_segment)[0]
    
    # Convert to time
    chorus_times = librosa.frames_to_time(chorus_frames, sr=sr)
    
    # Find the longest continuous section
    if len(chorus_times) > 0:
        # Group consecutive frames
        diffs = np.diff(chorus_frames)
        breaks = np.where(diffs > 1)[0]
        
        if len(breaks) > 0:
            # Find the longest section
            section_lengths = np.diff(np.concatenate(([0], breaks + 1, [len(chorus_frames)])))
            longest_section = np.argmax(section_lengths)
            
            if longest_section == 0:
                start_idx = 0
                end_idx = breaks[0] + 1
            elif longest_section == len(section_lengths) - 1:
                start_idx = breaks[-1] + 1
                end_idx = len(chorus_frames)
            else:
                start_idx = breaks[longest_section - 1] + 1
                end_idx = breaks[longest_section] + 1
            
            start_time = chorus_times[start_idx]
            end_time = chorus_times[end_idx - 1]
        else:
            # Only one continuous section
            start_time = chorus_times[0]
            end_time = chorus_times[-1]
    else:
        # Fallback: use middle section of the song
        total_duration = len(y) / sr
        start_time = total_duration * 0.4
        end_time = total_duration * 0.6
    
    # Ensure minimum duration (10 seconds)
    if end_time - start_time < 10:
        mid_point = (start_time + end_time) / 2
        start_time = max(0, mid_point - 5)
        end_time = min(len(y) / sr, mid_point + 5)
    
    return float(start_time), float(end_time)

def simplify_arrangement(notes, difficulty='beginner'):
    """
    Simplify note arrangement based on difficulty level
    
    Args:
        notes (list): List of note events
        difficulty (str): Difficulty level ('beginner', 'intermediate', 'advanced')
        
    Returns:
        dict: Simplified arrangement with right_hand and left_hand notes
    """
    # Sort notes by pitch
    sorted_notes = sorted(notes, key=lambda x: x['pitch'])
    
    # Find median pitch to separate hands
    pitches = [note['pitch'] for note in notes]
    median_pitch = np.median(pitches) if pitches else 60  # Default to middle C
    
    # Separate notes into right and left hand
    right_hand = []
    left_hand = []
    
    for note in notes:
        if note['pitch'] >= median_pitch:
            right_hand.append(note)
        else:
            left_hand.append(note)
    
    # Apply simplification based on difficulty
    if difficulty == 'beginner':
        # For beginners, keep only the melody in the right hand
        # and simple bass notes in the left hand
        right_hand = extract_melody(right_hand)
        left_hand = extract_bass_line(left_hand)
    
    elif difficulty == 'intermediate':
        # For intermediate, keep melody and some harmony in right hand
        # and basic chord patterns in left hand
        right_hand = extract_melody_with_harmony(right_hand)
        left_hand = extract_chord_pattern(left_hand)
    
    # Advanced keeps all notes
    
    return {
        'right_hand': right_hand,
        'left_hand': left_hand
    }

def extract_melody(notes):
    """Extract the main melody from a set of notes"""
    # Sort by start time
    sorted_notes = sorted(notes, key=lambda x: x['start_time'])
    
    # Simple algorithm: keep the highest pitch at each onset time
    melody = []
    current_onset = -1
    
    for note in sorted_notes:
        # Round to nearest 10ms to group notes at similar onset times
        onset = round(note['start_time'] * 100) / 100
        
        if onset != current_onset:
            # New onset time, add this note
            melody.append(note)
            current_onset = onset
        else:
            # Same onset time, keep the higher pitch
            if note['pitch'] > melody[-1]['pitch']:
                melody[-1] = note
    
    return melody

def extract_bass_line(notes):
    """Extract a simple bass line from a set of notes"""
    # Sort by start time
    sorted_notes = sorted(notes, key=lambda x: x['start_time'])
    
    # Simple algorithm: keep the lowest pitch at each beat
    bass_line = []
    current_beat = -1
    
    for note in sorted_notes:
        # Round to nearest quarter note (assuming 4/4 time)
        beat = int(note['start_time'] * 4) / 4
        
        if beat != current_beat:
            # New beat, add this note
            bass_line.append(note)
            current_beat = beat
        else:
            # Same beat, keep the lower pitch
            if note['pitch'] < bass_line[-1]['pitch']:
                bass_line[-1] = note
    
    return bass_line

def extract_melody_with_harmony(notes):
    """Extract melody with some harmony notes"""
    # First get the main melody
    melody = extract_melody(notes)
    
    # Add some harmony notes (thirds, sixths)
    harmony = []
    
    for note in notes:
        # Check if this note forms a third or sixth with any melody note
        for mel_note in melody:
            # Notes at the same time
            if abs(note['start_time'] - mel_note['start_time']) < 0.1:
                interval = abs(note['pitch'] - mel_note['pitch'])
                # Major/minor third or sixth
                if interval in [3, 4, 8, 9] and note != mel_note:
                    harmony.append(note)
                    break
    
    # Combine melody and harmony
    result = melody + harmony
    
    # Sort by start time
    result.sort(key=lambda x: x['start_time'])
    
    return result

def extract_chord_pattern(notes):
    """Extract a chord pattern from a set of notes"""
    # Sort by start time
    sorted_notes = sorted(notes, key=lambda x: x['start_time'])
    
    # Group notes by beat
    beat_groups = {}
    
    for note in sorted_notes:
        # Round to nearest quarter note
        beat = int(note['start_time'] * 4) / 4
        
        if beat not in beat_groups:
            beat_groups[beat] = []
        
        beat_groups[beat].append(note)
    
    # For each beat, keep root and fifth (simple chord pattern)
    chord_pattern = []
    
    for beat, beat_notes in sorted(beat_groups.items()):
        if not beat_notes:
            continue
        
        # Sort by pitch
        beat_notes.sort(key=lambda x: x['pitch'])
        
        # Always keep the lowest note (root)
        chord_pattern.append(beat_notes[0])
        
        # If there are more notes, try to find a fifth
        if len(beat_notes) > 1:
            for note in beat_notes[1:]:
                if (note['pitch'] - beat_notes[0]['pitch']) % 12 == 7:
                    # Perfect fifth
                    chord_pattern.append(note)
                    break
    
    return chord_pattern
