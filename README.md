# Real-Time Webcam Captioning with Gemma3:4b and Ollama

This project provides a web-based interface for real-time captioning of your webcam feed using the Gemma3:4b multimodal model, served locally via Ollama. It captures frames from your webcam, allows you to input custom instructions (prompts), and displays the generated descriptions. Additionally, it saves a history of all prompts and captions, along with the corresponding captured images.

---

## Features

* **Live Webcam Feed:** Displays your webcam stream directly in the browser.
* **Real-Time Captioning:** Sends webcam frames to a local gemma3:4b model (via Ollama) for description.
* **Custom Prompts:** Allows users to specify custom instructions or questions for the model regarding the webcam image.
* **Adjustable Refresh Rate:** Control how frequently frames are captured and sent for captioning.
* **Caption History:** Automatically saves all prompts and their corresponding generated captions to a text file (`saved_captions/caption_history.txt`).
* **Image Saving:** Automatically saves the captured webcam frames that are sent for captioning into the `saved_images/` folder.
* **Simple Web Interface:** Easy-to-use interface built with Flask, HTML, CSS, and JavaScript.

## Project Structure

```text
./
├── .venv/                  # Virtual environment
├── saved_captions/
│   └── caption_history.txt # Stores Q&A history
├── saved_images/           # Stores captured image frames
├── static/
│   ├── css/
│   │   └── style.css       # Styles for the web interface
│   └── js/
│       └── script.js       # Front-end JavaScript logic
├── templates/
│   └── index.html          # Main HTML page for the interface
├── app.py                  # Flask back-end application
└── README.md               # Project documentation
```


*(Note: The `.venv` folder is a standard Python virtual environment. It's good practice to include it in your `.gitignore` file if you're using Git.)*

## Prerequisites

Before you begin, ensure you have the following installed:

1.  **Python 3.7+**
2.  **Ollama Desktop:** Download and install from [ollama.com](https://ollama.com).
3.  **gemma3:4b Model (or another gemma variant):**
    * After installing Ollama, pull the model by running the following command in your terminal:
        ```bash
        ollama pull gemma3:4b
        ```
    * Verify the model is available:
        ```bash
        ollama list
        ```
4.  **A Webcam:** Connected to your computer and accessible by your browser/OS.

## Setup and Installation

1.  **Clone the Repository (or create your project directory):**
    ```bash
    # If you've cloned from GitHub:
    # git clone
    # cd webcam-captioning
    ```

2.  **Create and Activate a Virtual Environment (Recommended):**
    ```bash
    python -m venv .venv
    # On Windows
    .\.venv\Scripts\activate
    # On macOS/Linux
    source .venv/bin/activate
    ```

3.  **Install Python Dependencies:**
    Make sure you have a `requirements.txt` file or install them manually:
    ```bash
    pip install Flask requests
    ```
    *(If you create a `requirements.txt` file, its content would be:*
    ```
    Flask>=2.0
    requests>=2.20
    ```
    *Then you could run `pip install -r requirements.txt`)*

4.  **Ensure Ollama Desktop is Running:** Start the Ollama application. It typically runs in the background.

## Running the Application

1.  **Navigate to the project directory** (the one containing `app.py`).
2.  **Run the Flask backend server:**
    ```bash
    python app.py
    ```
3.  **Open your web browser** (Chrome or Firefox recommended for best compatibility) and go to:
    [http://localhost:5000](http://localhost:5000) or [http://127.0.0.1:5000](http://127.0.0.1:5000)

## How to Use

1.  **Grant Webcam Permission:** When you first click "Start," your browser will ask for permission to access your webcam. You **must** click "Allow."
    * If you don't see a prompt or if it's blocked, check your browser's site settings for `http://localhost:5000` and your operating system's camera privacy settings to ensure your browser has access.
2.  **Enter Instruction (Prompt):** In the "Instruction (Prompt)" text area, type what you want the gemma model to describe or answer about the webcam image (e.g., "What object is in the center?", "Describe the scene.", "What colors are prominent?").
3.  **Adjust Interval (Optional):** Select the desired time interval between frame captures from the dropdown menu.
4.  **Click "Start":**
    * The webcam feed will appear.
    * The application will begin capturing frames at the specified interval.
    * Each captured frame will be sent with your instruction to the gemma model.
    * The model's response will appear in the "Response" text area.
5.  **View Saved Data:**
    * **Captions:** Open the `saved_captions/caption_history.txt` file to see a log of all instructions, responses, timestamps, and associated image filenames.
    * **Images:** Browse the `saved_images/` folder to see the individual frames that were processed. Images are named with a timestamp.
6.  **Click "Stop"** to halt the webcam feed and captioning process.

## Configuration Notes

* **Ollama API URL:** The Ollama API endpoint is currently hardcoded in `app.py` as `http://localhost:11434/api/generate`. If your Ollama instance runs on a different address or port, you'll need to modify this in `app.py`.
* **gemma Model:** The model used is `gemma3:4b`, also hardcoded in `app.py`. If you wish to use a different gemma variant available in your Ollama setup, change the `MODEL` variable in `app.py`.
* **Image Quality:** Captured frames are converted to JPEG format at the highest quality (1.0) before being sent to the model and saved. This is handled in `static/js/script.js`.

## Troubleshooting

* **"Webcam permission denied":**
    * Ensure you clicked "Allow" when the browser prompted for camera access.
    * Check browser site settings: Padlock icon in address bar -> Site Settings -> Camera -> Allow for `http://localhost:5000`.
    * Check OS camera permissions:
        * **Windows:** Settings -> Privacy & security -> Camera -> Allow apps & desktop apps.
        * **macOS:** System Settings -> Privacy & Security -> Camera -> Ensure your browser is checked.
* **No captions appear / "Could not connect to Ollama server":**
    * Verify that Ollama Desktop is running.
    * Confirm that the `gemma3:4b` model (or your chosen model) is downloaded and listed in `ollama list`.
    * Check the terminal where `python app.py` is running for any error messages from the Flask server or Ollama.
* **404 Errors for CSS/JS files:** Ensure your `static/css/style.css` and `static/js/script.js` files are correctly placed as per the project structure.

## Future Enhancements (Ideas)

* Allow model selection from the UI.
* Option to not save images/captions.
* Display saved images directly in the web interface.
* More robust error handling and user feedback.
* Package as a Docker container for easier deployment.

## License

This project is open-sourced under the MIT License.