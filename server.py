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
    return HTMLResponse(content="<h1>Hello, FastAPI with Socket.IO!</h1>", status_code=200)


@sio.event
async def connect(sid, environ):
    print(f"Client {sid} connected")


@sio.event
async def disconnect(sid):
    print(f"Client {sid} disconnected")


@sio.on('send_image')
async def handle_image(sid, data):
    # Decode the image from base64
    image_data = base64.b64decode(data['image'])
    # Save the image to display it
    with open("received_image.png", "wb") as f:
        f.write(image_data)

    # Emit an event to the client-side for user input
    await sio.emit('display_image', {'image': data['image']}, room=sid)


@sio.on('send_text')
async def handle_text(sid, data):
    # Send the user input back to the client
    await sio.emit('receive_text', {'text': data['text']}, room=sid)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)