import os
import numpy as np

# Add CV2 stubs for IDE to recognize methods
try:
    import cv2
    # Test if methods exist
    cv2.rectangle
    cv2.applyColorMap
    cv2.COLORMAP_HOT
except (ImportError, AttributeError):
    print("Warning: Some cv2 methods not found, using stub implementation")
    # Create comprehensive stub implementation for IDE
    class CV2Stub:
        # Constants
        COLOR_BGR2RGB = 4
        COLOR_RGB2BGR = 4
        COLORMAP_HOT = 11
        COLORMAP_COOL = 8
        COLORMAP_JET = 2
        FONT_HERSHEY_SIMPLEX = 0
        
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
            
        def rectangle(self, img, pt1, pt2, color, thickness=1, lineType=8, shift=0):
            """Stub for cv2.rectangle"""
            return img
            
        def line(self, img, pt1, pt2, color, thickness=1, lineType=8, shift=0):
            """Stub for cv2.line"""
            return img
            
        def circle(self, img, center, radius, color, thickness=1, lineType=8, shift=0):
            """Stub for cv2.circle"""
            return img
            
        def cvtColor(self, src, code, dstCn=None):
            """Stub for cv2.cvtColor"""
            return src
            
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
                def isOpened(self):  # Add isOpened method
                    return True
            return DummyWriter()
            
        def putText(self, img, text, org, fontFace, fontScale, color, 
                   thickness=1, lineType=8, bottomLeftOrigin=False):
            """Stub for cv2.putText"""
            return img
            
        def applyColorMap(self, src, colormap):
            """Stub for cv2.applyColorMap"""
            if hasattr(src, 'shape'):
                return np.zeros((src.shape[0], src.shape[1], 3), dtype=np.uint8)
            return np.zeros((1, 1, 3), dtype=np.uint8)
            
        def addWeighted(self, src1, alpha, src2, beta, gamma, dst=None):
            """Stub for cv2.addWeighted"""
            if src2 is not None and hasattr(src2, 'copy'):
                return src2.copy()
            return np.zeros((1, 1, 3), dtype=np.uint8)
            
        def resize(self, src, dsize, fx=None, fy=None, interpolation=None):
            """Stub for cv2.resize"""
            if dsize is not None and len(dsize) == 2:
                return np.zeros((dsize[1], dsize[0], 3), dtype=np.uint8)
            return src
    
    # Replace cv2 with our comprehensive stub
    cv2 = CV2Stub()

