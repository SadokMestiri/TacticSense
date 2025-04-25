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
            
        def rectangle(self, img, pt1, pt2, color, thickness=1, lineType=8, shift=0):
            """Stub for cv2.rectangle"""
            pass
            
        def putText(self, img, text, org, fontFace, fontScale, color, 
                    thickness=1, lineType=8, bottomLeftOrigin=False):
            """Stub for cv2.putText"""
            pass
    cv2 = CV2Stub()

# Constants from OpenCV in case they're not recognized
FONT_HERSHEY_SIMPLEX = 0

def calculate_distance(point1, point2):
    """Calculate Euclidean distance between two points."""
    return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5

def get_team_color(team_label):
    """Get color for team visualization based on team label."""
    if team_label == 'Team A':
        return (255, 0, 0)  # Red
    elif team_label == 'Team B':
        return (0, 0, 255)  # Blue
    return (255, 255, 255)  # Default to white

def draw_bounding_box(image, bbox, color, label):
    """Draw bounding box with label on image."""
    try:
        x, y, w, h = bbox
        cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
        cv2.putText(image, label, (x, y - 10), FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    except Exception as e:
        print(f"Error drawing bounding box: {e}")

def cluster_colors(jersey_colors):
    """Cluster jersey colors to identify teams."""
    try:
        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=2)
        kmeans.fit(jersey_colors)
        return kmeans.cluster_centers_
    except ImportError:
        print("scikit-learn not installed. Using simple clustering instead.")
        return simple_color_clustering(jersey_colors)

def simple_color_clustering(colors):
    """Simple clustering method when scikit-learn is not available."""
    if not colors or len(colors) < 2:
        return [np.array([255, 0, 0]), np.array([0, 0, 255])]  # Default colors
        
    # Calculate mean as centroid 1
    c1 = np.mean(colors, axis=0)
    # Find the point furthest from mean as centroid 2
    max_dist = 0
    c2 = None
    for color in colors:
        dist = np.linalg.norm(color - c1)
        if dist > max_dist:
            max_dist = dist
            c2 = color
    
    if c2 is None:
        c2 = np.array([0, 0, 255])
        
    return [c1, c2]