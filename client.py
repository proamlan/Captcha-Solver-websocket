import asyncio
import websockets
import requests
import os


async def websocket_client():
    uri = "ws://localhost:8000/ws/client1"

    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            print(f"Received: {message}")

            # Simulate user input after receiving a message
            user_input = input("Enter text to send: ")
            await websocket.send(user_input)


def upload_image(image_path):
    url = "http://localhost:8000/upload"
    with open(image_path, 'rb') as image_file:
        files = {'image': image_file}
        response = requests.post(url, files=files)
    print(response.json())


if __name__ == "__main__":
    image_path = "captcha_08609_y9Aqf.png"

    # Step 1: Upload Image
    if os.path.exists(image_path):
        upload_image(image_path)
    else:
        print("Image file not found!")

    # Step 2: Connect to WebSocket and communicate
    asyncio.run(websocket_client())
