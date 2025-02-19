# Video Processing Tools

This repository contains two powerful video processing tools:
1. Video Generator - Create modified versions of videos with various effects
2. Video Comparison Tool - Compare and analyze differences between two videos

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Tools Description](#tools-description)
- [Requirements](#requirements)
- [Contributing](#contributing)
- [License](#license)

## Features

### Video Generator
- Multiple effect options:
  - Speed modification
  - Color adjustments (hue, saturation, brightness)
  - Border effects
  - Overlay text and shapes
  - Zoom effects
  - Edge detection
- Batch processing capability
- User-friendly GUI interface
- Progress tracking
- Customizable effect parameters

### Video Comparison Tool
- Detailed analysis of video differences:
  - Speed comparison
  - Color analysis (HSV)
  - Zoom detection
  - Border comparison
  - Edge detection
  - Overlay detection
- Real-time preview
- Comprehensive similarity metrics
- Detailed analysis report

## Installation

```bash
# Clone the repository
git clone https://github.com/lendai-token/tiktok-video-generator.git

# Navigate to the project directory
cd tiktok-video-generator

# Install required packages
pip install -r requirements.txt
```

## Requirements

```txt
opencv-python>=4.5.0
numpy>=1.19.0
Pillow>=8.0.0
tkinter (included with Python)
```

## Usage

### Video Generator

```bash
python video_generator.py
```

1. Select input video file
2. Configure desired effects:
   - Speed modification
   - Color adjustments
   - Border effects
   - Overlay options
   - Zoom settings
   - Edge detection parameters
3. Set number of versions to generate
4. Click "Generate Videos" button

### Video Comparison Tool

```bash
python main.py
```

1. Click "Select Original Video" to choose the first video
2. Click "Select Modified Video" to choose the second video
3. Click "Compare Videos" to start analysis
4. View results in the text area

## Tools Description

### Video Generator
The Video Generator tool allows users to create multiple modified versions of a video with various effects. It features:
- Customizable effect parameters
- Real-time progress tracking
- Batch processing capabilities
- Output directory management
- Preview functionality

### Video Comparison Tool
The Video Comparison Tool provides detailed analysis of differences between two videos:
- Overall similarity percentage
- Individual effect analysis
- Visual preview of both videos
- Detailed metrics for each modification type
- Comprehensive report generation

## Technical Details

### Supported Video Formats
- MP4
- AVI
- MOV

### Analysis Metrics
- Speed difference
- Zoom variation
- Color modifications (HSV)
- Border effects
- Edge detection
- Overlay presence

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
- OpenCV community
- Python-tkinter documentation
- NumPy documentation
- PIL/Pillow documentation
