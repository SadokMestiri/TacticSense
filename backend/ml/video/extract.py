import subprocess
import os
import tempfile

def extract_audio(video_path, output_path=None):
    """Extract audio from video file using FFmpeg"""
    if output_path is None:
        # Create a temporary WAV file
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, f"{os.path.basename(video_path)}.wav")
    
    # Use FFmpeg to extract audio
    command = [
        "ffmpeg", "-i", video_path,
        "-vn",  # No video
        "-acodec", "pcm_s16le",  # PCM 16-bit little-endian format
        "-ar", "16000",  # 16kHz sample rate (good for Whisper)
        "-ac", "1",  # Mono channel
        "-y",  # Overwrite output file if it exists
        output_path
    ]
    
    subprocess.run(command, check=True)
    return output_path