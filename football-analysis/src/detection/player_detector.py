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
            
        def VideoCapture(self, *args, **kwargs):
            class DummyCapture:
                def isOpened(self):
                    return False
                def read(self):
                    return False, None
                def release(self):
                    pass
            return DummyCapture()
    cv2 = CV2Stub()

# Import torch with error handling
try:
    import torch
except ImportError:
    print("Error importing PyTorch. Make sure it's installed properly.")
    # Create a stub for torch if it can't be imported
    class TorchStub:
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
        
        def load(self, *args, **kwargs):
            return self
            
        @property
        def hub(self):
            return self
    torch = TorchStub()

# Import config with fallback
try:
    from src.utils.config import MODEL_PATH
except ImportError:
    print("Error importing config. Using default model path.")
    MODEL_PATH = os.path.join(os.path.dirname(parent_dir), 'models', 'yolov8_weights.pt')

class PlayerDetector:
    def __init__(self, model_path=None):
        try:
            # Try the newer YOLO API first (preferred method)
            print("Attempting to load YOLOv8 model using current API...")
            from ultralytics import YOLO
            self.model = YOLO('yolov8n.pt')  # This will auto-download if needed
            print("YOLOv8n model loaded successfully via YOLO class")
        except ImportError:
            # Fall back to older torch.hub method
            try:
                print("Falling back to torch.hub for YOLOv8 model...")
                self.model = torch.hub.load('ultralytics/yolov8', 'yolov8n', trust_repo=True)
                print("Standard YOLOv8n model loaded successfully via torch.hub")
            except Exception as e:
                print(f"Error loading standard model: {e}")
                self.model = None
                print("No model loaded. Detection will not work.")

    def detect_players(self, frame):
        """
        Detect players in a frame using YOLOv8
        
        Parameters:
            frame: Input image frame
        
        Returns:
            List of bounding boxes in (x, y, w, h) format
        """
        if self.model is None:
            print("Model not loaded properly")
            return []
            
        try:
            results = self.model(frame)
            bounding_boxes = []
            
            # Handle different result formats based on which YOLO API is used
            if hasattr(results, 'xyxy'):  # Old torch.hub format
                detections = results.xyxy[0]
                for *box, conf, cls in detections:
                    if conf > 0.5 and int(cls) == 0:  # Only consider 'person' class with confidence > 0.5
                        x1, y1, x2, y2 = map(int, box)
                        bounding_boxes.append((x1, y1, x2-x1, y2-y1))  # Convert to x,y,w,h format
            else:  # New ultralytics format
                # Get the first result (assuming single image input)
                result = results[0] if isinstance(results, list) else results
                
                # Extract boxes and filter for person class (class 0)
                for box in result.boxes:
                    if box.cls == 0 and box.conf > 0.5:  # Person class with confidence > 0.5
                        # Get coordinates (convert to int)
                        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                        bounding_boxes.append((x1, y1, x2-x1, y2-y1))  # Convert to x,y,w,h format

            return bounding_boxes
        except Exception as e:
            print(f"Error in player detection: {e}")
            return []

    def process_video(self, video_path):
        """
        Process entire video and detect players in each frame
        
        Parameters:
            video_path: Path to video file
            
        Returns:
            List of tuples containing (frame, bounding_boxes)
        """
        if not os.path.exists(video_path):
            print(f"Video file not found: {video_path}")
            return []
            
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print(f"Could not open video: {video_path}")
                return []
                
            frames = []

            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                bounding_boxes = self.detect_players(frame)
                frames.append((frame, bounding_boxes))

            cap.release()
            return frames
        except Exception as e:
            print(f"Error processing video: {e}")
            return []