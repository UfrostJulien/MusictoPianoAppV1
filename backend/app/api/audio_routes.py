"""
Audio routes for the API
"""

import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
# Fix import path to use correct module structure
from app.services.audio_service import download_youtube_audio, process_audio_file
from app.utils.validators import validate_youtube_url, allowed_file

# Create blueprint
bp = Blueprint('audio', __name__, url_prefix='/api/audio')

@bp.route('/youtube', methods=['POST'])
def process_youtube():
    """Process YouTube URL to extract audio"""
    
    # Get JSON data
    data = request.get_json()
    
    # Validate input
    if not data or 'url' not in data:
        return jsonify({'error': 'Missing URL parameter'}), 400
    
    url = data['url']
    
    if not validate_youtube_url(url):
        return jsonify({'error': 'Invalid YouTube URL'}), 400
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Create job directory
    job_dir = os.path.join(current_app.config['RESULTS_FOLDER'], job_id)
    os.makedirs(job_dir, exist_ok=True)
    
    try:
        # Download YouTube audio (this would be a Celery task in production)
        audio_file = download_youtube_audio(url, job_dir)
        
        # Process audio file
        process_audio_file(audio_file, job_dir)
        
        return jsonify({
            'job_id': job_id,
            'status': 'processing',
            'message': 'YouTube audio extraction started'
        }), 202
    
    except Exception as e:
        return jsonify({
            'error': 'Failed to process YouTube URL',
            'message': str(e)
        }), 500

@bp.route('/upload', methods=['POST'])
def upload_audio():
    """Upload audio file for processing"""
    
    # Check if file is in request
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    
    # Check if file is empty
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check if file is allowed
    if not allowed_file(file.filename, {'mp3', 'wav', 'ogg', 'flac', 'm4a'}):
        return jsonify({'error': 'File type not allowed'}), 400
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Create job directory
    job_dir = os.path.join(current_app.config['RESULTS_FOLDER'], job_id)
    os.makedirs(job_dir, exist_ok=True)
    
    try:
        # Save file
        filename = secure_filename(file.filename)
        file_path = os.path.join(job_dir, filename)
        file.save(file_path)
        
        # Process audio file
        process_audio_file(file_path, job_dir)
        
        return jsonify({
            'job_id': job_id,
            'status': 'processing',
            'message': 'Audio file uploaded and processing started'
        }), 202
    
    except Exception as e:
        return jsonify({
            'error': 'Failed to process audio file',
            'message': str(e)
        }), 500

@bp.route('/status/<job_id>', methods=['GET'])
def get_status(job_id):
    """Get status of audio processing job"""
    
    # Check if job directory exists
    job_dir = os.path.join(current_app.config['RESULTS_FOLDER'], job_id)
    
    if not os.path.exists(job_dir):
        return jsonify({'error': 'Job not found'}), 404
    
    # Check for status file (in a real implementation, this would query Celery)
    status_file = os.path.join(job_dir, 'status.txt')
    
    if os.path.exists(status_file):
        with open(status_file, 'r') as f:
            status = f.read().strip()
    else:
        status = 'processing'
    
    return jsonify({
        'job_id': job_id,
        'status': status
    }), 200
