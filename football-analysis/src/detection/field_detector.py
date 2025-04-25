import numpy as np

# Add CV2 stubs for IDE to recognize methods
try:
    import cv2
    # Test if methods exist
    cv2.cvtColor
    cv2.findContours
    cv2.convexHull
    cv2.bitwise_or
    cv2.threshold
    cv2.THRESH_BINARY
    cv2.Canny
    cv2.HoughLinesP
    cv2.arcLength
    cv2.approxPolyDP
    cv2.pointPolygonTest
    cv2.countNonZero
    cv2.moments
    cv2.resize
    cv2.INTER_LINEAR
    cv2.INTER_NEAREST
except (ImportError, AttributeError):
    print("Warning: Some cv2 methods not found, using stub implementation")
    # Create comprehensive stub implementation for IDE
    class CV2Stub:
        # Constants for color conversion
        COLOR_BGR2HSV = 40
        COLOR_BGR2GRAY = 6
        COLOR_BGR2RGB = 4
        COLOR_RGB2BGR = 4

        # Constants for thresholding
        THRESH_BINARY = 0
        THRESH_BINARY_INV = 1
        THRESH_TRUNC = 2
        THRESH_TOZERO = 3
        THRESH_TOZERO_INV = 4

        # Constants for morphology
        MORPH_OPEN = 2
        MORPH_CLOSE = 3
        MORPH_DILATE = 1
        MORPH_ERODE = 0

        # Constants for contour retrieval
        RETR_EXTERNAL = 0
        CHAIN_APPROX_SIMPLE = 1
        FONT_HERSHEY_SIMPLEX = 0

        # Constants for interpolation
        INTER_LINEAR = 1
        INTER_NEAREST = 0

        def __getattr__(self, name):
            return lambda *args, **kwargs: None

        def cvtColor(self, src, code, dstCn=None):
            """Stub for cv2.cvtColor"""
            if code == self.COLOR_BGR2GRAY:
                if hasattr(src, 'shape') and len(src.shape) == 3:
                    return np.zeros((src.shape[0], src.shape[1]), dtype=np.uint8)
            return np.zeros_like(src)

        def inRange(self, src, lowerb, upperb):
            """Stub for cv2.inRange"""
            if hasattr(src, 'shape'):
                if len(src.shape) == 3:
                    return np.zeros((src.shape[0], src.shape[1]), dtype=np.uint8)
                return np.zeros(src.shape[:2], dtype=np.uint8)
            return np.zeros((1, 1), dtype=np.uint8)

        def morphologyEx(self, src, op, kernel, dst=None, anchor=None,
                        iterations=None, borderType=None, borderValue=None):
            """Stub for cv2.morphologyEx"""
            return np.zeros_like(src)

        def dilate(self, src, kernel, dst=None, anchor=None, iterations=1,
                borderType=None, borderValue=None):
            """Stub for cv2.dilate"""
            return np.zeros_like(src)

        def erode(self, src, kernel, dst=None, anchor=None, iterations=1,
                borderType=None, borderValue=None):
            """Stub for cv2.erode"""
            return np.zeros_like(src)

        def findContours(self, image, mode, method, contours=None,
                        hierarchy=None, offset=None):
            """Stub for cv2.findContours"""
            return [], None

        def contourArea(self, contour, oriented=None):
            """Stub for cv2.contourArea"""
            return 0.0

        def minAreaRect(self, points):
            """Stub for cv2.minAreaRect"""
            return ((0, 0), (0, 0), 0)

        def boxPoints(self, box):
            """Stub for cv2.boxPoints"""
            return np.array([[0, 0], [0, 0], [0, 0], [0, 0]], dtype=np.float32)

        def convexHull(self, points, clockwise=None, returnPoints=True):
            """Stub for cv2.convexHull"""
            # Ensure output is a numpy array with correct shape for subsequent operations
            if isinstance(points, np.ndarray):
                 # Return a simplified version, e.g., first and last point if enough points
                 if points.shape[0] > 1:
                      return np.array([points[0], points[-1]], dtype=points.dtype).reshape((-1, 1, 2))
                 elif points.shape[0] == 1:
                      return points.reshape((-1, 1, 2))
            return np.array([[[0,0]]], dtype=np.int32) # Default fallback

        def drawContours(self, image, contours, contourIdx, color,
                        thickness=None, lineType=None, hierarchy=None,
                        maxLevel=None, offset=None):
            """Stub for cv2.drawContours"""
            return None # Modifies image in place, returns None

        def bitwise_and(self, src1, src2, dst=None, mask=None):
            """Stub for cv2.bitwise_and"""
            if hasattr(src1, 'shape'):
                # Ensure output shape matches broadcast rules if shapes differ
                try:
                    out_shape = np.broadcast(src1, src2).shape
                    return np.zeros(out_shape, dtype=src1.dtype)
                except ValueError: # If shapes are incompatible for broadcasting
                    return np.zeros_like(src1) # Fallback
            return np.zeros((1, 1), dtype=np.uint8)

        def bitwise_or(self, src1, src2, dst=None, mask=None):
            """Stub for cv2.bitwise_or"""
            if hasattr(src1, 'shape'):
                 try:
                    out_shape = np.broadcast(src1, src2).shape
                    return np.zeros(out_shape, dtype=src1.dtype)
                 except ValueError:
                    return np.zeros_like(src1)
            return np.zeros((1, 1), dtype=np.uint8)

        def threshold(self, src, thresh, maxval, type, dst=None):
            """Stub for cv2.threshold"""
            if hasattr(src, 'shape'):
                return 0, np.zeros_like(src)
            return 0, np.zeros((1, 1), dtype=np.uint8)

        def GaussianBlur(self, src, ksize, sigmaX, sigmaY=0, borderType=None):
            """Stub for cv2.GaussianBlur"""
            return src

        def Canny(self, image, threshold1, threshold2, edges=None, apertureSize=None, L2gradient=None):
            """Stub for cv2.Canny"""
            if hasattr(image, 'shape'):
                if len(image.shape) == 3:
                    return np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)
                return np.zeros(image.shape, dtype=np.uint8)
            return np.zeros((1, 1), dtype=np.uint8)

        def HoughLinesP(self, image, rho, theta, threshold, lines=None,
                       minLineLength=None, maxLineGap=None):
            """Stub for cv2.HoughLinesP"""
            # Return None or an empty array if no lines are expected in stub mode
            # Or return a single dummy line if subsequent code needs at least one line
            # return None
            return np.array([[[0, 0, 1, 1]]], dtype=np.int32) # Return one dummy line

        def line(self, img, pt1, pt2, color, thickness=1, lineType=8, shift=0):
            """Stub for cv2.line"""
            return img

        def arcLength(self, curve, closed):
            """Stub for cv2.arcLength"""
            return 0.0 # Return a float

        def approxPolyDP(self, curve, epsilon, closed):
            """Stub for cv2.approxPolyDP"""
            if isinstance(curve, np.ndarray):
                 # Return shape similar to expected output (N, 1, 2)
                 if curve.shape[0] > 0:
                      return curve.reshape((-1, 1, 2))
            return np.array([[[0,0]]], dtype=np.int32) # Default fallback

        def pointPolygonTest(self, contour, pt, measureDist):
            """Stub for cv2.pointPolygonTest"""
            return 1.0

        def countNonZero(self, src):
            """Stub for cv2.countNonZero"""
            if hasattr(src, 'size'):
                return src.size // 2
            return 1

        def moments(self, array, binaryImage=False):
             """Stub for cv2.moments"""
             return {'m00': 1.0, 'm10': 0.0, 'm01': 0.0,
                     'mu20': 0.0, 'mu11': 0.0, 'mu02': 0.0,
                     'mu30': 0.0, 'mu21': 0.0, 'mu12': 0.0, 'mu03': 0.0,
                     'nu20': 0.0, 'nu11': 0.0, 'nu02': 0.0,
                     'nu30': 0.0, 'nu21': 0.0, 'nu12': 0.0, 'nu03': 0.0}

        def resize(self, src, dsize, fx=None, fy=None, interpolation=None):
            """Stub for cv2.resize"""
            # Return an array of the target size
            if dsize is not None and len(dsize) == 2:
                 # Check if src has channel dimension
                 if len(src.shape) == 3:
                      return np.zeros((dsize[1], dsize[0], src.shape[2]), dtype=src.dtype)
                 else:
                      return np.zeros((dsize[1], dsize[0]), dtype=src.dtype)
            # If resizing by factors fx, fy (approximate)
            elif fx is not None and fy is not None:
                 new_h = int(src.shape[0] * fy)
                 new_w = int(src.shape[1] * fx)
                 if len(src.shape) == 3:
                      return np.zeros((new_h, new_w, src.shape[2]), dtype=src.dtype)
                 else:
                      return np.zeros((new_h, new_w), dtype=src.dtype)
            return src # Fallback

    cv2 = CV2Stub()


