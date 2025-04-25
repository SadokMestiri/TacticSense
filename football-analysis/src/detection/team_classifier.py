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
    # Test if required functions exist
    cv2.cvtColor
    cv2.COLOR_BGR2HSV
    cv2.calcHist
    cv2.minMaxLoc
    cv2.inRange
    cv2.countNonZero
    cv2.mean
except (ImportError, AttributeError):
    print("Error importing OpenCV or missing required functions. Using stub implementation.")
    # Create a more comprehensive stub for cv2
    class CV2Stub:
        # Constants
        COLOR_BGR2HSV = 40
        COLOR_BGR2RGB = 4
        COLOR_RGB2BGR = 4
        
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
            
        def VideoCapture(self, *args, **kwargs):
            class DummyCapture:
                def isOpened(self):
                    return False
                def read(self):
                    return False, None
                def release(self):
                    pass
            return DummyCapture()
            
        def mean(self, src, mask=None):
            """Stub for cv2.mean - returns a 4-tuple of zeros"""
            return (0.0, 0.0, 0.0, 0.0)
            
        def cvtColor(self, src, code, dstCn=None):
            """Stub for cv2.cvtColor - returns the input array"""
            return src
            
        def calcHist(self, images, channels, mask, histSize, ranges, hist=None, accumulate=False):
            """Stub for cv2.calcHist - returns a simple histogram"""
            dummy_hist = np.ones(tuple(histSize), dtype=np.float32)
            return dummy_hist
            
        def minMaxLoc(self, src, mask=None):
            """Stub for cv2.minMaxLoc - returns dummy min/max values and locations"""
            return 0.0, 1.0, (0, 0), (0, 0)
            
        def inRange(self, src, lowerb, upperb):
            """Stub for cv2.inRange - returns an all-zero mask"""
            if hasattr(src, 'shape'):
                if len(src.shape) == 3:
                    return np.zeros((src.shape[0], src.shape[1]), dtype=np.uint8)
                return np.zeros(src.shape[:2], dtype=np.uint8)
            return np.zeros((1, 1), dtype=np.uint8)
            
        def countNonZero(self, src):
            """Stub for cv2.countNonZero - returns 1"""
            return 1
    
    cv2 = CV2Stub()

# Import scikit-learn with error handling
try:
    from sklearn.cluster import KMeans
except ImportError:
    print("Error importing scikit-learn. Using fallback clustering.")
    
    # Simple KMeans fallback implementation
    class KMeans:
        def __init__(self, n_clusters=2, random_state=None):
            self.n_clusters = n_clusters
            self.labels_ = None
            
        def fit(self, X):
            # Very simple implementation - just assign alternating labels
            if X.shape[0] == 0:
                self.labels_ = []
            else:
                self.labels_ = [i % self.n_clusters for i in range(X.shape[0])]
            return self

