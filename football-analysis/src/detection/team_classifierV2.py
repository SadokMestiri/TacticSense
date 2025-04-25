# Add CV2 stubs for IDE to recognize methods
try:
    import cv2
    cv2.cvtColor
    cv2.COLOR_BGR2HSV
    cv2.line  # For drawing formation lines
except (ImportError, AttributeError):
    print("Warning: Some cv2 methods not found, using stub implementation")
    # Create comprehensive stub implementation for IDE
    class CV2Stub:
        # Constants for color conversion
        COLOR_BGR2HSV = 40
        COLOR_HSV2BGR = 54
        COLOR_BGR2RGB = 4
        COLOR_RGB2BGR = 4
        
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
            
        def cvtColor(self, src, code, dstCn=None):
            """Stub for cv2.cvtColor"""
            return src
            
        def calcHist(self, images, channels, mask, histSize, ranges, hist=None, accumulate=False):
            """Stub for cv2.calcHist"""
            return np.ones(tuple(histSize), dtype=np.float32)
            
        def minMaxLoc(self, src, mask=None):
            """Stub for cv2.minMaxLoc"""
            return 0.0, 1.0, (0, 0), (0, 0)
        
        def inRange(self, src, lowerb, upperb):
            """Stub for cv2.inRange"""
            if hasattr(src, 'shape'):
                if len(src.shape) == 3:
                    return np.zeros((src.shape[0], src.shape[1]), dtype=np.uint8)
                return np.zeros(src.shape[:2], dtype=np.uint8)
            return np.zeros((1, 1), dtype=np.uint8)
            
        def countNonZero(self, src):
            """Stub for cv2.countNonZero"""
            return 1
            
        def line(self, img, pt1, pt2, color, thickness=1, lineType=8, shift=0):
            """Stub for cv2.line"""
            return img
            
        def putText(self, img, text, org, fontFace, fontScale, color, 
                   thickness=1, lineType=8, bottomLeftOrigin=False):
            """Stub for cv2.putText"""
            return img
            
        FONT_HERSHEY_SIMPLEX = 0
    
    cv2 = CV2Stub()

import numpy as np
try:
    from sklearn.cluster import KMeans
except ImportError:
    # Simple KMeans fallback implementation
    class KMeans:
        def __init__(self, n_clusters=2, random_state=None):
            self.n_clusters = n_clusters
            self.labels_ = None
            self.cluster_centers_ = None
            
        def fit(self, X):
            # Very simple implementation - just assign alternating labels
            if X.shape[0] == 0:
                self.labels_ = []
                self.cluster_centers_ = np.zeros((self.n_clusters, X.shape[1]))
            else:
                self.labels_ = [i % self.n_clusters for i in range(X.shape[0])]
                self.cluster_centers_ = []
                for i in range(self.n_clusters):
                    points = [X[j] for j in range(X.shape[0]) if self.labels_[j] == i]
                    if points:
                        self.cluster_centers_.append(np.mean(points, axis=0))
                    else:
                        self.cluster_centers_.append(np.zeros(X.shape[1]))
                self.cluster_centers_ = np.array(self.cluster_centers_)
            return self

class FormationData:
    """Structure to store team formation information"""
    def __init__(self):
        self.team_a_positions = []
        self.team_b_positions = []
        self.formation_a = "Unknown"
        self.formation_b = "Unknown"

