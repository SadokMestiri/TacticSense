import cv2
import numpy as np

def preprocess_frame(frame, target_size=(640, 640)):
    """
    Resize and normalize the input frame.

    Parameters:
    - frame: The input video frame.
    - target_size: The desired size for the frame (default is 640x640).

    Returns:
    - processed_frame: The resized and normalized frame.
    """
    # Resize the frame
    resized_frame = cv2.resize(frame, target_size)

    # Normalize the frame
    normalized_frame = resized_frame / 255.0

    return normalized_frame

def extract_frames(video_path):
    """
    Extract frames from a video file.

    Parameters:
    - video_path: The path to the video file.

    Returns:
    - frames: A list of extracted frames.
    """
    frames = []
    cap = cv2.VideoCapture(video_path)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)

    cap.release()
    return frames