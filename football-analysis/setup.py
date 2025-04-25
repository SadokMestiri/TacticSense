from setuptools import setup, find_packages

setup(
    name="football-analysis",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0",
        "opencv-python>=4.5.0",
        "torch>=1.9.0",
        "torchvision>=0.10.0",
        "seaborn>=0.11.0",
        "scikit-learn>=0.24.0",
        "matplotlib>=3.4.0",
        "pillow>=8.2.0",
        "ffmpeg-python>=0.2.0",
        "ultralytics>=8.0.0"
    ],
)