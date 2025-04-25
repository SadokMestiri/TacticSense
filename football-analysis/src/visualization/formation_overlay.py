import numpy as np
import os
import sys

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import OpenCV with error handling
try:
    import cv2
except ImportError:
    print("Error importing OpenCV. Make sure it's installed properly.")
    # Create a stub for cv2 if it can't be imported
    class CV2Stub:
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
        
        def circle(self, img, center, radius, color, thickness=1, lineType=8, shift=0):
            """Stub for cv2.circle"""
            pass
            
        def rectangle(self, img, pt1, pt2, color, thickness=1, lineType=8, shift=0):
            """Stub for cv2.rectangle"""
            pass
            
        def line(self, img, pt1, pt2, color, thickness=1, lineType=8, shift=0):
            """Stub for cv2.line"""
            pass
            
        def VideoCapture(self, *args, **kwargs):
            class DummyCapture:
                def isOpened(self):
                    return False
                def read(self):
                    return False, None
                def release(self):
                    pass
                def get(self, propId):
                    return 0
            return DummyCapture()
            
        def VideoWriter_fourcc(self, *args):
            """Stub for cv2.VideoWriter_fourcc"""
            return 0
            
        def VideoWriter(self, filename, fourcc, fps, frameSize, isColor=True):
            """Stub for cv2.VideoWriter"""
            class DummyWriter:
                def write(self, img):
                    pass
                def release(self):
                    pass
            return DummyWriter()
    cv2 = CV2Stub()

# Define constants that might be missing
CAP_PROP_FRAME_WIDTH = 3
CAP_PROP_FRAME_HEIGHT = 4
CAP_PROP_FPS = 5
CAP_PROP_POS_FRAMES = 1

# Import local modules with error handling
try:
    from src.utils.helpers import get_team_color
except ImportError:
    print("Error importing helpers module. Using fallback.")
    def get_team_color(team_label):
        """Fallback team color function."""
        if team_label == 'Team A':
            return (255, 0, 0)  # Red
        elif team_label == 'Team B':
            return (0, 0, 255)  # Blue
        return (255, 255, 255)  # Default to white

def overlay_formation(frame, player_positions):
    """
    Draws the formation overlay on the given frame for all teams.

    Parameters:
    - frame: The video frame on which to draw.
    - player_positions: A list of dictionaries containing player positions with 'x', 'y', and 'team' keys.

    Returns:
    - Annotated frame with formation overlay.
    """
    # Create a copy of the frame to avoid modifying the original
    annotated_frame = frame.copy() if hasattr(frame, 'copy') else frame
    
    # Group positions by team
    team_positions = {}
    for pos in player_positions:
        team = pos.get('team', 'unknown')
        if team not in team_positions:
            team_positions[team] = []
        team_positions[team].append((pos['x'], pos['y']))
    
    # Draw formations for each team
    for team_label, positions in team_positions.items():
        annotated_frame = draw_formation(annotated_frame, positions, team_label)
    
    return annotated_frame

def draw_formation(frame, player_positions, team_label):
    """
    Draws the formation overlay for a specific team on the given frame.

    Parameters:
    - frame: The video frame on which to draw.
    - player_positions: A list of tuples containing player positions (x, y).
    - team_label: The label of the team ('Team A' or 'Team B').

    Returns:
    - Annotated frame with formation overlay for the team.
    """
    color = get_team_color(team_label)
    
    # Draw bounding boxes and circles at player positions
    for (x, y) in player_positions:
        try:
            x, y = int(x), int(y)
            # Draw player position with circle
            try:
                cv2.circle(frame, (x, y), 5, color, -1)
            except Exception as e:
                print(f"Error drawing circle: {e}")
                
            # Draw bounding box
            try:
                cv2.rectangle(frame, (x - 10, y - 10), (x + 10, y + 10), color, 2)
            except Exception as e:
                print(f"Error drawing rectangle: {e}")
                
        except (ValueError, TypeError) as e:
            print(f"Error with player position coordinates ({x}, {y}): {e}")
            continue

    # Connect players with lines (for simplicity, connect first to last)
    if len(player_positions) > 1:
        for i in range(len(player_positions) - 1):
            try:
                x1, y1 = int(player_positions[i][0]), int(player_positions[i][1])
                x2, y2 = int(player_positions[i + 1][0]), int(player_positions[i + 1][1])
                
                try:
                    cv2.line(frame, (x1, y1), (x2, y2), color, 2)
                except Exception as e:
                    print(f"Error drawing line: {e}")
                    
            except (ValueError, TypeError) as e:
                print(f"Error with line coordinates: {e}")
                continue

    return frame

def overlay_formations_on_video(video_path, player_data, output_path):
    """
    Overlays formations on the video based on player data.

    Parameters:
    - video_path: Path to the input video file.
    - player_data: Dictionary containing frame numbers and player positions.
    - output_path: Path to save the annotated video.
    """
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise IOError(f"Cannot open video file: {video_path}")
            
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        width = int(cap.get(CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(CAP_PROP_FPS)
        
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_number = int(cap.get(CAP_PROP_POS_FRAMES))
            if frame_number in player_data:
                for team_label, positions in player_data[frame_number].items():
                    frame = draw_formation(frame, positions, team_label)

            out.write(frame)

        cap.release()
        out.release()
        
    except Exception as e:
        print(f"Error in video processing: {e}")