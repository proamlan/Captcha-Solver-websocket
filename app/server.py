import uvicorn
from fastapi import FastAPI, WebSocket, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.websockets import WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

clients = {}


@app.post("/upload")
async def upload_image(image: UploadFile = File(...)):
    print("received file")
    # Save the uploaded image
    image_path = Path('static/received_image.png')
    with image_path.open('wb') as f:
        f.write(await image.read())

    # Notify clients
    for client in clients.values():
        await client.send_text("Image received. Please refresh the page.")

    return {"message": "Image received. Waiting for user input."}


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    clients[client_id] = websocket

    try:
        while True:
            # Wait for text input from the client
            text = await websocket.receive_text()
            await websocket.send_text(f"Received text: {text}")
    except WebSocketDisconnect:
        del clients[client_id]


@app.get("/", response_class=HTMLResponse)
async def get(request):
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == '__main__':
    uvicorn.run("server:app", host="0.0.0.0", port=8000, log_level="debug")
