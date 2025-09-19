from flask import Flask, render_template, request, jsonify
import requests
import logging
import os
import base64
from datetime import datetime

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# --- Configuration ---
# Fixed Ollama API URL (previously from UI)
# For better practice, this could be an environment variable
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL = "gemma3:4b" # Ensure this model is pulled in Ollama

# --- Paths for saving data ---
SAVE_DIR = os.path.dirname(os.path.abspath(__file__)) # Gets the directory of app.py
CAPTIONS_HISTORY_DIR = os.path.join(SAVE_DIR, "saved_captions")
IMAGES_DIR = os.path.join(SAVE_DIR, "saved_images")
CAPTIONS_FILE_PATH = os.path.join(CAPTIONS_HISTORY_DIR, "caption_history.txt")

# --- Helper function to ensure directories exist ---
def ensure_dir(directory_path):
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path)
            logging.info(f"Created directory: {directory_path}")
        except OSError as e:
            logging.error(f"Error creating directory {directory_path}: {e}")
            # Depending on how critical this is, you might want to raise the exception
            # or handle it by not attempting to save files. For now, we'll log and continue.


# Ensure directories are created when the app starts
ensure_dir(CAPTIONS_HISTORY_DIR)
ensure_dir(IMAGES_DIR)


@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/api/caption', methods=['POST'])
def get_caption():
    """
    Receives image data and a prompt, sends it to Ollama,
    saves the image and caption history, and returns the caption.
    """
    if not request.is_json:
        logging.error("Request not JSON")
        return jsonify({'error': 'Invalid request: Content-Type must be application/json'}), 415

    data = request.get_json()
    base64_image_data = data.get('image_data') # This is just the base64 string, no prefix
    custom_prompt = data.get('prompt', 'Describe what you see.').strip()

    if not base64_image_data:
        logging.error("No image_data in request")
        return jsonify({'error': 'No image data provided'}), 400
    if not custom_prompt:
        logging.error("Prompt is missing")
        return jsonify({'error': 'Prompt is required'}), 400

    # --- Save the captured image ---
    try:
        # Create a unique filename for the image using a timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3] # YYYYMMDD_HHMMSS_ms
        image_filename = f"frame_{timestamp}.jpg"
        image_save_path = os.path.join(IMAGES_DIR, image_filename)

        # Decode the base64 string to bytes and save the image
        image_bytes = base64.b64decode(base64_image_data)
        with open(image_save_path, 'wb') as img_file:
            img_file.write(image_bytes)
        logging.info(f"Saved image to {image_save_path}")
    except base64.binascii.Error as b64_error:
        logging.error(f"Error decoding base64 image data: {b64_error}")
        # Optionally, you could decide not to proceed if saving image fails
    except Exception as e:
        logging.error(f"Error saving image: {e}")
        # Optionally, decide if this error should stop processing

    # --- Prepare payload for Ollama ---
    payload = {
        "model": MODEL,
        "prompt": custom_prompt,
        "images": [base64_image_data], # Ollama API expects just the base64 string in the list
        "stream": False
    }

    logging.info(f"Sending request to Ollama at {OLLAMA_API_URL} for model {MODEL}...")
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=90) # Increased timeout
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)

        ollama_response_data = response.json()
        logging.info("Received response from Ollama.")
        caption = ollama_response_data.get('response', '').strip()

        if not caption:
            logging.warning("Ollama returned an empty caption.")
            caption = "No description could be generated for this frame."
        elif "Sorry, I can't" in caption or "I am unable to" in caption:
            logging.info(f"Ollama could not process the image with prompt '{custom_prompt}': {caption}")
            caption = "Model could not process the image as requested."

        # --- Save the question and answer to history file ---
        try:
            with open(CAPTIONS_FILE_PATH, 'a', encoding='utf-8') as history_file:
                history_file.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                history_file.write(f"Q: {custom_prompt}\n")
                history_file.write(f"A: {caption}\n")
                if 'image_filename' in locals(): # Check if image_filename was set
                    history_file.write(f"Image: {image_filename}\n")
                history_file.write("-" * 30 + "\n\n")
            logging.info(f"Saved Q/A to {CAPTIONS_FILE_PATH}")
        except Exception as e:
            logging.error(f"Error saving caption history: {e}")

        return jsonify({'caption': caption})

    except requests.exceptions.Timeout:
        logging.error(f"Request to Ollama ({OLLAMA_API_URL}) timed out.")
        return jsonify({'error': 'The request to the Ollama server timed out.'}), 504
    except requests.exceptions.ConnectionError:
        logging.error(f"Could not connect to Ollama server at {OLLAMA_API_URL}. Is Ollama running?")
        return jsonify({'error': f'Could not connect to Ollama server at {OLLAMA_API_URL}.'}), 503
    except requests.exceptions.HTTPError as e:
        error_detail = "Unknown Ollama API error"
        try:
            error_detail = e.response.json().get("error", e.response.text)
        except ValueError: # If response is not JSON
            error_detail = e.response.text if e.response.text else str(e)
        logging.error(f"Ollama API ({OLLAMA_API_URL}) error: {e.response.status_code} - {error_detail}")
        return jsonify({'error': f'Ollama API error: {error_detail}'}), e.response.status_code
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({'error': f'An unexpected server error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) # Set debug=False for production