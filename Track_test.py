import cv2
import numpy as np
import dlib
import sys

class RoiSelection:
    def __init__(self):
        self.start_point = None
        self.current_point = None
        self.selected = False

roi_selection_data = RoiSelection()
vertical_bias = 0.4

def roi_selection(event, x, y, flags, param):
    global roi_selection_data, tracking_started

    if event == cv2.EVENT_LBUTTONDOWN:
        if tracking_started:
            tracking_started = False
            roi_selection_data.selected = False
            roi_selection_data.start_point = None
            roi_selection_data.current_point = None
        else:
            roi_selection_data.start_point = (x, y)
            roi_selection_data.current_point = (x, y)
            roi_selection_data.selected = False

    elif event == cv2.EVENT_MOUSEMOVE:
        if roi_selection_data.start_point is not None:
            roi_selection_data.current_point = (x, y)

    elif event == cv2.EVENT_LBUTTONUP:
        if roi_selection_data.start_point is not None:
            roi_selection_data.selected = True

def find_largest_contour(frame):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray_frame, 127, 255, 0)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    max_area = -1
    max_contour = None
    for c in contours:
        area = cv2.contourArea(c)
        if area > max_area:
            max_area = area
            max_contour = c

    return max_contour

def get_bounding_rect(roi):
    return (roi.left(), roi.top(), roi.right()-roi.left()+1, roi.bottom()-roi.top()+1)

def smooth_camera_movement(current_roi, prev_roi, alpha=0.15):
    if prev_roi is None:
        return current_roi

    x1, y1, w1, h1 = current_roi
    x2, y2, w2, h2 = prev_roi

    nx = int(x1 * alpha + x2 * (1 - alpha))
    ny = int(y1 * alpha + y2 * (1 - alpha))

    return (nx, ny, w1, h1)

def draw_cropped_frame(frame, roi):
    x, y, w, h = [int(value) for value in roi]
    cropped_frame = frame[y:y+h, x:x+w]
    cv2.imshow('CADRE', cropped_frame)

def on_vertical_bias_trackbar(val):
    global vertical_bias
    vertical_bias = val / 100

def create_trackbar():
    cv2.createTrackbar("HeadRoom", "Frame", 50, 100, on_vertical_bias_trackbar)

def apply_cinematic_rules(frame, roi, ref_width_ratio=0.7, headroom_ratio=0, thirds_rule_ratio=0.666):
    global vertical_bias
    frame_height, frame_width = frame.shape[:2]
    x, y, w, h = roi

    ref_width = int(frame_width * ref_width_ratio)
    ref_height = int(ref_width * (9 / 16))

    x_target = x + w // 2 - ref_width // 2
    y_target = y + h // 2 - ref_height // 2

    x_target = max(0, min(x_target, frame_width - ref_width))
    y_target = max(0, min(y_target, frame_height - ref_height))

    # Apply the rule of thirds and vertical bias
    y_target = int(y_target - h * (1 - thirds_rule_ratio) + h * vertical_bias)

    # Adjust headroom based on ROI height and headroom_ratio
    headroom = int(h * headroom_ratio)
    y_target -= headroom

    y_target = max(0, min(y_target, frame_height - ref_height))

    return x_target, y_target, ref_width, ref_height

def main():
    global roi_selection_data, tracking_started, prev_roi, prev_frame, vertical_bias

    #WebCam
    #cap = cv2.VideoCapture(0)
    #ret, frame = cap.read()

    #Video File
    video_path = '/Users/zap/Desktop/CAM3.mp4'
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    #

    if not ret:
        print("No suitable camera device found.")
        sys.exit(1)

    tracking_started = False
    prev_roi = None
    prev_frame = None

    tracker = dlib.correlation_tracker()
    cv2.namedWindow('Frame')
    cv2.setMouseCallback('Frame', roi_selection)
    create_trackbar()

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        frame_height, frame_width = frame.shape[:2]

        if tracking_started:
            success = tracker.update(frame)
            if success:
                roi = get_bounding_rect(tracker.get_position())
                x, y, w, h = roi
                if w > 0 and h > 0:
                    cv2.rectangle(frame, (int(x), int(y)), (int(x + w), int(y + h)), (0, 0, 255), 2)

                    smoothed_roi = smooth_camera_movement(roi, prev_roi)
                    blue_rectangle_roi = apply_cinematic_rules(frame, smoothed_roi)
                    x, y, w, h = blue_rectangle_roi
                    cv2.rectangle(frame, (int(x), int(y)), (int(x + w), int(y + h)), (255, 0, 0), 2)

                    draw_cropped_frame(frame, blue_rectangle_roi)
                    prev_roi = smoothed_roi
            else:
                largest_contour = find_largest_contour(frame)
                if largest_contour is not None:
                    bbox = get_bounding_rect(dlib.rectangle(*cv2.boundingRect(largest_contour)))
                    x, y, w, h = bbox
                    tracker.start_track(frame, dlib.rectangle(x, y, x + w, y + h))
                    tracking_started = True
        else:
            if roi_selection_data.start_point and roi_selection_data.current_point:
                cv2.rectangle(frame, roi_selection_data.start_point, roi_selection_data.current_point, (0, 255, 0), 2)

            if roi_selection_data.selected:
                x1, y1 = roi_selection_data.start_point
                x2, y2 = roi_selection_data.current_point
                init_roi = (x1, y1, abs(x1 - x2), abs(y1 - y2))
                if init_roi[2] > 10 and init_roi[3] > 10:
                    tracker.start_track(frame, dlib.rectangle(x1, y1, x2, y2))
                    tracking_started = True
                else:
                    tracking_started = False
                roi_selection_data.start_point = None
                roi_selection_data.current_point = None
                roi_selection_data.selected = False

        cv2.imshow('Frame', frame)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
