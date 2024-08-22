# server.py
import base64
import socketio
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# Create a FastAPI app
app = FastAPI()

# Allow CORS (optional, but useful for frontend development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a Socket.IO server
sio = socketio.AsyncServer(async_mode="asgi")
# Attach Socket.IO server to the FastAPI app
app.mount("/socket.io", socketio.ASGIApp(sio, socketio_path="socket.io"))


@app.get("/")
async def get():
    # Replace with your own HTML template path if needed
    with open("templates/index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)


@sio.event
async def connect(sid, environ):
    print(f"Client {sid} connected")


@sio.event
async def disconnect(sid):
    print(f"Client {sid} disconnected")


@sio.on('send_image')
async def handle_image(sid, data):
    try:
        # Emit the image to be displayed on the webpage
        await sio.emit('display_image', {'image': data['image']})
    except Exception as e:
        print(f"Error handling image: {e}")


@sio.on('refresh')
async def handle_refresh(sid):
    print("refresh clicked")
    try:
        await sio.emit("refresh")
    except Exception as e:
        print(f"Error refreshing captcha : {e}")


@sio.on('send_text')
async def handle_text(sid, data):
    try:
        print(f"Received text from client {sid}: {data['text']}")
        # Send the entered text back to all clients
        await sio.emit('receive_text', {'text': data['text']})
    except Exception as e:
        print(f"Error handling text: {e}")


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)
