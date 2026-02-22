from service.utils.platform_info import CURRENT_OS, OS
from service.utils.file_utils import load_config
import json
import asyncio
import websockets
import cv2 as cv

SERVER_URI = "ws://localhost:5001"

async def run():
    print(f"Connecting to {SERVER_URI}...")
    test = cv.imread(r"C:\Users\ExploraVision\Src\ar_table_backend_service\text-test-4k.png")
    async with websockets.connect(SERVER_URI) as websocket:
        print("Connected. Waiting for messages...\n")
        try:
            async for message in websocket:
                print("Received:", message)

                print("Received:", message)

                # Parse JSON message
                data = json.loads(message)

                # Clone base image so we redraw fresh every frame
                frame = test.copy()

                if "markers" in data:
                    for marker in data["markers"]:
                        marker_data = marker.get("Data", {})
                        x = int(marker_data.get("X", 0))
                        y = int(marker_data.get("Y", 0))

                        # Draw red dot (BGR: 0,0,255)
                        cv.circle(frame, (x, y), radius=10, color=(0, 0, 255), thickness=-1)

                # Show updated image
                cv.imshow("Markers", cv.resize(frame, None, fx=0.3, fy=0.3))
                cv.waitKey(1)

        except websockets.ConnectionClosed:
            print("Connection closed")

    cv.destroyAllWindows()
if __name__ == "__main__":
    asyncio.run(run())
