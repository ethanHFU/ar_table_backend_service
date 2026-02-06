from service.utils.platform_info import CURRENT_OS, OS
import asyncio
import websockets

SERVER_URI = "ws://localhost:5001"

async def run():
    print(f"Connecting to {SERVER_URI}...")
    async with websockets.connect(SERVER_URI) as websocket:
        print("Connected. Waiting for messages...\n")

        try:
            async for message in websocket:
                print("Received:", message)
        except websockets.ConnectionClosed:
            print("Connection closed")

if __name__ == "__main__":
    asyncio.run(run())
