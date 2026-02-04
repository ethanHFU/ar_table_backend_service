import socket
import json

from service.vision.camera import init_video_capture
from service.vision.detection import ArucoMarkerDetector, Marker

import cv2 as cv
import numpy as np


def send_payload(conn, marker_id, x, y):
    payload = {
        "Id": marker_id,
        "MessageType": "CONTROLHOVER",
        "Data": {
            "X": float(x),
            "Y": float(y)
        },
    }
    conn.sendall(json.dumps(payload).encode("utf-8") + b"\n")    


if __name__ == "__main__":
    HOST = "0.0.0.0"
    PORT = 9999

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(1)

    print("Waiting for client...")
    conn, addr = server.accept()
    print("Connected:", addr)

    cap = None

    try:
        DETECTOR_PARAMETERS = {
            "perspectiveRemoveIgnoredMarginPerCell": 0.1,
            "perspectiveRemovePixelPerCell": 4,
            "errorCorrectionRate": 0.5
        }

        detector = ArucoMarkerDetector("DICT_4X4_250", DETECTOR_PARAMETERS)

        CAM_IDX, WIDTH, HEIGHT, FPS = 0, 1920, 1080, 30
        cap = init_video_capture(CAM_IDX, WIDTH, HEIGHT, FPS)

        WINDOW_NAME = "MAIN"
        cv.namedWindow(WINDOW_NAME, cv.WINDOW_NORMAL)
        cv.resizeWindow(WINDOW_NAME, (WIDTH, HEIGHT))

        while True:
            ret, frame = cap.read()
            if not ret:
                print("No frame read")
                break

            markers = detector.detect(frame)
            if markers:
                m = markers[0]
                send_payload(conn, m.id, m.center.X, m.center.Y)

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

        try:
            conn.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        conn.close()

        server.close()