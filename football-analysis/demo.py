import cv2
import numpy as np
import os
import sys
import argparse
from tqdm import tqdm  # For progress bar

# Add CV2 stubs for IDE recognition
try:
    # Test if some common OpenCV functionality exists
    cv2.VideoCapture
    cv2.CAP_PROP_FPS
except (AttributeError, NameError):
    print("Warning: Some cv2 methods not found, using stub implementation")
    # Create a comprehensive stub implementation for IDE
    class CV2Stub:
        # Constants
        CAP_PROP_FPS = 5
        CAP_PROP_FRAME_WIDTH = 3
        CAP_PROP_FRAME_HEIGHT = 4
        CAP_PROP_FRAME_COUNT = 7
        FONT_HERSHEY_SIMPLEX = 0
        
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
        
        def VideoCapture(self, *args):
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
            return 0
            
        def VideoWriter(self, filename, fourcc, fps, frameSize, isColor=True):
            class DummyWriter:
                def write(self, img):
                    pass
                def release(self):
                    pass
            return DummyWriter()
            
        def putText(self, img, text, org, fontFace, fontScale, color, 
                   thickness=1, lineType=8, bottomLeftOrigin=False):
            pass
            
        def imshow(self, winname, mat):
            pass
            
        def waitKey(self, delay=0):
            return 0
            
        def destroyAllWindows(self):
            pass
    
    # Replace cv2 with our stub that has all required methods
    cv2 = CV2Stub()

# Add project root to path to ensure imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import components
from src.detection.player_detector import PlayerDetector
from src.detection.team_classifier import TeamClassifier
from src.visualization.formation_overlay import overlay_formation
from src.visualization.heatmap_generator import generate_heatmap, plot_heatmap


def run_demo(video_path, output_dir, sample_rate=10, show_preview=True, save_video=True):
    """
    Run the complete football analysis pipeline demo
    
    Args:
        video_path: Path to the input video file
        output_dir: Directory to save output files
        sample_rate: Process every Nth frame (default: 10)
        show_preview: Show real-time preview (default: True)
        save_video: Save the output video (default: True)
    """
    print("Initializing football analysis pipeline...")
    
    # Initialize components
    detector = PlayerDetector()
    classifier = TeamClassifier()
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Open video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return
    
    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"Video stats: {frame_width}x{frame_height}, {fps} FPS, {total_frames} frames")
    
    # Setup video writer
    video_writer = None
    if save_video:
        output_video_path = os.path.join(output_dir, "analysis_output.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(
            output_video_path, fourcc, fps//sample_rate, (frame_width, frame_height)
        )
    
    # Data structures to store analysis results
    all_player_positions = []
    frame_count = 0
    processed_count = 0
    
    # Process the video
    print("Processing video frames...")
    progress_bar = tqdm(total=total_frames)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame_count += 1
        progress_bar.update(1)
        
        # Process only every Nth frame to save time
        if frame_count % sample_rate != 0:
            continue
            
        processed_count += 1
        
        # 1. Detect players in the frame
        bounding_boxes = detector.detect_players(frame)
        
        # 2. Classify players into teams
        team_labels = classifier.classify_teams(bounding_boxes, frame)
        
        # 3. Extract player positions for visualization
        frame_positions = []
        for i, box in enumerate(bounding_boxes):
            if i < len(team_labels):  # Ensure we have a team label
                x, y, w, h = box
                center_x = x + w//2
                center_y = y + h//2
                
                # Store position data
                pos_data = {
                    'x': center_x,
                    'y': center_y,
                    'team': team_labels[i],
                    'frame': frame_count
                }
                
                frame_positions.append(pos_data)
                all_player_positions.append(pos_data)
        
        # 4. Generate visualizations for current frame
        annotated_frame = frame.copy()
        
        # Add formation overlay
        annotated_frame = overlay_formation(annotated_frame, frame_positions)
        
        # Add frame number and processing info
        cv2.putText(
            annotated_frame, 
            f"Frame: {frame_count}", 
            (10, 30), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            1, 
            (255, 255, 255), 
            2
        )
        
        # Display and save
        if show_preview:
            cv2.imshow('Football Analysis', annotated_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        if video_writer:
            video_writer.write(annotated_frame)
    
    # Cleanup video resources
    progress_bar.close()
    cap.release()
    if video_writer:
        video_writer.release()
    if show_preview:
        cv2.destroyAllWindows()
    
    # Generate heatmaps from all collected position data
    print("Generating heatmaps...")
    frame_shape = (frame_height, frame_width)
    
    # Overall heatmap
    overall_heatmap = generate_heatmap(all_player_positions, frame_shape=frame_shape)
    plot_heatmap(
        overall_heatmap, 
        os.path.join(output_dir, "overall_heatmap.png"),
        "Overall Player Positions"
    )
    
    # Team A heatmap
    team_a_heatmap = generate_heatmap(
        all_player_positions, team_label="Team A", frame_shape=frame_shape
    )
    plot_heatmap(
        team_a_heatmap, 
        os.path.join(output_dir, "team_a_heatmap.png"),
        "Team A Player Positions"
    )
    
    # Team B heatmap
    team_b_heatmap = generate_heatmap(
        all_player_positions, team_label="Team B", frame_shape=frame_shape
    )
    plot_heatmap(
        team_b_heatmap, 
        os.path.join(output_dir, "team_b_heatmap.png"),
        "Team B Player Positions"
    )
    
    print(f"\nAnalysis complete! Processed {processed_count} frames.")
    print(f"Output saved to {output_dir}")
    print(f" - Annotated video: {os.path.join(output_dir, 'analysis_output.mp4')}")
    print(f" - Overall heatmap: {os.path.join(output_dir, 'overall_heatmap.png')}")
    print(f" - Team A heatmap: {os.path.join(output_dir, 'team_a_heatmap.png')}")
    print(f" - Team B heatmap: {os.path.join(output_dir, 'team_b_heatmap.png')}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Football Match Analysis Pipeline')
    parser.add_argument('video', help='Path to input video file')
    parser.add_argument('--output', '-o', default='output', help='Output directory')
    parser.add_argument('--sample-rate', '-s', type=int, default=10, 
                        help='Process every Nth frame (default: 10)')
    parser.add_argument('--no-preview', action='store_true', 
                        help='Disable real-time preview')
    parser.add_argument('--no-save-video', action='store_true', 
                        help='Do not save output video')
    
    args = parser.parse_args()
    
    run_demo(
        args.video,
        args.output,
        sample_rate=args.sample_rate,
        show_preview=not args.no_preview,
        save_video=not args.no_save_video
    )