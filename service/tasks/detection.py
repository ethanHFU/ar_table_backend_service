import os
from service.utils.file_utils import load_config
from service.vision.camera import init_video_capture
from service.vision.aruco import ArucoMarkerDetector, Marker
from service.ws.server import WebSocketServer

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


def run_service(detector, cap, ws, H):
    try:
        WINDOW_NAME = "MAIN"
        cv.namedWindow(WINDOW_NAME, cv.WINDOW_AUTOSIZE)

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
    CFG = load_config(r"service/config.json")
    
    detector = ArucoMarkerDetector(CFG["aruco_detection"]["physical_marker_dict"],
                                   CFG["aruco_detection"]["detector_parameters"])

    # Init camera
    cap = init_video_capture(CFG["camera"]["index"],
                             CFG["camera"]["width"],
                             CFG["camera"]["height"],
                             CFG["camera"]["fps"])

    # undistort_map = cv.initUndistortRectifyMap()

    H = np.identity(3)
    # H = np.load(os.path.join('cam_to_proj_H.npz'))

    # Init websocket
    ws = WebSocketServer(port=5001)
    ws.start()
    
    run_service(detector, cap, ws, H)
    


