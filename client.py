# client.py
import base64
import socketio

sio = socketio.Client()


@sio.event
def connect():
    print('Connected to server')


@sio.event
def disconnect():
    print('Disconnected from server')


@sio.on('receive_text')
def on_receive_text(data):
    print(f"Received text from server: {data['text']}")


def send_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        sio.emit('send_image', {'image': encoded_image})


if __name__ == '__main__':
    sio.connect('http://localhost:8000/ws')  # Ensure the correct endpoint is used
    # Send an image
    send_image("captcha_08609_y9Aqf.png")
    # Wait for the response
    sio.wait()
