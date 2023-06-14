# Video stream ROI Tracking with basic Cinematic Composition Rules

This project is a basic Python-based implementation of real-time tracking using OpenCV, dlib, and numpy. It leverages the cinematic composition rules to determine the region of interest in the video stream. This program is suitable for tracking a persone within a video or through a webcam in real-time.

## Requirements

The script requires the following Python packages:

- OpenCV (4.7.0.72)
- Numpy (1.24.2)
- dlib (19.24.1)

To install these packages, run:

```bash
pip install -r requirements.txt
```

## Usage

To run the script, use the following command:

```bash
python main.py
```

## Functionality

Once started, the script will open a window displaying the webcam or any video capture device feed. 

To start tracking an object (or face), left-click and drag the mouse to draw a rectangle around the object. When you release the mouse button, the tracker will initialize and start to track the object. 

While tracking, the script also applies cinematic composition rules (like the rule of thirds) to guide the camera framing, if possible. It will draw a red rectangle around the tracked object and a blue rectangle to represent the ideal framing and open a second window that show the framing.

You can stop tracking by clicking on the feed.

To close the script, press the 'q' button.

## License

This project is licensed under the MIT License. See `LICENSE` for more details.
