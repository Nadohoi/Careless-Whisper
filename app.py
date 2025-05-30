from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
import os
import torch
import webbrowser
from faster_whisper import WhisperModel
from datetime import timedelta
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Get parameters from form
    model_size = request.form.get('model', 'tiny')
    device_type = request.form.get('device', 'cpu')
    
    # Process with Whisper
    try:
        # Check if CUDA is available for GPU processing
        if device_type == 'gpu' and not torch.cuda.is_available():
            device_type = 'cpu'
            compute_type = 'int8'
        else:
            compute_type = 'float16' if device_type == 'gpu' else 'int8'
        
        # Convert 'gpu' to 'cuda' for Whisper model
        device = 'cuda' if device_type == 'gpu' else 'cpu'
        
        # Save the file to a temporary location in memory
        import tempfile
        import shutil
        
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, file.filename)
        
        try:
            # Save the file to the temporary location
            file.save(temp_file_path)
            
            # Initialize the model and transcribe
            model = WhisperModel(model_size, device=device, compute_type=compute_type)
            segments, info = model.transcribe(temp_file_path, beam_size=3)
        finally:
            # Clean up the temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Format results
        results = []
        srt_content = []
        
        for segment in segments:
            start_time = str(timedelta(seconds=int(segment.start))) + ',000'
            end_time = str(timedelta(seconds=int(segment.end))) + ',000'
            text = segment.text.strip()
            
            segment_info = {
                'id': segment.id + 1,
                'start': start_time,
                'end': end_time,
                'text': text
            }
            
            results.append(segment_info)
            
            # Create SRT format entry
            srt_entry = f"{segment.id + 1}\n{start_time} --> {end_time}\n{text}\n\n"
            srt_content.append(srt_entry)
        
        # Prepare SRT content as string
        srt_content_str = ''.join(srt_content)
        
        # Generate a unique ID for this session
        import uuid
        session_id = str(uuid.uuid4())
        
        # Store SRT content in memory (in a real app, you might want to use a proper cache)
        if not hasattr(app, 'srt_cache'):
            app.srt_cache = {}
        
        output_filename = os.path.splitext(file.filename)[0] + '.srt'
        app.srt_cache[session_id] = {
            'content': srt_content_str,
            'filename': output_filename
        }
        
        return jsonify({
            'success': True,
            'language': info.language,
            'language_probability': round(info.language_probability, 2),
            'segments': results,
            'session_id': session_id,
            'srt_filename': output_filename
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<session_id>')
def download_file(session_id):
    # Get SRT content from cache
    if not hasattr(app, 'srt_cache') or session_id not in app.srt_cache:
        return jsonify({'error': 'Session expired or invalid'}), 404
    
    srt_data = app.srt_cache[session_id]
    srt_content = srt_data['content']
    filename = srt_data['filename']
    
    # Create a bytes-like object in memory with UTF-8 encoding
    srt_bytes = srt_content.encode('utf-8')
    srt_io = BytesIO(srt_bytes)
    
    # Send the file directly from memory with proper encoding
    response = send_file(
        srt_io,
        as_attachment=True,
        download_name=filename,
        mimetype='text/plain; charset=utf-8'
    )
    
    # Set content disposition to force download
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

if __name__ == '__main__':
    # Remove problematic DLL if it exists (carried over from original code)
    dll_path = r'labbase\Library\bin\libiomp5md.dll'
    if os.path.exists(dll_path):
        os.remove(dll_path)
    
    # Initialize SRT cache
    app.srt_cache = {}
    
    webbrowser.open('http://127.0.0.1:5000')
    
    app.run(debug=False)
