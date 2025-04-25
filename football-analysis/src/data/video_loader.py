import cv2
import os

def load_video(video_path):
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    video_capture = cv2.VideoCapture(video_path)
    if not video_capture.isOpened():
        raise IOError(f"Cannot open video file: {video_path}")
    
    return video_capture

def extract_frames(video_capture, frame_interval=1):
    frames = []
    frame_count = 0
    
    while True:
        ret, frame = video_capture.read()
        if not ret:
            break
        
        if frame_count % frame_interval == 0:
            frames.append(frame)
        
        frame_count += 1
    
    return frames

def release_video(video_capture):
    video_capture.release()