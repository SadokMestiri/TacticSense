import cv2
import numpy as np

class PositionTracker:
    def __init__(self):
        self.player_positions = []
        self.current_frame = 0

    def update_positions(self, frame_number, detections):
        """
        Update player positions with new detections.
        
        Parameters:
            frame_number: Current frame number
            detections: List of dictionaries containing detection information
        """
        self.current_frame = frame_number
        
        for detection in detections:
            try:
                # Calculate center position
                if 'x_min' in detection and 'x_max' in detection:
                    # If using min/max coordinates
                    x_center = (detection['x_min'] + detection['x_max']) / 2
                    y_center = (detection['y_min'] + detection['y_max']) / 2
                elif 'bbox' in detection:
                    # If using bounding box format (x, y, w, h)
                    x, y, w, h = detection['bbox']
                    x_center = x + w / 2
                    y_center = y + h / 2
                else:
                    # Direct position
                    x_center = detection.get('x', 0)
                    y_center = detection.get('y', 0)
                
                team_label = detection.get('team_label', 'unknown')
                
                self.player_positions.append({
                    'frame': frame_number,
                    'x': x_center,
                    'y': y_center,
                    'team': team_label,
                    'id': detection.get('id', -1),
                    'confidence': detection.get('confidence', 1.0)
                })
            except Exception as e:
                print(f"Error updating position: {e}")

    def get_positions(self, frame_number=None, team_label=None):
        """
        Get player positions, optionally filtered by frame number and team label.
        
        Parameters:
            frame_number: Filter by specific frame (default: None)
            team_label: Filter by team label (default: None)
            
        Returns:
            List of position dictionaries
        """
        result = self.player_positions
        
        if frame_number is not None:
            result = [pos for pos in result if pos['frame'] == frame_number]
            
        if team_label is not None:
            result = [pos for pos in result if pos['team'] == team_label]
            
        return result

    def reset(self):
        """Reset all stored positions."""
        self.player_positions = []
        self.current_frame = 0