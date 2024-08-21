import asyncio
import websockets
import requests


async def send_image(image_path):
    # Step 1: Send image to the server
    with open(image_path, 'rb') as image_file:
        response = requests.post('http://0.0.0.0:8000/upload', files={'image': image_file})

    # Step 2: Wait for the text response
    async with websockets.connect('ws://0.0.0.0:8000/ws') as websocket:
        text_response = await websocket.recv()
        print("Received text:", text_response)

    # Step 3: Continue with line no. 6
    # (Your logic here)
    print("Got the response: " + text_response)


if __name__ == '__main__':
    asyncio.run(send_image('captcha_08609_y9Aqf.png'))
