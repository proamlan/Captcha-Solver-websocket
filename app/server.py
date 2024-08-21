import uvicorn
from fastapi import FastAPI, WebSocket, UploadFile, File
from fastapi.responses import HTMLResponse
from typing import List

app = FastAPI()
clients = []


@app.post("/upload")
async def upload_image(image: UploadFile = File(...)):
    # Save the uploaded image for user input
    with open('received_image.png', 'wb') as f:
        f.write(await image.read())
    return {"message": "Image received. Waiting for user input."}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)

    # Wait for user to input the text manually
    # This part assumes the server-side user will somehow input the text
    text = await get_user_input()  # Replace with your logic for user input

    await websocket.send_text(text)
    await websocket.close()


async def get_user_input():
    # Simulate user input
    return input("Enter the text for the received image: ")


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
