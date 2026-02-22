from service.utils.file_utils import load_config
from service.vision.camera import init_video_capture
from service.utils.transform_utils import dist_to_map
from service.vision.aruco import ArucoMarkerDetector
import time
import cv2 as cv
import numpy as np
import os


def _detect_markers_with_attempts(
        detector: ArucoMarkerDetector,
        expected_count: int = None,
        flip_H = None) -> tuple:
    """
    @public
    Try capturing markers up to MAX_NR_OF_ATTEMPTS times.
    Return detected corners and ids; exit if markers cannot be detected reliably.
    """
    for attempt in range(1, MAX_NR_OF_ATTEMPTS + 1):
        frame = _get_most_recent_frame()
        if frame is None or np.mean(frame) < 5:
            print("Captured image is black, skipping frame.")
            continue
        
        if flip_H is not None:
            if CFG["flip"]["horizontal"] or CFG["flip"]["vertical"]:
                frame = cv.warpPerspective(
                    frame,
                    flip_H,
                    (CFG["camera"]["width"], CFG["camera"]["height"])
                )

        corners, ids = detector.detect(frame, DEBUG)
        if ids is not None:
            num_ids = len(ids)
            if expected_count:
                if num_ids > expected_count:
                    print(
                        f"Detected {num_ids} markers, expected {expected_count}. Assume setup or settings are wrong; exiting."
                    )
                    os._exit(0)
                elif num_ids == expected_count:
                    print(f"Detected {expected_count} markers on attempt {attempt}.")
                    return corners, ids
            else:
                return corners, ids

    print(
        f"Failed to detect expected markers in {MAX_NR_OF_ATTEMPTS} attempts. Assume setup or settings are wrong; exiting."
    )
    os._exit(0)

def _extract_common_corners(
    grid_corners: np.ndarray,
    grid_ids: np.ndarray,
    proj_grid_corners: np.ndarray,
    proj_grid_ids: np.ndarray,
) -> tuple:
    """
    From detected corners and ids in both images, extract only the corners corresponding 
    to markers detected in both images. Returns the common corners ordered by marker id.
    
    Returns:
        common_grid_corners: np.ndarray of shape (N*4, 2)
        common_proj_corners: np.ndarray of shape (N*4, 2)
        common_ids: list of int
    """
    if grid_ids is None or proj_grid_ids is None:
        print("No markers detected in one of the images. Exiting.")
        os._exit(0)

    # Flatten and ensure integer type
    grid_ids = np.asarray(grid_ids).flatten().astype(int)
    proj_ids = np.asarray(proj_grid_ids).flatten().astype(int)

    # Build lookup dictionaries
    grid_map = {id_: np.squeeze(c).astype(np.float32) for id_, c in zip(grid_ids, grid_corners)}
    proj_map = {id_: np.squeeze(c).astype(np.float32) for id_, c in zip(proj_ids, proj_grid_corners)}

    # Find intersection of detected IDs
    common_ids = sorted(set(grid_ids).intersection(proj_ids))

    if not common_ids:
        print("No common markers detected between projected and captured images. Exiting.")
        os._exit(0)

    # Collect corresponding corners in the same sorted order
    common_grid_corners = np.concatenate([grid_map[id_].reshape(-1, 2) for id_ in common_ids], axis=0)
    common_proj_corners = np.concatenate([proj_map[id_].reshape(-1, 2) for id_ in common_ids], axis=0)

    if DEBUG:
        print(f"{len(common_ids)} common markers detected: {common_ids}")
        
    return common_grid_corners, common_proj_corners, common_ids
    
def _setup_aruco_grid():
    """
    @public
    Generate an ArUco grid board image to be projected for calibration.
    """
    rows = 9
    aruco_grid_dim = (int(rows / CFG["projector"]["height"] * CFG["projector"]["width"]), rows)
    aruco_grid = cv.aruco.GridBoard(
        aruco_grid_dim, 0.02, 0.01,
        cv.aruco.getPredefinedDictionary(getattr(cv.aruco, CFG["aruco_detection"]["projected_marker_dict"]))
    ).generateImage((CFG["projector"]["width"], CFG["projector"]["height"]), 1, 1)
    return aruco_grid

