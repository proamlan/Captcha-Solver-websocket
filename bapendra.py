import json
import asyncio

import socketio
import websockets
import base64
from playwright.async_api import async_playwright


async def extract_data(page):
    # Find the first table (Identitas Kendaraan)
    identitas_rows = await page.query_selector_all('#hasil table:nth-of-type(1) tr')
    identitas_data = {
        await (await row.query_selector('td:first-child')).inner_text(): await (await row.query_selector(
            'td:last-child')).inner_text()
        for row in identitas_rows
    }

    # Find the second table (Biaya Penul Tahunan)
    biaya_tahunan_rows = await page.query_selector_all('#hasil table:nth-of-type(2) tr')
    biaya_tahunan_data = {
        await (await row.query_selector('td:first-child')).inner_text(): await (await row.query_selector(
            'td:last-child')).inner_text()
        for row in biaya_tahunan_rows
    }

    # Find the third table (Tambahan Biaya Penul 5 Tahunan)
    biaya_lima_tahunan_rows = await page.query_selector_all('#hasil table:nth-of-type(3) tr')
    biaya_lima_tahunan_data = {
        await (await row.query_selector('td:first-child')).inner_text(): await (await row.query_selector(
            'td:last-child')).inner_text()
        for row in biaya_lima_tahunan_rows
    }

    # Combine all data into a single dictionary
    result = {
        "Identitas Kendaraan": identitas_data,
        "Biaya Penul Tahunan": biaya_tahunan_data,
        "Tambahan Biaya Penul 5 Tahunan": biaya_lima_tahunan_data
    }

    return result


async def send_image_to_socketio(image_data):
    sio = socketio.AsyncClient(logger=True, engineio_logger=True)
    uri = "http://0.0.0.0:8000"  # Adjust this to your Socket.IO server address

    ocr_result = None
    ocr_event = asyncio.Event()

    @sio.event
    def connect():
        print("Connected to Socket.IO server")

    @sio.event
    def disconnect():
        print("Disconnected from Socket.IO server")

    @sio.on('ocr_result')
    def on_ocr_result(data):
        nonlocal ocr_result
        print(f"Received OCR result: {data}")
        ocr_result = data
        ocr_event.set()

    @sio.event
    def connect_error(data):
        print(f"Connection error: {data}")

    try:
        await sio.connect(uri)
        print("Connected to server, sending image...")

        # Encode the image data to base64
        encoded_image = base64.b64encode(image_data).decode('utf-8')

        # Send the image data
        await sio.emit('send_image', {
            "image": encoded_image,
            "text": "Perform OCR on this image"
        })
        print("Image sent, waiting for OCR result...")

        # Wait for the OCR result with a timeout
        try:
            await asyncio.wait_for(ocr_event.wait(), timeout=30)  # 30 seconds timeout
        except asyncio.TimeoutError:
            print("Timeout waiting for OCR result")

        print("Disconnecting from server...")
        await sio.disconnect()

        if ocr_result:
            return ocr_result.get('text', '')
        else:
            print("No OCR result received")
            return ''
    except Exception as e:
        print(f"Socket.IO connection error: {e}")
        return ""


async def run():
    async with async_playwright() as playwright:
        # Launch a new browser instance
        browser = await playwright.chromium.launch(headless=False)  # Set to True for headless mode
        context = await browser.new_context()

        # Open a new page
        page = await context.new_page()

        # Navigate to the webpage
        await page.goto("https://bapenda.jatimprov.go.id/info/pkb")

        # Wait for the page to load completely
        await page.wait_for_load_state("load")

        # Find the input element with name "nopol" and enter the vehicle registration number
        await page.fill('input[name="nopol"]', 'L 1554 RL')

        # Wait for 1 second
        await asyncio.sleep(1)

        # Get the canvas element and take a screenshot
        canvas_element = page.locator('#canvas')
        canvas_image = await canvas_element.screenshot()

        # Send the image to the Socket.IO server for OCR
        ocr_text = await send_image_to_socketio(canvas_image)

        if ocr_text:
            # Fill the OCR result into the CAPTCHA input field
            await page.fill('input[name="captcha_field"]', ocr_text)  # Adjust the selector to your captcha field

            # Submit the form
            await page.click('button[type="submit"]')

            # Log the result
            print("Form submitted with OCR text:", ocr_text)

            # Wait for the page to load after submission
            await page.wait_for_load_state("load")

            # Extract the data
            data = await extract_data(page)

            # Convert the data to JSON and print it
            json_data = json.dumps(data, indent=4)
            print(json_data)
        else:
            print("Failed to retrieve OCR text")

        # Close the browser
        await browser.close()


if __name__ == '__main__':
    asyncio.run(run())
