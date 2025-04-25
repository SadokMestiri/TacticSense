# Football Tactical Analysis System

This project is designed to analyze football highlight videos, generating insights such as player heatmaps and formation snapshots. The system utilizes computer vision techniques to detect players, classify them into teams based on jersey colors, and visualize their movements throughout the video.

## Project Structure

```
football-analysis
├── src
│   ├── data
│   │   ├── video_loader.py        # Functions to load video files and extract frames
│   │   └── preprocessing.py        # Functions for preprocessing frames (resizing, normalization)
│   ├── detection
│   │   ├── player_detector.py      # YOLOv8 model implementation for player detection
│   │   └── team_classifier.py      # Functions for jersey color clustering to classify teams
│   ├── tracking
│   │   └── position_tracker.py      # Tracks player positions across frames
│   ├── visualization
│   │   ├── heatmap_generator.py    # Generates heatmaps for each team
│   │   └── formation_overlay.py     # Overlays formation snapshots on selected frames
│   └── utils
│       ├── config.py               # Configuration settings for the project
│       └── helpers.py              # Utility functions for various tasks
├── models
│   └── yolov8_weights.pt           # Pre-trained weights for the YOLOv8 model
├── notebooks
│   ├── model_testing.ipynb         # Jupyter notebook for testing model performance
│   └── analysis_examples.ipynb     # Jupyter notebook for analysis techniques and visualizations
├── tests
│   ├── test_detection.py            # Unit tests for detection functionalities
│   └── test_visualization.py        # Unit tests for visualization functionalities
├── output                           # Directory for storing output files (heatmaps, annotated videos)
├── requirements.txt                 # Lists project dependencies
├── main.py                          # Entry point for the application
└── README.md                        # Project documentation
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/football-analysis.git
   cd football-analysis
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Download the YOLOv8 weights and place them in the `models` directory.

## Usage Guidelines

- To run the analysis, execute the `main.py` file:
  ```
  python main.py
  ```

- Modify the configuration settings in `src/utils/config.py` to adjust paths and parameters as needed.

## Overview of Functionalities

- **Video Loading**: Load and extract frames from highlight videos.
- **Player Detection**: Utilize YOLOv8 to detect players in each frame.
- **Team Classification**: Classify players into teams based on jersey colors using clustering techniques.
- **Position Tracking**: Track player positions across frames and save relevant data.
- **Heatmap Generation**: Create heatmaps visualizing player presence for each team.
- **Formation Overlay**: Overlay formation snapshots on selected frames, illustrating team structures.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for details.