def _calibrate_camera_to_projector():
    """
    @public
    Project an ArUco grid and detect it with the camera.
    Compute the camera-to-projector homography.
    """
    aruco_grid = _setup_aruco_grid()    
    gt_grid_corners, gt_grid_ids = DETECTOR_PROJ.detect(aruco_grid)

    
    # front, rear, rear_upsidedown, front_upsidedown
    # To respect mirrored projector setups for IT-Trans: flip grid -> detect markers -> unflip marker-coords 
    # Build flip homography
    flip_H = _build_flip_matrix(CFG["camera"]["width"], 
                                CFG["camera"]["height"], 
                                flip_h=CFG["flip"]["horizontal"], 
                                flip_v=CFG["flip"]["vertical"])
    
    cv.imshow(WNAME, aruco_grid)
    cv.waitKey(1)
    proj_grid_corners, proj_grid_ids = _detect_markers_with_attempts(DETECTOR_PROJ, flip_H=flip_H)
    # Suppose corners from aruco:
    # corners: list of arrays of shape (1, 4, 2)
    # flipped_corners = []
    proj_grid_corners = list(proj_grid_corners)
    for idx, marker in enumerate(proj_grid_corners):
        pts_flipped = cv.perspectiveTransform(marker, flip_H)
        proj_grid_corners[idx] = pts_flipped
    proj_grid_corners = tuple(proj_grid_corners)

    print("corners shape before", np.array(proj_grid_corners).shape)

    common_grid_corners, common_proj_corners, _ = _extract_common_corners(
        gt_grid_corners, gt_grid_ids, proj_grid_corners, proj_grid_ids
    )

    camera_to_projector_homography, _ = cv.findHomography(np.array(common_proj_corners), np.array(common_grid_corners))
    return camera_to_projector_homography

def _get_outermost_corners(markers: np.ndarray) -> np.ndarray:
    """
    @public
    Identify the outermost corner of each marker relative to the average center,
    then order those four corners clockwise starting from the top-left.

    Returns
    -------
    np.ndarray
        Shape (1, 4, 2); ordered as: [top-left, top-right, bottom-right, bottom-left]
    """
    markers = np.asarray(markers, dtype=np.float32)
    if markers.ndim == 3 and markers.shape[1:] == (4, 2):
        markers = markers.reshape(-1, 1, 4, 2)
    elif markers.ndim == 4 and markers.shape[1:] == (1, 4, 2):
        pass
    else:
        markers = markers.reshape(-1, 1, 4, 2)

    all_corners = markers[:, 0, :, :].reshape(-1, 2)
    center = np.mean(all_corners, axis=0)

    outermost = []
    for marker in markers:
        corners = marker[0]
        dists = np.linalg.norm(corners - center, axis=1)
        outermost_idx = int(np.argmax(dists))
        outermost.append(corners[outermost_idx])

    outermost = np.asarray(outermost, dtype=np.float32)
    centroid = np.mean(outermost, axis=0)
    angles = np.arctan2(outermost[:, 1] - centroid[1], outermost[:, 0] - centroid[0])
    order = np.argsort(angles)
    ordered = outermost[order]

    top_left_index = np.argmin(np.sum(ordered, axis=1))
    ordered = np.roll(ordered, -top_left_index, axis=0)

    return ordered.reshape(1, 4, 2).astype(np.float32)

def _calibrate_bounding_box(camera_to_projector_homography: np.ndarray) -> tuple:
    """
    @public
    Detect physical ArUco markers at table corners and compute bounding box homography.
    """
    cv.imshow(WNAME, WHITE_IMG)
    cv.waitKey(1)   
    time.sleep(1) # Ensure white image is being displayed

    table_corners, table_ids = _detect_markers_with_attempts(DETECTOR_PHYS, expected_count=4)

    outermost_corners = _get_outermost_corners(table_corners)
    dst_pts = cv.perspectiveTransform(outermost_corners, camera_to_projector_homography)

    src_pts = np.asarray([[[0, 0], 
                           [CFG["projector"]["width"], 0], 
                           [CFG["projector"]["width"],CFG["projector"]["height"]],
                           [0, CFG["projector"]["height"]]]], np.float32)
    bounding_box_homography, _ = cv.findHomography(src_pts, dst_pts)
    return bounding_box_homography


