import os
import sys
import numpy as np
from tqdm import tqdm

# Add CV2 stubs for IDE to recognize methods
try:
    import cv2
    # Test if methods exist
    cv2.VideoCapture
    cv2.CAP_PROP_FPS
    cv2.VideoWriter_fourcc
    cv2.drawContours
    cv2.putText
    cv2.imwrite
except (ImportError, AttributeError):
    print("Warning: Some cv2 methods not found, using stub implementation")
    # Create comprehensive stub implementation for IDE
    class CV2Stub:
        # Constants for video capture properties
        CAP_PROP_FPS = 5
        CAP_PROP_FRAME_WIDTH = 3
        CAP_PROP_FRAME_HEIGHT = 4
        CAP_PROP_FRAME_COUNT = 7
        CAP_PROP_POS_FRAMES = 1
        
        # Font constants
        FONT_HERSHEY_SIMPLEX = 0
        
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
        
        def VideoCapture(self, *args):
            """Stub for cv2.VideoCapture"""
            class DummyCapture:
                def isOpened(self):
                    return False
                def read(self):
                    return False, None
                def release(self):
                    pass
                def get(self, propId):
                    return 0
                def set(self, propId, value):
                    return True
            return DummyCapture()
            
        def VideoWriter_fourcc(self, *args):
            """Stub for cv2.VideoWriter_fourcc"""
            return 0
            
        def VideoWriter(self, filename, fourcc, fps, frameSize, isColor=True):
            """Stub for cv2.VideoWriter"""
            class DummyWriter:
                def isOpened(self):
                    return True
                def write(self, img):
                    pass
                def release(self):
                    pass
            return DummyWriter()
            
        def drawContours(self, image, contours, contourIdx, color, 
                        thickness=None, lineType=None, hierarchy=None, 
                        maxLevel=None, offset=None):
            """Stub for cv2.drawContours"""
            return image
            
        def putText(self, img, text, org, fontFace, fontScale, color, 
                   thickness=1, lineType=8, bottomLeftOrigin=False):
            """Stub for cv2.putText"""
            return img
            
        def imwrite(self, filename, img, params=None):
            """Stub for cv2.imwrite"""
            return True
            
        def rectangle(self, img, pt1, pt2, color, thickness=1, lineType=8, shift=0):
            """Stub for cv2.rectangle"""
            return img
    
    # Replace cv2 with our comprehensive stub
    cv2 = CV2Stub()

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from src.detection.player_detector import PlayerDetector
from src.detection.field_detector import FieldDetector
from src.detection.team_classifierV2 import TeamClassifierV2
from src.visualization.heatmap_generator import generate_team_heatmaps
from src.utils.helpers import draw_bounding_box, get_team_color

