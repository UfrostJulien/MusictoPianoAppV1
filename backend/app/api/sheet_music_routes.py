"""
Sheet music routes for the API
"""

import os
import json
import subprocess
from flask import Blueprint, request, jsonify, current_app, send_from_directory
# Fix import path to use correct module structure
from app.services.sheet_music_service import generate_sheet_music, create_preview_image

# Create blueprint
bp = Blueprint('sheet_music', __name__, url_prefix='/api/sheet-music')

@bp.route('/generate', methods=['POST'])
def create_sheet_music():
    """Generate sheet music from transcription"""
    
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
    
    # Check for transcription file
    transcription_file = os.path.join(job_dir, 'transcription.json')
    
    if not os.path.exists(transcription_file):
        return jsonify({'error': 'Transcription not found'}), 404
    
    try:
        # Read transcription
        with open(transcription_file, 'r') as f:
            transcription = json.load(f)
        
        # Generate sheet music
        title = options.get('title', 'Transcribed Music')
        composer = options.get('composer', 'Music Transcription App')
        difficulty = options.get('difficulty', 'beginner')
        include_chords = options.get('include_chords', True)
        
        lily_file, pdf_file = generate_sheet_music(
            transcription['notes'],
            transcription['tempo'],
            job_dir,
            title=title,
            composer=composer,
            difficulty=difficulty,
            include_chords=include_chords
        )
        
        # Create preview image
        preview_file = create_preview_image(pdf_file, job_dir)
        
        # Update status
        with open(os.path.join(job_dir, 'status.txt'), 'w') as f:
            f.write('completed')
        
        return jsonify({
            'job_id': job_id,
            'status': 'completed',
            'message': 'Sheet music generation completed',
            'files': {
                'lily': os.path.basename(lily_file),
                'pdf': os.path.basename(pdf_file),
                'preview': os.path.basename(preview_file)
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Failed to generate sheet music',
            'message': str(e)
        }), 500

@bp.route('/download/pdf/<job_id>', methods=['GET'])
def download_pdf(job_id):
    """Download PDF sheet music"""
    
    # Check if job directory exists
    job_dir = os.path.join(current_app.config['RESULTS_FOLDER'], job_id)
    
    if not os.path.exists(job_dir):
        return jsonify({'error': 'Job not found'}), 404
    
    # Find PDF file
    pdf_files = [f for f in os.listdir(job_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        return jsonify({'error': 'PDF file not found'}), 404
    
    return send_from_directory(
        job_dir,
        pdf_files[0],
        as_attachment=True,
        download_name=f'sheet_music_{job_id}.pdf'
    )

@bp.route('/preview/<job_id>', methods=['GET'])
def get_preview(job_id):
    """Get preview image of sheet music"""
    
    # Check if job directory exists
    job_dir = os.path.join(current_app.config['RESULTS_FOLDER'], job_id)
    
    if not os.path.exists(job_dir):
        return jsonify({'error': 'Job not found'}), 404
    
    # Find preview image
    preview_files = [f for f in os.listdir(job_dir) if f.endswith('_preview.png')]
    
    if not preview_files:
        return jsonify({'error': 'Preview image not found'}), 404
    
    return send_from_directory(
        job_dir,
        preview_files[0],
        mimetype='image/png'
    )