def _build_flip_matrix(width, height, flip_h, flip_v):
    M = np.eye(3, dtype=np.float32)

    if flip_h:
        Mh = np.array([
            [-1, 0, width - 1],
            [ 0, 1, 0],
            [ 0, 0, 1]
        ], dtype=np.float32)
        M = Mh @ M

    if flip_v:
        Mv = np.array([
            [1,  0, 0],
            [0, -1, height - 1],
            [0,  0, 1]
        ], dtype=np.float32)
        M = Mv @ M

    return M


def _get_most_recent_frame():
    # Cant rely on setting buffersize to 1, so we have to do this s***
    cap = init_video_capture(CFG["camera"]["index"],
                             CFG["camera"]["width"],
                             CFG["camera"]["height"],
                             CFG["camera"]["fps"])
    _, frame = cap.read()
    cap.release()
    frame = cv.remap(
                    frame.copy(),
                    MAP_A,
                    MAP_B,
                    interpolation=cv.INTER_LINEAR
                )
    return frame


if __name__ == "__main__":
    DEBUG = True
    CFG = load_config(r"service/config.json")

    # Load calibration
    ud = np.load(os.path.join('service/calibration', 'undistortion_args.npz'))
    camMtx = ud["camMtx"]
    distCoeffs = ud["distCoeff"]
    camMtxNew = ud["camMtxNew"]
    
    # TODO: add to camera class
    MAP_A, MAP_B = dist_to_map(camMtx,
                               distCoeffs,
                               camMtxNew,
                               CFG["camera"]["width"],
                               CFG["camera"]["height"])

    MAX_NR_OF_ATTEMPTS = 10
    WNAME = "MAIN"
    WINDOW = cv.namedWindow(WNAME, cv.WINDOW_NORMAL)
    cv.moveWindow(WNAME, 
                    x=CFG["projector"]["screen_position"][0],
                    y=CFG["projector"]["screen_position"][1])
    cv.setWindowProperty(WNAME, cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
    DETECTOR_PHYS = ArucoMarkerDetector(CFG["aruco_detection"]["physical_marker_dict"], 
                                        CFG["aruco_detection"]["detector_parameters"])
    DETECTOR_PROJ = ArucoMarkerDetector(CFG["aruco_detection"]["projected_marker_dict"],
                                        CFG["aruco_detection"]["detector_parameters"])
    
    WHITE_IMG = np.ones((CFG["projector"]["height"], CFG["projector"]["width"], 3), np.uint8) * 255
    # text_test_img = r"C:\Users\ExploraVision\Src\ar_table_backend_service\text_img_test.png"
    # TEST_IMG = cv.resize(cv.imread(text_test_img), (CFG["projector"]["width"], CFG["projector"]["height"]))

    cam_to_proj_H = _calibrate_camera_to_projector()
    bounding_box_H = _calibrate_bounding_box(cam_to_proj_H)

    print("Calibration was successful.")

    # Save calibration
    CALIBRATION_DIR = 'service/calibration'
    os.makedirs(CALIBRATION_DIR, exist_ok=True)
    np.save(os.path.join(CALIBRATION_DIR, 'cam_to_proj_H.npy'), cam_to_proj_H)
    np.save(os.path.join(CALIBRATION_DIR, 'bounding_box_H.npy'), bounding_box_H)
    print(f"Calibration was saved to {CALIBRATION_DIR}.")


    if DEBUG:
        print("Displaying calibration bounding box in white.")
        debug_img = cv.warpPerspective(WHITE_IMG, bounding_box_H, (CFG["projector"]["width"], CFG["projector"]["height"]))
        # debug_img = cv.warpPerspective(TEST_IMG, bounding_box_H, (CFG["projector"]["width"], CFG["projector"]["height"]))
        cv.imshow(WNAME, debug_img)
        cv.waitKey(0)

