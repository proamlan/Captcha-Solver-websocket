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
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            sio.emit('send_image', {'image': encoded_image})
    except Exception as e:
        print(f"Error sending image: {e}")


if __name__ == '__main__':
    sio.connect('http://localhost:8000')
    # Send an image
    send_image("captcha_08609_y9Aqf.png")

    # Keep the client running to receive text
    try:
        sio.wait()
    except KeyboardInterrupt:
        print("Client stopped by user")
    finally:
        sio.disconnect()
