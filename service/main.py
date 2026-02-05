import json
import asyncio
import queue
from service.server import WebSocketServer

from service.vision.camera import init_video_capture
from service.vision.detection import ArucoMarkerDetector, Marker

import cv2 as cv
import numpy as np


def marker_payload(marker_id, x, y):
    return {
            "Id": int(marker_id),
            "MessageType": "CONTROLHOVER",
            "Data": {
                "X": float(x),
                "Y": float(y),
            },
        }

def markers_payload(markers):
    return {
        "markers": [marker_payload(m.id, m.center.X, m.center.Y) for m in markers]
    }

def run_calibration():
    pass

def run_service(detector, cap, ws, H):
    try:
        WINDOW_NAME = "MAIN"
        cv.namedWindow(WINDOW_NAME, cv.WINDOW_NORMAL)
        cv.resizeWindow(WINDOW_NAME, (WIDTH, HEIGHT))

        while True:
            ret, frame = cap.read()
            if not ret:
                print("No frame read")
                break

            # TODO: Undistortion with remap
            markers = detector.detect(frame)
            if markers:

                for marker in markers:
                    cv.perspectiveTransform(marker.corners_cv, H)
                
                ws.broadcast(markers_payload(markers))
                corners, ids = Marker.to_cv_collection(markers)
                frame = cv.aruco.drawDetectedMarkers(frame, corners, ids)

            cv.imshow(WINDOW_NAME, frame)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        print("Shutting down...")
        if cap is not None:
            cap.release()
        cv.destroyAllWindows()


if __name__ == "__main__":
    
    
    # Init detector
    DETECTOR_PARAMETERS = {
            "perspectiveRemoveIgnoredMarginPerCell": 0.1,
            "perspectiveRemovePixelPerCell": 4,
            "errorCorrectionRate": 0.5
    }
    detector = ArucoMarkerDetector("DICT_4X4_250", DETECTOR_PARAMETERS)

    # Init camera
    CAM_IDX, WIDTH, HEIGHT, FPS = 0, 1920, 1080, 30
    cap = init_video_capture(CAM_IDX, WIDTH, HEIGHT, FPS)

    # undistort_map = cv.initUndistortRectifyMap()

    H = np.identity(3)
    
    # Init websocket
    ws = WebSocketServer(port=5001)
    ws.start()
    
    run_service(detector, cap, ws, H)
    


