import os
import subprocess
import tempfile

def overlay_subtitles(video_path, srt_path, output_path=None):
    """Overlay SRT subtitles onto a video using FFmpeg"""
    if output_path is None:
        filename, ext = os.path.splitext(os.path.basename(video_path))
        output_path = os.path.join(os.path.dirname(video_path), f"{filename}_subtitled{ext}")
    
    # FFmpeg command to overlay subtitles
    command = [
        "ffmpeg",
        "-i", video_path,
        "-vf", f"subtitles={srt_path}:force_style='FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BackColour=&H80000000,BorderStyle=4'",
        "-c:a", "copy",
        "-y",
        output_path
    ]
    
    subprocess.run(command, check=True)
    return output_path

def overlay_subtitles_with_style(video_path, srt_path, output_path=None, 
                                font_size=24, position="bottom", color="white"):
    """Overlay SRT subtitles with custom styling"""
    if output_path is None:
        filename, ext = os.path.splitext(os.path.basename(video_path))
        output_path = os.path.join(os.path.dirname(video_path), f"{filename}_styled{ext}")
    
    # Color mapping
    color_map = {
        "white": "&H00FFFFFF",
        "yellow": "&H0000FFFF",
        "green": "&H0000FF00",
        "red": "&H000000FF"
    }
    
    # Position mapping
    position_map = {
        "bottom": "10",
        "top": "90",
        "middle": "50"
    }
    
    # Set color and position
    color_value = color_map.get(color.lower(), "&H00FFFFFF")
    pos_value = position_map.get(position.lower(), "10")
    
    # FFmpeg command with advanced styling
    command = [
        "ffmpeg",
        "-i", video_path,
        "-vf", f"subtitles={srt_path}:force_style='FontSize={font_size},PrimaryColour={color_value},OutlineColour=&H00000000,BackColour=&H80000000,BorderStyle=4,Alignment={pos_value}'",
        "-c:a", "copy",
        "-y",
        output_path
    ]
    
    subprocess.run(command, check=True)
    return output_path