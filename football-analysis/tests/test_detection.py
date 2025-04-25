import unittest
import numpy as np
import os
import sys
from unittest.mock import MagicMock, patch

# Add the project root directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # Get the parent directory (project root)
if project_root not in sys.path:
    sys.path.append(project_root)

# Now imports should work correctly
from src.detection.player_detector import PlayerDetector
from src.detection.team_classifier import TeamClassifier


class TestPlayerDetection(unittest.TestCase):

    def setUp(self):
        # Mock the detector to avoid actual model loading
        with patch('src.detection.player_detector.torch.hub.load') as mock_load:
            self.detector = PlayerDetector()
            self.detector.model = MagicMock()
            
            # Create a properly structured mock return value
            mock_results = MagicMock()
            # Structure the detection array to match what's expected by the for *box, conf, cls unpacking
            mock_results.xyxy = [np.array([[100, 150, 150, 250, 0.9, 0]])]
            self.detector.model.return_value = mock_results
            
        self.classifier = TeamClassifier()

    def test_player_detection(self):
        # Create a dummy frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Test detection
        boxes = self.detector.detect_players(frame)
        self.assertIsInstance(boxes, list)
        self.assertEqual(len(boxes), 1, "Should detect one player")
        self.assertEqual(boxes[0], (100, 150, 50, 100), "Bounding box should be (x, y, w, h) format")

    def test_team_classification(self):
        # Create a dummy frame with colored regions
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Create red and blue regions for team classification
        # Red team area
        frame[50:150, 100:150] = [0, 0, 255]
        # Blue team area
        frame[250:350, 300:350] = [255, 0, 0]
        
        # Sample bounding boxes
        sample_boxes = [(100, 50, 50, 100), (300, 250, 50, 100)]
        
        # Test classification
        team_labels = self.classifier.classify_teams(sample_boxes, frame)
        self.assertIsInstance(team_labels, list)
        self.assertEqual(len(team_labels), len(sample_boxes), "Team classification count should match boxes")
        self.assertTrue(all(label in ['Team A', 'Team B'] for label in team_labels), 
                        "Team labels should be either 'Team A' or 'Team B'")

if __name__ == '__main__':
    unittest.main()