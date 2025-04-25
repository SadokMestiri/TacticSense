import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# Add CV2Stub definition to fix IDE warnings
try:
    # Test if methods exist
    cv2.GaussianBlur
    cv2.applyColorMap
    cv2.rectangle
    cv2.line
    cv2.circle
    cv2.putText
    cv2.imwrite
    cv2.FONT_HERSHEY_SIMPLEX
except (AttributeError, NameError):
    print("Warning: cv2 methods not found, using stub implementation")
    # Create comprehensive stub implementation for IDE
    class CV2Stub:
        # Color map constants
        COLORMAP_JET = 2
        COLORMAP_HOT = 11
        COLORMAP_COOL = 8
        
        # Font constants
        FONT_HERSHEY_SIMPLEX = 0
        FONT_HERSHEY_PLAIN = 1
        FONT_HERSHEY_DUPLEX = 2
        
        # Line types
        LINE_4 = 4
        LINE_8 = 8
        LINE_AA = 16
        
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
            
        def GaussianBlur(self, src, ksize, sigmaX, sigmaY=0, borderType=None):
            """Stub for cv2.GaussianBlur"""
            return src  # Return input unchanged
            
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
            
        def rectangle(self, img, pt1, pt2, color, thickness=1, lineType=8, shift=0):
            """Stub for cv2.rectangle"""
            return img
            
        def line(self, img, pt1, pt2, color, thickness=1, lineType=8, shift=0):
            """Stub for cv2.line"""
            return img
            
        def circle(self, img, center, radius, color, thickness=1, lineType=8, shift=0):
            """Stub for cv2.circle"""
            return img
            
        def putText(self, img, text, org, fontFace, fontScale, color, thickness=1, lineType=8, bottomLeftOrigin=False):
            """Stub for cv2.putText"""
            return img
            
        def imwrite(self, filename, img, params=None):
            """Stub for cv2.imwrite"""
            return True
    
    # Replace cv2 with our comprehensive stub
    cv2 = CV2Stub()

def create_field_template(width=800, height=500):
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

def generate_heatmap(positions, team_label=None, frame_shape=(500, 800)):
    """
    Generate a heatmap from player positions.
    
    Parameters:
        positions: List of player position dictionaries
        team_label: Filter positions by team label (None for all players)
        frame_shape: Shape of the output heatmap (height, width)
        
    Returns:
        Heatmap image with field overlay
    """
    # Create field template
    field_img = create_field_template(width=frame_shape[1], height=frame_shape[0])
    
    # Initialize heatmap
    heatmap = np.zeros(frame_shape, dtype=np.float32)
    
    # Add player positions to heatmap
    for pos in positions:
        if team_label is None or pos.get('team') == team_label:
            try:
                x, y = int(pos['x']), int(pos['y'])
                # Check if coordinates are within bounds
                if 0 <= y < frame_shape[0] and 0 <= x < frame_shape[1]:
                    # Create a gaussian blob at player position
                    sigma = 15.0  # Size of the gaussian blob
                    
                    # Only process a region around the position for efficiency
                    region_size = int(sigma * 3)
                    x1 = max(0, x - region_size)
                    x2 = min(frame_shape[1], x + region_size + 1)
                    y1 = max(0, y - region_size)
                    y2 = min(frame_shape[0], y + region_size + 1)
                    
                    # Create coordinate grids for the region
                    Y, X = np.ogrid[y1:y2, x1:x2]
                    
                    # Calculate squared distance
                    dist_squared = (X - x)**2 + (Y - y)**2
                    
                    # Create gaussian kernel
                    kernel = np.exp(-dist_squared / (2 * sigma**2))
                    
                    # Add to heatmap
                    heatmap[y1:y2, x1:x2] += kernel
            except (KeyError, ValueError, IndexError):
                continue
    
    # Normalize heatmap
    max_value = np.max(heatmap)
    if max_value > 0:
        heatmap = heatmap / max_value
    
    # Convert to uint8 image
    heatmap_img = (heatmap * 255).astype(np.uint8)
    
    # Apply colormap
    colormap_type = cv2.COLORMAP_COOL if team_label == 'Team A' else (
                    cv2.COLORMAP_HOT if team_label == 'Team B' else cv2.COLORMAP_JET)
    colored_heatmap = cv2.applyColorMap(heatmap_img, colormap_type)
    
    # Overlay on field
    result = field_img.copy()
    
    # Fix: Ensure both images have the same data type before blending
    # Convert both to uint8 if they're not already
    colored_heatmap = colored_heatmap.astype(np.uint8)
    result = result.astype(np.uint8)
    
    # Create a destination array of the same type and size
    dst = np.zeros_like(result)
    
    # Now perform the weighted addition with explicit destination
    alpha = 0.6
    cv2.addWeighted(colored_heatmap, alpha, result, 1 - alpha, 0, dst)
    
    # Copy back to result
    result = dst.copy()
    
    # Add team label
    title = "Overall Player Positions"
    if team_label:
        title = f"{team_label} Positions"
    
    # Add title to image
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(result, title, (10, 25), font, 0.7, (255, 255, 255), 2)
    
    return result

def generate_team_heatmaps(player_positions, output_dir, frame_shape=(500, 800)):
    """
    Generate and save heatmaps for each team and overall
    
    Parameters:
        player_positions: List of player position dictionaries
        output_dir: Directory to save output images
        frame_shape: Shape of the output heatmap (height, width)
        
    Returns:
        Dictionary with heatmap images
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    result = {}
    
    # Generate and save overall heatmap
    overall_heatmap = generate_heatmap(player_positions, None, frame_shape)
    overall_path = os.path.join(output_dir, "overall_heatmap.jpg")
    cv2.imwrite(overall_path, overall_heatmap)
    result['overall'] = overall_heatmap
    
    # Generate and save Team A heatmap
    team_a_heatmap = generate_heatmap(player_positions, 'Team A', frame_shape)
    team_a_path = os.path.join(output_dir, "team_a_heatmap.jpg")
    cv2.imwrite(team_a_path, team_a_heatmap)
    result['team_a'] = team_a_heatmap
    
    # Generate and save Team B heatmap
    team_b_heatmap = generate_heatmap(player_positions, 'Team B', frame_shape)
    team_b_path = os.path.join(output_dir, "team_b_heatmap.jpg")
    cv2.imwrite(team_b_path, team_b_heatmap)
    result['team_b'] = team_b_heatmap
    
    return result