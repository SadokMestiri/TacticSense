# Configuration settings for the football analysis project

import os

# Get the absolute path to the project root directory
def get_project_root():
    """Returns the absolute path to the project root directory"""
    current_file = os.path.abspath(__file__)
    utils_dir = os.path.dirname(current_file)
    src_dir = os.path.dirname(utils_dir)
    return os.path.dirname(src_dir)

# Paths
BASE_DIR = get_project_root()
VIDEO_DIR = os.path.join(BASE_DIR, 'input_videos')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'yolov8_weights.pt')

# Create directories if they don't exist
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

# Model parameters
CONFIDENCE_THRESHOLD = 0.5
NMS_THRESHOLD = 0.4

# Heatmap parameters
HEATMAP_RESOLUTION = (640, 480)  # Width, Height
HEATMAP_COLOR_MAP = 'hot'  # Color map for heatmap visualization

# Frame processing parameters
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FRAME_RATE = 30  # Frames per second for video processing

# Team colors for classification (example values)
TEAM_A_COLOR = [255, 0, 0]  # Red
TEAM_B_COLOR = [0, 0, 255]  # Blue

# Video paths
# This can be overridden by the user
VIDEO_PATH = os.path.join(VIDEO_DIR, 'sample.mp4')

# Other settings
DEBUG_MODE = True  # Set to True to enable debug logs