class FieldDetector:
    """Detects the soccer field boundaries using green color and selected outermost white lines"""

    def __init__(self, detection_width=640): # Add target width for detection
        self.field_mask = None
        self.field_contour = None
        self.boundary_lines = {'top': None, 'bottom': None, 'left': None, 'right': None}
        self.field_detected = False
        self.history_size = 3
        self.line_history = {'top': [], 'bottom': [], 'left': [], 'right': []}
        self.last_green_centroid = None
        self.last_green_area = 0
        self.frame_counter = 0
        self.detection_interval = 2
        self.detection_width = detection_width # Store target width
        self.original_shape = None # To store original frame shape for scaling back

        # Parameters
        self.min_field_area_ratio = 0.10
        self.canny_low_thresh = 50
        self.canny_high_thresh = 150
        self.hough_threshold = 30
        self.hough_min_line_length = 30
        self.hough_max_line_gap = 40
        self.line_angle_tolerance = 12
        self.green_close_kernel_size = (7, 7)
        self.green_open_kernel_size = (3, 3)
        self.camera_shift_threshold = 0.15
        self.camera_area_change_threshold = 0.30

    def _get_line_params(self, x1, y1, x2, y2):
        """Calculate slope (m) and intercept (c) or vertical line x-value"""
        if abs(x2 - x1) < 1e-6: # Vertical line check robust to float errors
            return np.inf, x1
        else:
            # Ensure denominator is not zero before division
            if abs(x2 - x1) < 1e-9: return None # Avoid division by zero if somehow missed
            m = (y2 - y1) / (x2 - x1)
            c = y1 - m * x1
            return m, c

    def _get_line_angle(self, x1, y1, x2, y2):
        """Calculate angle of the line in degrees"""
        # Ensure denominator is not zero
        dx = x2 - x1
        dy = y2 - y1
        if abs(dx) < 1e-9 and abs(dy) < 1e-9: return 0 # Avoid atan2(0,0)
        angle = np.degrees(np.arctan2(dy, dx))
        return angle

    def _intersect(self, line1_params, line2_params):
        """Find intersection point of two lines given (m, c) or (inf, x)"""
        if line1_params is None or line2_params is None: return None
        m1, c1 = line1_params
        m2, c2 = line2_params

        # Check for parallel lines (including two vertical lines)
        if m1 == m2: return None # Handles inf == inf and finite m1 == finite m2
        # Check if slopes are extremely close (nearly parallel)
        if m1 != np.inf and m2 != np.inf and abs(m1 - m2) < 1e-6: return None

        if m1 == np.inf: # Line 1 is vertical
            x = c1
            if m2 == np.inf: return None # Should be caught by m1==m2, but safety check
            y = m2 * x + c2
        elif m2 == np.inf: # Line 2 is vertical
            x = c2
            y = m1 * x + c1
        else: # General case
            # Ensure denominator is not zero
            if abs(m1 - m2) < 1e-9: return None
            x = (c2 - c1) / (m1 - m2)
            y = m1 * x + c1

        return int(round(x)), int(round(y))

    def _select_outermost_line(self, lines, side):
        """Select the single most boundary-like line from a cluster"""
        if not lines:
            return None

        best_line = None
        if side == 'top':
            min_y = float('inf')
            for line in lines:
                avg_y = (line[1] + line[3]) / 2
                if avg_y < min_y:
                    min_y = avg_y
                    best_line = line
        elif side == 'bottom':
            max_y = float('-inf')
            for line in lines:
                avg_y = (line[1] + line[3]) / 2
                if avg_y > max_y:
                    max_y = avg_y
                    best_line = line
        elif side == 'left':
            min_x = float('inf')
            for line in lines:
                avg_x = (line[0] + line[2]) / 2
                if avg_x < min_x:
                    min_x = avg_x
                    best_line = line
        elif side == 'right':
            max_x = float('-inf')
            for line in lines:
                avg_x = (line[0] + line[2]) / 2
                if avg_x > max_x:
                    max_x = avg_x
                    best_line = line

        if best_line is not None:
            return self._get_line_params(best_line[0], best_line[1], best_line[2], best_line[3])
        else:
            return None

    def detect_field(self, frame):
        self.frame_counter += 1
        self.original_shape = frame.shape # Store original shape

        # Frame Skipping
        if self.field_detected and self.frame_counter % self.detection_interval != 0:
            # Ensure contour is scaled correctly if returning cached result
            if self.field_contour is not None and self.original_shape is not None:
                 # Assuming self.field_contour is stored in the scaled-down coordinate space
                 scale_x = self.original_shape[1] / self.detection_width
                 scale_y = self.original_shape[0] / (self.detection_width * self.original_shape[0] / self.original_shape[1]) # Maintain aspect ratio
                 scaled_contour = (self.field_contour * [scale_x, scale_y]).astype(np.int32)
                 # We need a mask of the original size if filtering happens later
                 scaled_mask = None
                 if self.field_mask is not None:
                      scaled_mask = cv2.resize(self.field_mask, (self.original_shape[1], self.original_shape[0]), interpolation=cv2.INTER_NEAREST)
                 return scaled_mask, scaled_contour
            else:
                 return self.field_mask, self.field_contour # Return whatever was cached

        # --- Downscale Frame ---
        h_orig, w_orig, _ = frame.shape
        scale_factor = self.detection_width / w_orig
        h_new = int(h_orig * scale_factor)
        w_new = self.detection_width
        try:
            frame_small = cv2.resize(frame, (w_new, h_new), interpolation=cv2.INTER_LINEAR)
        except Exception as resize_error:
             print(f"Error resizing frame: {resize_error}. Using original frame.")
             frame_small = frame # Fallback to original if resize fails
             h_new, w_new, _ = frame_small.shape # Update dimensions

        height, width, _ = frame_small.shape # Use dimensions of the potentially resized frame
        # ---

        # Default to previous detection (in scaled coordinates)
        final_mask_small = self.field_mask
        final_contour_small = self.field_contour

        try:
            # 1. GREEN FIELD DETECTION & CAMERA SHIFT CHECK (on frame_small)
            hsv = cv2.cvtColor(frame_small, cv2.COLOR_BGR2HSV)
            # ... rest of green detection ...
            lower_green = np.array([30, 40, 40])
            upper_green = np.array([90, 255, 255])
            green_mask = cv2.inRange(hsv, lower_green, upper_green)
            kernel_close = np.ones(self.green_close_kernel_size, np.uint8)
            kernel_open = np.ones(self.green_open_kernel_size, np.uint8)
            green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_CLOSE, kernel_close)
            green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_OPEN, kernel_open)
            contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # --- Early Exit 1 ---
            if not contours:
                 print("No green contours found.")
                 return self.field_mask, self.field_contour # Return previous scaled mask/contour

            min_area = height * width * self.min_field_area_ratio
            large_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]

            # --- Early Exit 2 ---
            if not large_contours:
                 print("No large green contours found.")
                 return self.field_mask, self.field_contour # Return previous scaled mask/contour

            green_contour = max(large_contours, key=cv2.contourArea)
            current_green_area = cv2.contourArea(green_contour)

            # --- Define the fallback function ---
            def fallback_to_green_hull():
                print("Falling back to green contour convex hull.")
                try:
                    # Use convex hull of the largest green contour
                    field_poly = cv2.convexHull(green_contour)
                    # Create mask from this hull
                    fallback_mask = np.zeros_like(green_mask)
                    cv2.drawContours(fallback_mask, [field_poly], 0, 255, -1)
                    # Extract contour from the mask
                    fallback_contours, _ = cv2.findContours(fallback_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    if fallback_contours:
                        fallback_contour = max(fallback_contours, key=cv2.contourArea)
                        # Update state with scaled results
                        self.field_mask = fallback_mask
                        self.field_contour = fallback_contour
                        self.field_detected = True
                        # Scale back for return
                        scale_x = self.original_shape[1] / width
                        scale_y = self.original_shape[0] / height
                        scaled_contour = (self.field_contour * [scale_x, scale_y]).astype(np.int32)
                        scaled_mask = cv2.resize(self.field_mask, (self.original_shape[1], self.original_shape[0]), interpolation=cv2.INTER_NEAREST)
                        return scaled_mask, scaled_contour
                except Exception as hull_error:
                    print(f"Error during convex hull fallback: {hull_error}")
                # If fallback fails, return previous cached result
                return self.field_mask, self.field_contour
            # ---

            # ... Camera shift check (using scaled dimensions width, height) ...
            M = cv2.moments(green_contour)
            current_green_centroid = None
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                current_green_centroid = (cX, cY)

            reset_history = False
            if self.last_green_centroid and current_green_centroid:
                dx = abs(current_green_centroid[0] - self.last_green_centroid[0])
                dy = abs(current_green_centroid[1] - self.last_green_centroid[1])
                area_change_ratio = abs(current_green_area - self.last_green_area) / (self.last_green_area + 1e-6)

                if (dx > width * self.camera_shift_threshold or
                    dy > height * self.camera_shift_threshold or
                    area_change_ratio > self.camera_area_change_threshold):
                    reset_history = True
                    self.line_history = {'top': [], 'bottom': [], 'left': [], 'right': []}

            self.last_green_centroid = current_green_centroid
            self.last_green_area = current_green_area
            green_mask_refined = np.zeros_like(green_mask)
            cv2.drawContours(green_mask_refined, [green_contour], 0, 255, -1)


            # 2. EDGE DETECTION (on frame_small)
            gray = cv2.cvtColor(frame_small, cv2.COLOR_BGR2GRAY)
            # ... rest of edge detection ...
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blurred, self.canny_low_thresh, self.canny_high_thresh)
            edges_on_field = cv2.bitwise_and(edges, green_mask_refined)


            # 3. HOUGH LINE TRANSFORM (on frame_small)
            lines = cv2.HoughLinesP(edges_on_field, 1, np.pi / 180,
                                   threshold=self.hough_threshold,
                                   minLineLength=self.hough_min_line_length,
                                   maxLineGap=self.hough_max_line_gap)

            # --- Fallback if no lines detected ---
            if lines is None:
                return fallback_to_green_hull()

            # 4. FILTER AND CLUSTER LINES (using scaled dimensions height, width)
            # ... (same logic) ...
            line_clusters = {'top': [], 'bottom': [], 'left': [], 'right': []}
            y_center = height / 2
            x_center = width / 2
            for line in lines:
                x1, y1, x2, y2 = line[0]
                angle = self._get_line_angle(x1, y1, x2, y2)
                if angle is None: continue
                mid_y = (y1 + y2) / 2
                mid_x = (x1 + x2) / 2
                if abs(angle) < self.line_angle_tolerance or abs(angle - 180) < self.line_angle_tolerance or abs(angle + 180) < self.line_angle_tolerance:
                    if mid_y < y_center: line_clusters['top'].append(line[0])
                    else: line_clusters['bottom'].append(line[0])
                elif abs(angle - 90) < self.line_angle_tolerance or abs(angle + 90) < self.line_angle_tolerance:
                    if mid_x < x_center: line_clusters['left'].append(line[0])
                    else: line_clusters['right'].append(line[0])


            # 5. SELECT OUTERMOST LINE & TEMPORAL SMOOTHING
            # ... (same logic, operates on scaled lines) ...
            current_boundary_lines = {}
            updated_sides = 0
            for side, cluster_lines in line_clusters.items():
                selected_params = self._select_outermost_line(cluster_lines, side)
                if selected_params:
                    if not reset_history:
                        self.line_history[side].append(selected_params)
                        if len(self.line_history[side]) > self.history_size:
                            self.line_history[side].pop(0)
                    else:
                         self.line_history[side] = [selected_params]
                    hist_params = [p for p in self.line_history[side] if p is not None]
                    if not hist_params: smooth_params = selected_params
                    else:
                         hist_slopes = [p[0] for p in hist_params if p[0] != np.inf]
                         hist_intercepts = [p[1] for p in hist_params if p[0] != np.inf]
                         hist_vertical_x = [p[1] for p in hist_params if p[0] == np.inf]
                         if len(hist_vertical_x) > len(hist_slopes):
                              if not hist_vertical_x: smooth_params = selected_params
                              else: smooth_params = np.inf, np.mean(hist_vertical_x)
                         elif hist_slopes: smooth_params = np.mean(hist_slopes), np.mean(hist_intercepts)
                         else:
                              if not hist_vertical_x: smooth_params = selected_params
                              else: smooth_params = np.inf, np.mean(hist_vertical_x)
                    current_boundary_lines[side] = smooth_params
                    self.boundary_lines[side] = smooth_params
                    updated_sides += 1
                else:
                    if not reset_history: current_boundary_lines[side] = self.boundary_lines.get(side, None)
                    else: current_boundary_lines[side] = None


            # --- Fallback if not enough valid sides found ---
            valid_sides = sum(1 for params in current_boundary_lines.values() if params is not None)
            if valid_sides < 3:
                 print(f"Only {valid_sides} boundary lines found.")
                 return fallback_to_green_hull()

            # 6. CALCULATE CORNERS (in scaled coordinates)
            # ... (same logic) ...
            corners = []
            c_top_left = self._intersect(current_boundary_lines.get('top'), current_boundary_lines.get('left'))
            c_top_right = self._intersect(current_boundary_lines.get('top'), current_boundary_lines.get('right'))
            c_bottom_left = self._intersect(current_boundary_lines.get('bottom'), current_boundary_lines.get('left'))
            c_bottom_right = self._intersect(current_boundary_lines.get('bottom'), current_boundary_lines.get('right'))
            valid_corners = [c for c in [c_top_left, c_top_right, c_bottom_right, c_bottom_left] if c is not None]

            # --- Fallback if not enough corners found ---
            if len(valid_corners) < 3:
                 print("Failed to calculate enough corners.")
                 return fallback_to_green_hull()

            corners_clipped = []
            for x, y in valid_corners:
                 cx = np.clip(x, 0, width - 1)
                 cy = np.clip(y, 0, height - 1)
                 corners_clipped.append([cx, cy])

            if len(corners_clipped) >= 3:
                 hull_points = np.array(corners_clipped, dtype=np.int32)
                 try: field_poly = cv2.convexHull(hull_points)
                 except Exception: field_poly = hull_points.reshape((-1, 1, 2))
            else: # Should not happen due to check above, but safety fallback
                 print("Less than 3 clipped corners.")
                 return fallback_to_green_hull()


            # 7. CREATE FINAL MASK AND CONTOUR (on frame_small)
            final_mask_small = np.zeros_like(green_mask)
            cv2.drawContours(final_mask_small, [field_poly], 0, 255, -1)

            final_area = cv2.countNonZero(final_mask_small)
            # --- Fallback if final area is too small (compared to green area) ---
            # Use a ratio of the green area as threshold, e.g., 50%
            if final_area < (current_green_area * 0.5):
                 print("Final mask area significantly smaller than green area.")
                 return fallback_to_green_hull()

            final_contours, _ = cv2.findContours(final_mask_small, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            # --- Fallback if no contour found from final mask ---
            if not final_contours:
                 print("No contour found from final mask.")
                 return fallback_to_green_hull()

            final_contour_small = max(final_contours, key=cv2.contourArea)

            # Update state with scaled results from LINE DETECTION
            self.field_mask = final_mask_small
            self.field_contour = final_contour_small
            self.field_detected = True

            # --- Scale results back to original frame size ---
            scale_x = self.original_shape[1] / width
            scale_y = self.original_shape[0] / height
            final_contour_orig = (final_contour_small * [scale_x, scale_y]).astype(np.int32)
            # Resize mask using nearest neighbor to keep it binary
            final_mask_orig = cv2.resize(final_mask_small, (self.original_shape[1], self.original_shape[0]), interpolation=cv2.INTER_NEAREST)

            return final_mask_orig, final_contour_orig

        except Exception as e:
            print(f"Error in field detection: {e}")
            # --- Generic Exception Fallback ---
            # Try green hull fallback even on generic error if green_contour exists
            if 'green_contour' in locals() and green_contour is not None:
                 print("Generic error occurred, attempting green hull fallback.")
                 return fallback_to_green_hull()
            else:
                 # If green contour wasn't even found, return cached
                 print("Generic error before green contour found, returning cached.")
                 # Scale back cached result if possible
                 if self.field_contour is not None and self.original_shape is not None:
                      scale_x = self.original_shape[1] / self.detection_width
                      scale_y = self.original_shape[0] / (self.detection_width * self.original_shape[0] / self.original_shape[1])
                      scaled_contour = (self.field_contour * [scale_x, scale_y]).astype(np.int32)
                      scaled_mask = None
                      if self.field_mask is not None:
                           scaled_mask = cv2.resize(self.field_mask, (self.original_shape[1], self.original_shape[0]), interpolation=cv2.INTER_NEAREST)
                      return scaled_mask, scaled_contour
                 else:
                      return self.field_mask, self.field_contour # Return unscaled cache


    def filter_players(self, bounding_boxes):
        """Filter out detections outside the detected field polygon (using original coordinates)"""
        # This method receives the *original size* bounding boxes
        # It needs the field contour scaled to the *original size*
        _, current_contour_orig = self.detect_field(np.zeros(self.original_shape, dtype=np.uint8)) # Get latest scaled contour

        if current_contour_orig is None:
             print("Warning: No field contour available for filtering.")
             return bounding_boxes # Don't filter if no contour

        filtered_boxes = []
        if len(current_contour_orig) > 0:
            contour_for_test = current_contour_orig.reshape(-1, 1, 2) if len(current_contour_orig.shape) == 2 else current_contour_orig

            for box in bounding_boxes:
                x, y, w, h = box
                feet_x, feet_y = int(x + w//2), int(y + h)

                try:
                    test_result = cv2.pointPolygonTest(contour_for_test, (float(feet_x), float(feet_y)), False)
                    if test_result >= 0:
                         filtered_boxes.append(box)
                    else:
                         center_x, center_y = int(x + w//2), int(y + h//2)
                         test_result_center = cv2.pointPolygonTest(contour_for_test, (float(center_x), float(center_y)), False)
                         if test_result_center >= 0:
                              filtered_boxes.append(box)
                except Exception as poly_test_error:
                     print(f"Error during pointPolygonTest: {poly_test_error}")
                     filtered_boxes.append(box)
        else:
             return bounding_boxes

        return filtered_boxes