# OMR Grading System using Computer Vision

A robust, production-ready Optical Mark Recognition (OMR) grading system designed for mobile captures. This system uses OpenCV to align, process, and grade OMR sheets with high accuracy, handling perspective distortion and lighting variations.

## Features

*   **Robust Alignment**: Uses ORB feature detection and Homography to align mobile-captured images with a reference template.
*   **Adaptive Processing**: Gaussian Adaptive Thresholding handles uneven lighting conditions.
*   **Configurable**: All parameters (bubble coordinates, exam keys, processing thresholds) are defined in `config/config.yaml`.
*   **Modular Architecture**: Clean separation of concerns (Aligner, Grader, Visualizer).
*   **Docker Ready**: Includes a Dockerfile for easy deployment.

## Project Structure

```
.
├── config/             # Configuration files
│   └── config.yaml     # Main config (paths, exam key, ROI coords)
├── data/               # Data directory
│   ├── inputs/         # Input images to be graded
│   ├── template/       # Reference template image
│   └── outputs/        # Graded results and debug images
├── scripts/            # Utility scripts
│   └── generate_mock_data.py # Generates sample template and input
├── src/                # Source code
│   ├── aligner.py      # ORB + Homography logic
│   ├── grader.py       # Thresholding + Bubble analysis
│   ├── visualizer.py   # Result drawing
│   └── utils.py        # Helpers
├── main.py             # Entry point
├── Dockerfile          # Container definition
└── requirements.txt    # Python dependencies
```

## Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd OMR_Grading_using_CompVision
    ```

2.  **Install Dependencies:**
    It is recommended to use a virtual environment.
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### 1. Generate Mock Data (Optional)
If you don't have your own OMR sheets yet, generate a sample template and a "filled" input image (with simulated perspective distortion).
```bash
python scripts/generate_mock_data.py
```
This will create:
- `data/template/template.jpg`
- `data/inputs/sample_sheet.jpg`

### 2. Run the Grader
Run the main pipeline. It will use the paths defined in `config/config.yaml` by default.
```bash
python main.py
```

To specify a different input image:
```bash
python main.py --input path/to/your/image.jpg
```

### 3. View Results
Check the `data/outputs/` directory for:
- `result.jpg`: The graded sheet with correct/incorrect overlays and score.
- `debug_aligned.jpg`: The input image after perspective correction.
- `debug_threshold.jpg`: The binary image used for bubble detection.

## Configuration

Edit `config/config.yaml` to customize:
- **`exam`**: Number of questions, options, and the correct answer key.
- **`roi`**: Coordinates for the first bubble, gaps between bubbles, and radius.
- **`processing`**: ORB parameters and Thresholding block sizes.

## Docker

To run the system in a container:

```bash
docker build -t omr-grader .
docker run -v $(pwd)/data:/app/data omr-grader
```