import os
from src.data.video_loader import load_video
from src.data.preprocessing import preprocess_frame
from src.detection.player_detector import detect_players
from src.detection.team_classifier import classify_teams
from src.tracking.position_tracker import track_positions
from src.visualization.heatmap_generator import generate_heatmaps
from src.visualization.formation_overlay import overlay_formations
from src.utils.config import Config

def main():
    # Load video
    video_path = Config.VIDEO_PATH
    frames = load_video(video_path)

    player_positions = []

    # Process each frame
    for frame_number, frame in enumerate(frames):
        # Preprocess frame
        processed_frame = preprocess_frame(frame)

        # Detect players
        bounding_boxes = detect_players(processed_frame)

        # Classify teams based on jersey color
        team_labels = classify_teams(processed_frame, bounding_boxes)

        # Track player positions
        positions = track_positions(bounding_boxes, team_labels, frame_number)
        player_positions.extend(positions)

    # Generate heatmaps for each team
    generate_heatmaps(player_positions)

    # Overlay formations on selected frames
    overlay_formations(frames, player_positions)

if __name__ == "__main__":
    main()