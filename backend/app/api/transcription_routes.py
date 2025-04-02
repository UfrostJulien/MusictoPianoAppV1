"""
Transcription routes for the API
"""

import os
import json
from flask import Blueprint, request, jsonify, current_app
# Fix import path to use correct module structure
from app.services.transcription_service import transcribe_audio, detect_chorus, simplify_arrangement

# Create blueprint
bp = Blueprint('transcription', __name__, url_prefix='/api/transcription')

@bp.route('/create', methods=['POST'])
def create_transcription():
    """Create transcription from processed audio"""
    
    # Get JSON data
    data = request.get_json()
    
    # Validate input
    if not data or 'job_id' not in data:
        return jsonify({'error': 'Missing job_id parameter'}), 400
    
    job_id = data['job_id']
    options = data.get('options', {})
    
    # Check if job directory exists
    job_dir = os.path.join(current_app.config['RESULTS_FOLDER'], job_id)
    
    if not os.path.exists(job_dir):
        return jsonify({'error': 'Job not found'}), 404
    
    try:
        # Find processed audio file
        audio_files = [f for f in os.listdir(job_dir) if f.endswith(('.wav', '.mp3', '.ogg', '.flac', '.m4a'))]
        
        if not audio_files:
            return jsonify({'error': 'No processed audio file found'}), 404
        
        audio_file = os.path.join(job_dir, audio_files[0])
        
        # Detect chorus if requested
        if options.get('detect_chorus_only', True):
            chorus_start, chorus_end = detect_chorus(audio_file)
            
            # Save chorus information
            with open(os.path.join(job_dir, 'chorus_info.json'), 'w') as f:
                json.dump({
                    'start_time': chorus_start,
                    'end_time': chorus_end
                }, f)
        else:
            chorus_start, chorus_end = None, None
        
        # Transcribe audio
        notes, tempo = transcribe_audio(
            audio_file, 
            start_time=chorus_start, 
            end_time=chorus_end
        )
        
        # Simplify arrangement if requested
        if options.get('simplify_arrangement', True):
            difficulty = options.get('difficulty', 'beginner')
            notes = simplify_arrangement(notes, difficulty)
        
        # Save transcription
        with open(os.path.join(job_dir, 'transcription.json'), 'w') as f:
            json.dump({
                'notes': notes,
                'tempo': tempo
            }, f)
        
        # Update status
        with open(os.path.join(job_dir, 'status.txt'), 'w') as f:
            f.write('transcribed')
        
        return jsonify({
            'job_id': job_id,
            'status': 'transcribed',
            'message': 'Audio transcription completed'
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Failed to transcribe audio',
            'message': str(e)
        }), 500

@bp.route('/<job_id>', methods=['GET'])
def get_transcription(job_id):
    """Get transcription for a job"""
    
    # Check if job directory exists
    job_dir = os.path.join(current_app.config['RESULTS_FOLDER'], job_id)
    
    if not os.path.exists(job_dir):
        return jsonify({'error': 'Job not found'}), 404
    
    # Check for transcription file
    transcription_file = os.path.join(job_dir, 'transcription.json')
    
    if not os.path.exists(transcription_file):
        return jsonify({'error': 'Transcription not found'}), 404
    
    # Read transcription
    with open(transcription_file, 'r') as f:
        transcription = json.load(f)
    
    return jsonify({
        'job_id': job_id,
        'transcription': transcription
    }), 200