def run_dynamic_analysis(video_path, output_dir, sample_rate=5):
    """
    Run football analysis with team formation detection and heatmap generation
    
    Args:
        video_path: Path to input video
        output_dir: Directory to save outputs
        sample_rate: Process every Nth frame
    """
    print("Initializing football analysis pipeline...")
    
    # Initialize components
    detector = PlayerDetector()
    field_detector = FieldDetector(detection_width=640)  # Initialize with desired width
    team_classifier = TeamClassifierV2()
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return
    
    # Video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"Video: {width}x{height} @ {fps}fps, {total_frames} frames")
    
    # Set up writers - use XVID codec with AVI container for wider compatibility
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    output_video_path = os.path.join(output_dir, "analysis_output.avi")
    
    out_video = cv2.VideoWriter(
        output_video_path,
        fourcc, 
        fps//sample_rate, 
        (width, height)
    )
    
    if not out_video.isOpened():
        print("Warning: Could not create output video writer.")
        # Try alternative codec
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        out_video = cv2.VideoWriter(
            output_video_path,
            fourcc, 
            fps//sample_rate, 
            (width, height)
        )
    
    # Process video
    frame_count = 0
    processed_count = 0
    current_field_mask = None
    current_field_contour = None  # Store the contour in original coordinates
    all_positions = []  # Initialize the list here

    print("Processing video...")
    progress_bar = tqdm(total=total_frames)
    
    # Attempt initial field detection
    print("Attempting initial field detection...")
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(total_frames * 0.1))  # Start 10% in
    ret, initial_frame = cap.read()
    if ret:
        current_field_mask, current_field_contour = field_detector.detect_field(initial_frame)
        if current_field_contour is not None:
            print("Initial field detection successful.")
        else:
            print("Initial field detection failed, will try per frame.")
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset video
    
    # Main processing loop
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame_count += 1
        progress_bar.update(1)
        
        # Process only every Nth frame
        if frame_count % sample_rate != 0:
            continue
            
        processed_count += 1
        
        # 1. Detect field
        current_field_mask, current_field_contour = field_detector.detect_field(frame)
        
        # 2. Detect players
        bounding_boxes = detector.detect_players(frame)
        
        # 3. Filter players outside the field
        if current_field_contour is not None:
            bounding_boxes = filter_players_outside_contour(bounding_boxes, current_field_contour)
        
        # 4. Classify teams
        team_labels = team_classifier.classify_teams(bounding_boxes, frame)
        
        # 5. Collect player positions for heatmap
        for i, box in enumerate(bounding_boxes):
            if i < len(team_labels):
                x, y, w, h = box
                position = {
                    'x': x + w//2,
                    'y': y + h,
                    'team': team_labels[i],
                    'frame': frame_count
                }
                all_positions.append(position)
        
        # 6. Create visualizations with formations
        viz_frame = frame.copy()
        
        # Draw field boundary if detected
        if current_field_contour is not None:
            cv2.drawContours(viz_frame, [current_field_contour], 0, (0, 255, 0), 2)
        
        # Draw player bounding boxes with team colors
        for i, box in enumerate(bounding_boxes):
            if i < len(team_labels):
                color = (0, 0, 255) if team_labels[i] == 'Team A' else (255, 0, 0)
                draw_bounding_box(viz_frame, box, color, team_labels[i])
        
        # Draw team formations
        viz_frame = team_classifier.draw_formations(viz_frame)
        
        # Add frame number
        cv2.putText(
            viz_frame,
            f"Frame: {frame_count}",
            (10, 90),  # Position below formation labels
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )
        
        # Save to video
        out_video.write(viz_frame)
        
        # Generate intermediate heatmap every 1000 frames
        if processed_count % 1000 == 0:
            print(f"\nGenerating intermediate heatmaps at frame {frame_count}...")
            generate_team_heatmaps(
                all_positions, 
                os.path.join(output_dir, f"heatmaps_{frame_count}"),
                frame_shape=(height, width)
            )
    
    # Cleanup video resources
    progress_bar.close()
    cap.release()
    out_video.release()
    
    # Generate final heatmaps
    print("\nGenerating final heatmaps...")
    heatmaps = generate_team_heatmaps(
        all_positions, 
        os.path.join(output_dir, "final_heatmaps"),
        frame_shape=(height, width)
    )
    
    print(f"\nAnalysis complete! Processed {processed_count} frames.")
    print(f"Output video: {output_video_path}")
    print(f"Heatmaps saved to: {os.path.join(output_dir, 'final_heatmaps')}")

def filter_players_outside_contour(bounding_boxes, field_contour):
    """Filters player bounding boxes based on whether their feet are inside the field contour."""
    if field_contour is None or len(field_contour) == 0:
        return bounding_boxes  # No filtering if contour is invalid

    filtered_boxes = []
    contour_for_test = field_contour.reshape(-1, 1, 2) if len(field_contour.shape) == 2 else field_contour

    for box in bounding_boxes:
        x, y, w, h = box
        feet_x, feet_y = int(x + w//2), int(y + h)

        try:
            test_result = cv2.pointPolygonTest(contour_for_test, (float(feet_x), float(feet_y)), False)
            if test_result >= 0:
                filtered_boxes.append(box)
        except Exception as poly_test_error:
            print(f"Error during pointPolygonTest in filter: {poly_test_error}")
            filtered_boxes.append(box)  # Include box if error occurs during test

    return filtered_boxes

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Dynamic Football Analysis")
    parser.add_argument("video", help="Path to input video file")
    parser.add_argument("--output", "-o", default="output", help="Output directory")
    parser.add_argument("--sample-rate", "-s", type=int, default=5, 
                      help="Process every Nth frame (default: 5)")
    
    args = parser.parse_args()
    
    run_dynamic_analysis(args.video, args.output, args.sample_rate)