class TeamClassifier:
    def __init__(self, num_teams=2):
        self.num_teams = num_teams
        self.team_colors = None  # Store team colors once identified
        
    def classify_teams(self, bounding_boxes, frame):
        """
        Classify teams based on jersey colors.
        
        Parameters:
            bounding_boxes: List of bounding boxes (x, y, w, h)
            frame: Image frame
            
        Returns:
            List of team labels ('Team A' or 'Team B')
        """
        if not bounding_boxes:
            return []
            
        jersey_colors = self._extract_jersey_color(frame, bounding_boxes)
        if jersey_colors.shape[0] < 2:  # Need at least 2 players to classify
            return ['Unknown'] * len(bounding_boxes)
            
        labels = self._classify(jersey_colors)
        
        # Convert numeric labels to team names
        team_labels = ['Team A' if label == 0 else 'Team B' for label in labels]
        return team_labels
        
    def _extract_jersey_color(self, frame, bounding_boxes):
        """Extract average color from player bounding boxes."""
        jersey_colors = []
        
        # Calculate upper body region (usually where jersey is most visible)
        for box in bounding_boxes:
            try:
                x, y, w, h = box
                # Focus on upper body for jersey color (exclude head and legs)
                upper_body_y = int(y + h * 0.2)  # Start below the head
                upper_body_h = int(h * 0.4)      # Take ~40% of player height
                
                # Ensure coordinates are within frame bounds
                y_start = max(0, upper_body_y)
                y_end = min(frame.shape[0], upper_body_y + upper_body_h)
                x_start = max(0, x)
                x_end = min(frame.shape[1], x + w)
                
                if y_end <= y_start or x_end <= x_start:
                    jersey_colors.append([0, 0, 0])
                    continue
                    
                roi = frame[y_start:y_end, x_start:x_end]
                if roi.size > 0:
                    try:
                        # Try using advanced color analysis with fallbacks
                        try:
                            # Convert to HSV for better color analysis
                            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
                            # Create histogram of hue channel
                            hist = cv2.calcHist([hsv_roi], [0, 1], None, [30, 30], [0, 180, 0, 256])
                            # Find peak in histogram
                            _, _, _, max_loc = cv2.minMaxLoc(hist)
                            h, s = max_loc
                            # Get average value from that hue/saturation
                            mask = cv2.inRange(hsv_roi, (h-2, s-30, 0), (h+2, s+30, 255))
                            if cv2.countNonZero(mask) > 0:
                                avg_color = cv2.mean(roi, mask=mask)[:3]
                            else:
                                avg_color = cv2.mean(roi)[:3]
                        except Exception as advanced_error:
                            print(f"Advanced color analysis failed: {advanced_error}")
                            # Fall back to simple mean
                            avg_color = cv2.mean(roi)[:3]
                        
                        jersey_colors.append(avg_color)
                    except Exception as e:
                        print(f"Color extraction failed: {e}")
                        # Use fallback
                        if hasattr(roi, 'shape') and len(roi.shape) == 3:
                            avg_color = np.mean(roi, axis=(0, 1))[:3]
                        else:
                            avg_color = [127, 127, 127]  # Gray fallback
                        jersey_colors.append(avg_color)
                else:
                    jersey_colors.append([0, 0, 0])
            except Exception as e:
                print(f"Error extracting jersey color: {e}")
                jersey_colors.append([0, 0, 0])
                
        return np.array(jersey_colors)
        
    def _classify(self, jersey_colors):
        """Classify colors into teams using KMeans."""
        if jersey_colors.shape[0] < self.num_teams:
            return [0] * len(jersey_colors)
            
        try:
            kmeans = KMeans(n_clusters=self.num_teams, random_state=42)
            kmeans.fit(jersey_colors)
            
            # Store team colors for consistent labeling
            if self.team_colors is None:
                self.team_colors = kmeans.cluster_centers_
                
            return kmeans.labels_
        except Exception as e:
            print(f"Error in team classification: {e}")
            return [0] * len(jersey_colors)

# These functions are kept for backwards compatibility
def classify_team(jersey_colors, num_teams=2):
    try:
        kmeans = KMeans(n_clusters=num_teams)
        kmeans.fit(jersey_colors)
        return kmeans.labels_
    except Exception:
        # Fallback to simple assignment
        return [i % num_teams for i in range(len(jersey_colors))]

def extract_jersey_color(frame, bounding_boxes):
    jersey_colors = []
    for box in bounding_boxes:
        try:
            if isinstance(box, tuple) and len(box) == 4:
                x, y, w, h = box
            else:
                continue
                
            # Safe region extraction
            y_start = max(0, y)
            y_end = min(frame.shape[0], y + h)
            x_start = max(0, x)
            x_end = min(frame.shape[1], x + w)
            
            if y_end <= y_start or x_end <= x_start:
                continue
                
            roi = frame[y_start:y_end, x_start:x_end]
            
            if roi.size > 0:
                try:
                    avg_color = cv2.mean(roi)[:3]  # Get average color in BGR
                except Exception:
                    # Calculate mean manually
                    if roi.ndim == 3:  # Color image
                        avg_color = np.mean(roi, axis=(0, 1))[:3]
                    else:  # Grayscale
                        avg_color = [np.mean(roi)] * 3
                jersey_colors.append(avg_color)
        except Exception:
            continue
            
    return np.array(jersey_colors) if jersey_colors else np.array([[0, 0, 0]])

def assign_teams_to_players(frame, bounding_boxes):
    jersey_colors = extract_jersey_color(frame, bounding_boxes)
    if len(jersey_colors) == 0:
        return []
    team_labels = classify_team(jersey_colors)
    return ['Team A' if label == 0 else 'Team B' for label in team_labels]