class DynamicHeatmapGenerator:
    """Generates dynamic heatmaps showing player movement over time"""
    
    def __init__(self, field_template=None, window_size=90):
        """
        Initialize with optional field template and time window
        
        Args:
            field_template: Optional pre-made soccer field image
            window_size: Number of frames in the sliding window
        """
        self.window_size = window_size
        self.position_history = []
        self.last_positions = {}  # Store last position for each player/team 
        self.team_colors = {
            'Team A': (0, 0, 255),  # Red in BGR
            'Team B': (255, 0, 0)   # Blue in BGR
        }
        
        if field_template is None:
            self.field_template = self._create_field_template(800, 500)
        else:
            self.field_template = field_template
    
    def _create_field_template(self, width=800, height=500):
        """Create a soccer field template image"""
        # Create green field
        field = np.ones((height, width, 3), dtype=np.uint8) * [80, 140, 30]
        
        # Draw field markings (white lines)
        # Outer boundary
        cv2.rectangle(field, (50, 50), (width-50, height-50), (255, 255, 255), 2)
        
        # Halfway line
        cv2.line(field, (width//2, 50), (width//2, height-50), (255, 255, 255), 2)
        
        # Center circle
        cv2.circle(field, (width//2, height//2), 60, (255, 255, 255), 2)
        cv2.circle(field, (width//2, height//2), 5, (255, 255, 255), -1)
        
        # Penalty areas
        cv2.rectangle(field, (50, height//2-90), (50+110, height//2+90), 
                     (255, 255, 255), 2)
        cv2.rectangle(field, (width-50-110, height//2-90), (width-50, height//2+90), 
                     (255, 255, 255), 2)
        
        # Goal areas
        cv2.rectangle(field, (50, height//2-40), (50+55, height//2+40), 
                     (255, 255, 255), 2)
        cv2.rectangle(field, (width-50-55, height//2-40), (width-50, height//2+40), 
                     (255, 255, 255), 2)
        
        # Goals
        cv2.rectangle(field, (40, height//2-30), (50, height//2+30), (120, 120, 120), -1)
        cv2.rectangle(field, (width-50, height//2-30), (width-40, height//2+30), 
                     (120, 120, 120), -1)
        
        return field
    
    def update_positions(self, frame_index, player_positions, team_labels=None):
        """
        Update the position history with new player positions
        
        Args:
            frame_index: Current frame number
            player_positions: List of player positions (x, y, w, h)
            team_labels: List of team labels for each player
        """
        positions = []
        
        for i, box in enumerate(player_positions):
            try:
                x, y, w, h = box
                team = team_labels[i] if team_labels and i < len(team_labels) else 'Unknown'
                
                # Skip unknown teams
                if team == 'Unknown':
                    continue
                
                player_id = f"player_{i}"
                pos_x, pos_y = int(x + w//2), int(y + h)  # Use feet position (bottom center)
                
                # Store player position and metadata
                player_pos = {
                    'x': pos_x,
                    'y': pos_y,
                    'team': team,
                    'id': player_id,
                    'frame': frame_index,
                    'box': box
                }
                positions.append(player_pos)
                
                # Track last position for movement trails
                self.last_positions[player_id] = player_pos
                
            except Exception as e:
                print(f"Error updating position: {e}")
        
        # Only add if we have positions
        if positions:
            frame_data = {
                'frame': frame_index,
                'positions': positions
            }
            self.position_history.append(frame_data)
            
            # Maintain sliding window
            while len(self.position_history) > self.window_size:
                self.position_history.pop(0)
    
    def generate_heatmap_frame(self, frame=None, alpha=0.6):
        """
        Generate a heatmap visualization for the current window
        
        Args:
            frame: Optional video frame to overlay
            alpha: Transparency of the heatmap
            
        Returns:
            Visualization image with heatmap
        """
        if not self.position_history:
            return self.field_template.copy()
        
        # Start with field template or provided frame
        if frame is not None:
            # Resize the frame to match field template dimensions if needed
            if frame.shape[0] != self.field_template.shape[0] or frame.shape[1] != self.field_template.shape[1]:
                frame = cv2.resize(frame, (self.field_template.shape[1], self.field_template.shape[0]))
            base_img = frame.copy()
        else:
            base_img = self.field_template.copy()
        
        # Create separate heatmaps for each team
        h, w = base_img.shape[:2]
        team_a_heatmap = np.zeros((h, w), dtype=np.float32)
        team_b_heatmap = np.zeros((h, w), dtype=np.float32)
        
        # Process position history to create heatmaps
        for frame_data in self.position_history:
            for pos in frame_data['positions']:
                try:
                    team = pos['team']
                    x, y = int(pos['x']), int(pos['y'])
                    
                    # Ensure coordinates are within bounds
                    if 0 <= x < w and 0 <= y < h:
                        # Add Gaussian blob with decay based on frame age
                        sigma = 15.0  # Size of the Gaussian blob
                        
                        # Create a small region around the position for efficiency
                        region_size = int(sigma * 3)
                        x1 = max(0, x - region_size)
                        x2 = min(w, x + region_size + 1)
                        y1 = max(0, y - region_size)
                        y2 = min(h, y + region_size + 1)
                        
                        # Create X and Y coordinate matrices
                        Y, X = np.ogrid[y1:y2, x1:x2]
                        
                        # Calculate squared distance
                        dist_squared = (X - x)**2 + (Y - y)**2
                        
                        # Create Gaussian kernel
                        kernel = np.exp(-dist_squared / (2 * sigma**2))
                        
                        # Add to appropriate team heatmap
                        if team == 'Team A':
                            team_a_heatmap[y1:y2, x1:x2] += kernel
                        elif team == 'Team B':
                            team_b_heatmap[y1:y2, x1:x2] += kernel
                
                except Exception as e:
                    print(f"Error generating heatmap: {e}")
                    continue
        
        # Normalize heatmaps
        team_a_max = np.max(team_a_heatmap)
        if team_a_max > 0:
            team_a_heatmap = team_a_heatmap / team_a_max
            
        team_b_max = np.max(team_b_heatmap)
        if team_b_max > 0:
            team_b_heatmap = team_b_heatmap / team_b_max
        
        # Apply color maps (red for team A, blue for team B)
        team_a_colored = cv2.applyColorMap(
            (team_a_heatmap * 255).astype(np.uint8), 
            cv2.COLORMAP_HOT
        )
        
        team_b_colored = cv2.applyColorMap(
            (team_b_heatmap * 255).astype(np.uint8), 
            cv2.COLORMAP_COOL
        )
        
        # Blend the heatmaps with the base image
        result = base_img.copy()
        cv2.addWeighted(team_a_colored, alpha, result, 1.0, 0, result)
        cv2.addWeighted(team_b_colored, alpha, result, 1.0, 0, result)
        
        # Add current player markers
        if self.position_history:
            latest_frame_data = self.position_history[-1]
            for pos in latest_frame_data['positions']:
                x, y = int(pos['x']), int(pos['y'])
                team = pos['team']
                if team == 'Team A':
                    color = (0, 0, 255)  # Red for Team A
                elif team == 'Team B':
                    color = (255, 0, 0)  # Blue for Team B
                else:
                    color = (255, 255, 255)  # White for unknown
                
                # Draw player position
                cv2.circle(result, (x, y), 5, color, -1)
        
        return result
    
    def create_dynamic_heatmap_video(self, output_path, fps=15):
        """
        Create a video with dynamic heatmap evolution
        
        Args:
            output_path: Path to save the output video
            fps: Frames per second
        """
        if not self.position_history or len(self.position_history) < 2:
            print("Not enough position data for video creation")
            return
        
        print(f"Creating heatmap video with {len(self.position_history)} frames...")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Set video size based on field template
        h, w = self.field_template.shape[:2]
        
        # Try different codec options
        try:
            # First try XVID codec (widely compatible)
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            output_file = output_path.replace('.mp4', '.avi')  # Change to AVI
            out = cv2.VideoWriter(output_file, fourcc, fps, (w, h))
            
            if not out.isOpened():
                # Fall back to other codecs if XVID fails
                codecs_to_try = ['MJPG', 'H264', 'MP4V']
                
                for codec in codecs_to_try:
                    try:
                        fourcc = cv2.VideoWriter_fourcc(*codec)
                        ext = '.avi' if codec in ['XVID', 'MJPG'] else '.mp4'
                        output_file = output_path.replace('.mp4', ext)
                        out = cv2.VideoWriter(output_file, fourcc, fps, (w, h))
                        if out.isOpened():
                            print(f"Using codec: {codec}")
                            break
                    except Exception:
                        continue
        
            if not out.isOpened():
                print("Failed to create video writer with any codec")
                return
            
            # Process each frame with a sliding window approach
            window_size = 30  # Number of frames in sliding window
            
            for i in range(len(self.position_history)):
                # Create window of frames
                start_idx = max(0, i - window_size)
                window_data = self.position_history[start_idx:i+1]
                
                # Create temporary generator with just this window
                temp_gen = DynamicHeatmapGenerator(self.field_template.copy())
                
                # Add all positions from window
                for frame_data in window_data:
                    positions = []
                    team_labels = []
                    for pos in frame_data['positions']:
                        if 'box' in pos:
                            positions.append(pos['box'])
                            team_labels.append(pos['team'])
                        else:
                            # Create a dummy box from position
                            x, y = pos['x'], pos['y']
                            dummy_box = (x-5, y-5, 10, 10)
                            positions.append(dummy_box)
                            team_labels.append(pos['team'])
                    
                    # Update the temp generator with this frame's data
                    temp_gen.update_positions(frame_data['frame'], positions, team_labels)
                
                # Generate heatmap for this window
                heatmap = temp_gen.generate_heatmap_frame(alpha=0.6)
                
                # Add frame counter
                frame_num = self.position_history[i]['frame']
                cv2.putText(
                    heatmap, 
                    f"Frame: {frame_num}", 
                    (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    1, 
                    (255, 255, 255), 
                    2
                )
                
                # Write to video
                out.write(heatmap)
                
                # Report progress
                if i % 10 == 0:
                    print(f"Processed {i}/{len(self.position_history)} frames")
            
            # Properly close the video
            out.release()
            print(f"Dynamic heatmap video saved to {output_file}")
            
            # Verify file was created
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                print(f"Video file created successfully: {os.path.getsize(output_file)} bytes")
            else:
                print("Error: Output video file not created or empty")
            
        except Exception as e:
            print(f"Error creating heatmap video: {e}")