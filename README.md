# Careless Whisper - Web Version

This is a web-based version of the Careless Whisper audio transcription tool that uses OpenAI's Whisper model for transcription.

## Features

- Transcribe audio and video files to text
- Support for different Whisper model sizes (tiny, medium, large-v3)
- CPU and GPU processing options
- SRT file format output
- Modern web interface

## Requirements

- Python 3.6+
- Required Python packages (install via `pip install -r requirements.txt`):
  - torch
  - faster-whisper
  - flask

## Setup and Running

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the Flask application:
   ```
   python app.py
   ```

3. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

4. Use the interface to:
   - Select a model size (tiny, medium, large-v3)
   - Choose processing device (CPU or GPU)
   - Upload an audio/video file
   - Click "Transform!" to transcribe
   - Download the resulting SRT file

## Notes

- GPU processing requires CUDA to be properly installed on your system
- For large files, the transcription process may take some time
- The web version automatically creates directories for uploads and outputs

## Credits

Programmed with ❤️ by Reiii & Supported by OpenAI Whisper Model
