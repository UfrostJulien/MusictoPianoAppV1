"""
Sheet Music Generation Module - Handles conversion of MIDI to sheet music PDF.
"""

import os
import tempfile
from typing import Dict, List, Optional, Tuple, Union

import mido
from mingus.containers import Note, NoteContainer, Bar, Track, Composition
from mingus.midi.midi_file_in import MIDI_to_Composition
import mingus.extra.lilypond as LilyPond


class SheetMusicError(Exception):
    """Exception raised for errors in the SheetMusic module."""
    pass


class MIDIToMingusConverter:
    """Class for converting MIDI data to Mingus objects."""
    
    def __init__(self):
        """Initialize the MIDI to Mingus converter."""
        pass
    
    def convert_midi_file(self, midi_file: str) -> Composition:
        """
        Convert a MIDI file to a Mingus Composition.
        
        Args:
            midi_file: Path to the MIDI file
            
        Returns:
            Mingus Composition object
        """
        try:
            # Use mingus to convert MIDI to Composition
            composition = MIDI_to_Composition(midi_file)
            return composition
        except Exception as e:
            raise SheetMusicError(f"Failed to convert MIDI to Composition: {str(e)}")
    
    def simplify_composition(self, composition: Composition) -> Composition:
        """
        Simplify a Composition for beginner/intermediate players.
        
        Args:
            composition: Mingus Composition object
            
        Returns:
            Simplified Composition object
        """
        # Create a new composition
        simplified = Composition()
        
        # Process each track
        for track_index, track in enumerate(composition):
            # Create a new track
            new_track = Track()
            
            # Set track name
            if track_index == 0:
                new_track.name = "Right Hand"
            else:
                new_track.name = "Left Hand"
            
            # Process each bar
            for bar in track:
                new_bar = Bar()
                
                # Copy time signature
                new_bar.meter = bar.meter
                
                # Process each beat
                for beat, notes in bar:
                    # Simplify chords if needed
                    if len(notes) > 3:  # If more than 3 notes in a chord
                        # Sort by pitch
                        sorted_notes = sorted(notes, key=lambda n: n.name_octave)
                        
                        # For right hand, keep highest notes (melody)
                        if track_index == 0:
                            notes = sorted_notes[-3:]  # Keep top 3 notes
                        # For left hand, keep lowest notes (bass)
                        else:
                            notes = sorted_notes[:2]  # Keep bottom 2 notes
                    
                    # Add to new bar
                    new_bar.place_notes(notes, beat)
                
                # Add bar to track
                new_track.add_bar(new_bar)
            
            # Add track to composition
            simplified.add_track(new_track)
        
        return simplified


class LilyPondRenderer:
    """Class for rendering sheet music using LilyPond."""
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the LilyPond renderer.
        
        Args:
            output_dir: Directory to save output files. If None, uses a temporary directory.
        """
        self.output_dir = output_dir or tempfile.gettempdir()
        os.makedirs(self.output_dir, exist_ok=True)
    
    def render_composition(self, composition: Composition, title: str, 
                          composer: str = "Unknown", output_file: Optional[str] = None) -> str:
        """
        Render a Composition to a PDF file.
        
        Args:
            composition: Mingus Composition object
            title: Title of the piece
            composer: Composer name
            output_file: Path to save the PDF file. If None, generates a name.
            
        Returns:
            Path to the generated PDF file
        """
        try:
            # Generate LilyPond code
            lily_code = self._generate_lilypond_code(composition, title, composer)
            
            # Determine output file path
            if output_file is None:
                safe_title = "".join(c if c.isalnum() else "_" for c in title)
                output_file = os.path.join(self.output_dir, f"{safe_title}.pdf")
            
            # Create LilyPond file
            lily_file = output_file.replace(".pdf", ".ly")
            with open(lily_file, 'w') as f:
                f.write(lily_code)
            
            # Run LilyPond to generate PDF
            os.system(f"lilypond -o {os.path.splitext(output_file)[0]} {lily_file}")
            
            return output_file
            
        except Exception as e:
            raise SheetMusicError(f"Failed to render sheet music: {str(e)}")
    
    def _generate_lilypond_code(self, composition: Composition, title: str, composer: str) -> str:
        """
        Generate LilyPond code from a Composition.
        
        Args:
            composition: Mingus Composition object
            title: Title of the piece
            composer: Composer name
            
        Returns:
            LilyPond code as string
        """
        # Start with version and header
        lily_code = r"""
\version "2.20.0"

\header {
  title = "%s"
  composer = "%s"
  tagline = "Generated by Music Transcription App"
}

\paper {
  #(set-paper-size "a4")
  top-margin = 15
  bottom-margin = 15
  left-margin = 15
  right-margin = 15
}

\layout {
  \context {
    \Score
    \override SpacingSpanner.base-shortest-duration = #(ly:make-moment 1/16)
  }
}
""" % (title, composer)
        
        # Add right hand part
        if len(composition) > 0:
            right_hand = composition[0]
            lily_code += r"""
rightHand = {
  \clef treble
  \time 4/4
  \key c \major
  \tempo 4 = 120
  
"""
            lily_code += LilyPond.from_Track(right_hand)
            lily_code += r"""
}
"""
        
        # Add left hand part
        if len(composition) > 1:
            left_hand = composition[1]
            lily_code += r"""
leftHand = {
  \clef bass
  \time 4/4
  \key c \major
  
"""
            lily_code += LilyPond.from_Track(left_hand)
            lily_code += r"""
}
"""
        
        # Add piano staff
        lily_code += r"""
\score {
  \new PianoStaff <<
    \new Staff = "right" \rightHand
    \new Staff = "left" \leftHand
  >>
  \layout { }
  \midi { }
}
"""
        
        return lily_code


def generate_sheet_music(midi_file: str, title: str = "Untitled", 
                        composer: str = "Unknown", output_file: Optional[str] = None) -> str:
    """
    Generate sheet music PDF from a MIDI file.
    
    Args:
        midi_file: Path to the MIDI file
        title: Title of the piece
        composer: Composer name
        output_file: Path to save the PDF file
        
    Returns:
        Path to the generated PDF file
    """
    try:
        # Convert MIDI to Mingus Composition
        converter = MIDIToMingusConverter()
        composition = converter.convert_midi_file(midi_file)
        
        # Simplify the composition
        simplified = converter.simplify_composition(composition)
        
        # Render to PDF
        renderer = LilyPondRenderer()
        pdf_file = renderer.render_composition(simplified, title, composer, output_file)
        
        return pdf_file
        
    except Exception as e:
        raise SheetMusicError(f"Failed to generate sheet music: {str(e)}")
