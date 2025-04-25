import unittest
import numpy as np
import os
import sys
import cv2

# Add the project root directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # Get the parent directory (project root)
if project_root not in sys.path:
    sys.path.append(project_root)

# Now imports should work correctly
from src.visualization.heatmap_generator import generate_heatmap
from src.visualization.formation_overlay import overlay_formation

class TestVisualization(unittest.TestCase):

    def setUp(self):
        # Setup mock player positions
        self.player_positions = [
            {'x': 100, 'y': 150, 'team': 'Team A'},
            {'x': 200, 'y': 250, 'team': 'Team A'},
            {'x': 300, 'y': 350, 'team': 'Team B'},
            {'x': 400, 'y': 450, 'team': 'Team B'},
        ]
        self.frame_shape = (500, 500)
        self.frame = np.zeros((self.frame_shape[0], self.frame_shape[1], 3), dtype=np.uint8)

    def test_generate_heatmap(self):
        # Test with no team filter
        heatmap = generate_heatmap(self.player_positions, frame_shape=self.frame_shape)
        self.assertEqual(heatmap.shape, self.frame_shape)
        self.assertTrue(np.any(heatmap > 0), "Heatmap should have non-zero values")
        
        # Test with team filter
        team_a_heatmap = generate_heatmap(self.player_positions, team_label='Team A', frame_shape=self.frame_shape)
        self.assertEqual(team_a_heatmap.shape, self.frame_shape)
        self.assertTrue(np.any(team_a_heatmap > 0), "Team A heatmap should have non-zero values")

    def test_overlay_formation(self):
        annotated_frame = overlay_formation(self.frame, self.player_positions)
        self.assertEqual(annotated_frame.shape, self.frame.shape)
        self.assertTrue(np.any(annotated_frame != self.frame), "Annotated frame should differ from original frame")
        
        # Test with empty positions list
        empty_frame = overlay_formation(self.frame, [])
        self.assertEqual(empty_frame.shape, self.frame.shape)
        # Should be unchanged since no positions to draw
        self.assertTrue(np.all(empty_frame == self.frame), "Empty positions should not modify the frame")

if __name__ == '__main__':
    unittest.main()