class TeamClassifierV2:
    """Team classifier with formation detection"""
    
    def __init__(self):
        self.team_colors = {}
        self.frame_count = 0
        self.formation_data = FormationData()
        self.field_detector = None  # Will be set externally
    
    def set_field_detector(self, field_detector):
        """Set field detector reference for excluding off-field players"""
        self.field_detector = field_detector
    
    def classify_teams(self, bounding_boxes, frame):
        """
        Classify players into teams and determine formations
        
        Args:
            bounding_boxes: List of bounding boxes (x, y, w, h)
            frame: Image frame
            
        Returns:
            List of team labels ('Team A' or 'Team B')
        """
        if not bounding_boxes:
            return []
        
        self.frame_count += 1
        jersey_colors = self._extract_jersey_color(frame, bounding_boxes)
        
        # Initialize team colors if not yet established
        if not self.team_colors and len(jersey_colors) >= 4:
            self._initialize_team_colors(jersey_colors)
        
        # Classify players based on jersey color similarity
        team_labels = []
        team_a_positions = []
        team_b_positions = []
        
        for i, color in enumerate(jersey_colors):
            team = self._classify_by_color(color)
            team_labels.append(team)
            
            # Store positions for formation analysis (x, y represent bottom center of player)
            if i < len(bounding_boxes):
                x, y, w, h = bounding_boxes[i]
                if team == 'Team A':
                    team_a_positions.append((x + w//2, y + h))
                elif team == 'Team B':
                    team_b_positions.append((x + w//2, y + h))
        
        # Update formation data
        self.formation_data.team_a_positions = team_a_positions
        self.formation_data.team_b_positions = team_b_positions
        
        # Analyze formations
        self._analyze_formations()
        
        return team_labels
    
    def _extract_jersey_color(self, frame, bounding_boxes):
        """Extract dominant color from jersey area"""
        colors = []
        
        for box in bounding_boxes:
            try:
                x, y, w, h = box
                
                # Focus on upper body for jersey color
                jersey_y = int(y + h * 0.2)  # Start 20% down from top (below head)
                jersey_h = int(h * 0.4)      # Take ~40% of height (jersey area)
                
                # Ensure coordinates are within frame bounds
                y_start = max(0, jersey_y)
                y_end = min(frame.shape[0], jersey_y + jersey_h)
                x_start = max(0, x)
                x_end = min(frame.shape[1], x + w)
                
                if y_end <= y_start or x_end <= x_start:
                    colors.append([0, 0, 0])
                    continue
                
                # Extract jersey region
                jersey = frame[y_start:y_end, x_start:x_end]
                
                if jersey.size > 0:
                    # Simple approach: use average color
                    avg_color = np.mean(jersey, axis=(0, 1))
                    colors.append(avg_color)
                else:
                    colors.append([0, 0, 0])
            except Exception as e:
                print(f"Error extracting jersey color: {e}")
                colors.append([0, 0, 0])
        
        return np.array(colors)
    
    def _initialize_team_colors(self, jersey_colors):
        """Initialize team colors using clustering"""
        try:
            # Filter out black/white colors that might be refs or noise
            valid_colors = []
            for color in jersey_colors:
                brightness = np.mean(color)
                if 20 < brightness < 200:  # Skip very dark/bright colors
                    valid_colors.append(color)
            
            if len(valid_colors) < 4:  # Need enough samples
                return False
            
            # Use KMeans to find team colors
            kmeans = KMeans(n_clusters=2)
            kmeans.fit(valid_colors)
            
            # Store team colors
            self.team_colors = {
                'Team A': kmeans.cluster_centers_[0],
                'Team B': kmeans.cluster_centers_[1]
            }
            
            print(f"Team colors initialized: A={self.team_colors['Team A']}, B={self.team_colors['Team B']}")
            return True
        except Exception as e:
            print(f"Error initializing team colors: {e}")
            return False
    
    def _classify_by_color(self, color):
        """Classify a player based on jersey color"""
        if not self.team_colors:
            return 'Unknown'
        
        # Calculate color similarity to each team
        dist_to_a = np.linalg.norm(color - self.team_colors['Team A'])
        dist_to_b = np.linalg.norm(color - self.team_colors['Team B'])
        
        # Classify based on closest team color
        if dist_to_a < dist_to_b:
            return 'Team A'
        else:
            return 'Team B'
    
    def _analyze_formations(self):
        """Analyze team formations based on player positions"""
        # Analyze Team A formation
        if len(self.formation_data.team_a_positions) >= 7:  # Need enough players
            # Sort players by y-position (from goal line to goal line)
            sorted_positions = sorted(self.formation_data.team_a_positions, key=lambda pos: pos[1])
            
            # Count players in different zones (defense, midfield, attack)
            defenders = 0
            midfielders = 0 
            attackers = 0
            
            field_height = 100  # Placeholder - should use actual field dimensions
            for _, y in sorted_positions:
                rel_pos = y / field_height  # Relative position on field
                
                if rel_pos < 0.33:  # Defense zone
                    defenders += 1
                elif rel_pos < 0.66:  # Midfield zone
                    midfielders += 1
                else:  # Attack zone
                    attackers += 1
            
            # Set formation string (e.g., 4-4-2, 4-3-3, etc.)
            self.formation_data.formation_a = f"{defenders}-{midfielders}-{attackers}"
        else:
            self.formation_data.formation_a = "Unknown"
            
        # Analyze Team B formation (similar to Team A)
        if len(self.formation_data.team_b_positions) >= 7:
            sorted_positions = sorted(self.formation_data.team_b_positions, key=lambda pos: pos[1])
            
            defenders = 0
            midfielders = 0 
            attackers = 0
            
            field_height = 100
            for _, y in sorted_positions:
                rel_pos = y / field_height
                
                if rel_pos < 0.33:
                    defenders += 1
                elif rel_pos < 0.66:
                    midfielders += 1
                else:
                    attackers += 1
            
            self.formation_data.formation_b = f"{defenders}-{midfielders}-{attackers}"
        else:
            self.formation_data.formation_b = "Unknown"
    
    def draw_formations(self, frame):
        """
        Draw team formations on the frame
        
        Args:
            frame: Video frame to draw on
            
        Returns:
            Frame with formations drawn
        """
        result = frame.copy()
        
        # Draw Team A connections (red)
        for i, pos1 in enumerate(self.formation_data.team_a_positions):
            for j, pos2 in enumerate(self.formation_data.team_a_positions):
                if i < j:  # Draw each connection only once
                    cv2.line(result, 
                            (int(pos1[0]), int(pos1[1])), 
                            (int(pos2[0]), int(pos2[1])), 
                            (0, 0, 255), 1)
        
        # Draw Team B connections (blue)
        for i, pos1 in enumerate(self.formation_data.team_b_positions):
            for j, pos2 in enumerate(self.formation_data.team_b_positions):
                if i < j:
                    cv2.line(result, 
                            (int(pos1[0]), int(pos1[1])), 
                            (int(pos2[0]), int(pos2[1])), 
                            (255, 0, 0), 1)
        
        # Add formation labels
        cv2.putText(result, f"Team A: {self.formation_data.formation_a}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(result, f"Team B: {self.formation_data.formation_b}", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        
        return result