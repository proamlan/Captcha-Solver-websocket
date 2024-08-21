import uvicorn
from fastapi import FastAPI, WebSocket, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.websockets import WebSocketDisconnect
from pathlib import Path

app = FastAPI()

# Mount static directory for serving images
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates directory
templates = Jinja2Templates(directory="templates")

# Dictionary to store WebSocket clients
clients = {}


@app.post("/upload")
async def upload_image(image: UploadFile = File(...)):
    # Save the uploaded image
    image_path = Path('static/received_image.png')
    with image_path.open('wb') as f:
        f.write(await image.read())

    # Notify all connected WebSocket clients that the image has been received
    for client_id, client in clients.items():
        await client.send_text("Image received")

    return {"message": "Image received and saved."}


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    clients[client_id] = websocket

    try:
        while True:
            # Wait for text input from the webpage
            text = await websocket.receive_text()
            print("received text: " + text)
            for client_id, client in clients.items():
                await client.send_text("Image received")

            # Echo the received text back to the client
            await websocket.send_text(f"Received text: {text}")
    except WebSocketDisconnect:
        del clients[client_id]


@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="debug")
