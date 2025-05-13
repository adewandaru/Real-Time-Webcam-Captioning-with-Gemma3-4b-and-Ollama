document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('webcam');
    const canvas = document.getElementById('canvas');
    const statusElement = document.getElementById('status');
    const toggleStreamButton = document.getElementById('toggleStreamButton');
    const refreshIntervalSelect = document.getElementById('refreshInterval');
    const errorMessageArea = document.getElementById('error-message-area');

    // const baseApiInput = document.getElementById('baseApi'); // Removed
    const instructionTextarea = document.getElementById('instruction');
    const responseTextarea = document.getElementById('response');

    let stream;
    let captureIntervalId;
    let isStreaming = false;

    function displayError(message) {
        errorMessageArea.textContent = message;
        errorMessageArea.style.display = 'block';
        statusElement.textContent = 'Error!';
        console.error(message);
    }

    function clearError() {
        errorMessageArea.textContent = '';
        errorMessageArea.style.display = 'none';
    }

    async function startWebcam() {
        clearError();
        statusElement.textContent = 'Initializing webcam...';
        responseTextarea.value = '';

        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            displayError('Your browser does not support MediaDevices API. Try a different browser.');
            return;
        }

        try {
            stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 640 }, // Request ideal width
                    height: { ideal: 480 }, // Request ideal height
                    facingMode: "user"
                }
            });

            video.srcObject = stream;
            video.onloadedmetadata = () => {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                isStreaming = true;
                toggleStreamButton.textContent = 'Stop';
                toggleStreamButton.classList.add('stop-button');
                statusElement.textContent = 'Webcam active. Capturing...';
                startCaptureInterval();
            };
        } catch (error) {
            console.error('Error accessing webcam:', error);
            let userMessage = 'Could not access the webcam.';
            if (error.name === "NotAllowedError" || error.name === "PermissionDeniedError") {
                userMessage = "Webcam permission denied. Please allow camera access in your browser and system settings, then try again.";
            } else if (error.name === "NotFoundError" || error.name === "DevicesNotFoundError") {
                userMessage = "No webcam found. Ensure a webcam is connected and enabled.";
            } else if (error.name === "NotReadableError" || error.name === "TrackStartError") {
                userMessage = "Webcam is already in use or encountered a hardware error.";
            }
            displayError(userMessage);
            statusElement.textContent = "Webcam error!";
        }
    }

    function stopWebcam() {
        clearError();
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
        video.srcObject = null;
        isStreaming = false;
        toggleStreamButton.textContent = 'Start';
        toggleStreamButton.classList.remove('stop-button');
        statusElement.textContent = 'Idle. Click Start.';
        clearInterval(captureIntervalId);
        console.log("Webcam stopped.");
    }

    toggleStreamButton.addEventListener('click', () => {
        if (isStreaming) {
            stopWebcam();
        } else {
            startWebcam();
        }
    });

    function startCaptureInterval() {
        clearInterval(captureIntervalId);
        const refreshRate = parseInt(refreshIntervalSelect.value, 10);
        if (isNaN(refreshRate) || refreshRate < 500) { // Min refresh rate
            displayError("Invalid refresh rate selected. Minimum is 500ms.");
            if (isStreaming) stopWebcam(); // Stop streaming if rate is invalid
            return;
        }
        statusElement.textContent = `Capturing every ${refreshRate / 1000}s...`;
        // Initial capture, then interval
        if (isStreaming) captureFrameAndSend(); // Only capture if still streaming
        captureIntervalId = setInterval(() => {
            if (isStreaming) captureFrameAndSend(); // Check again before sending
        }, refreshRate);
    }

    refreshIntervalSelect.addEventListener('change', () => {
        if (isStreaming) {
            startCaptureInterval(); // Restart interval with new rate
        }
    });

    async function captureFrameAndSend() {
        if (!isStreaming || video.paused || video.ended || video.readyState < 3) {
            return;
        }

        const context = canvas.getContext('2d');
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Get image data as Base64. Use JPEG with max quality (1.0).
        const imageDataUrl = canvas.toDataURL('image/jpeg', 1.0);
        const base64Image = imageDataUrl.split(',')[1]; // Remove the "data:image/jpeg;base64," part

        if (!base64Image) {
            console.error("Failed to get base64 image data from canvas.");
            return;
        }

        statusElement.textContent = 'Sending frame...';
        // const currentApiUrl = baseApiInput.value.trim(); // Removed
        const currentInstruction = instructionTextarea.value.trim();

        if (!currentInstruction) {
            displayError("Instruction (Prompt) cannot be empty.");
            statusElement.textContent = 'Prompt missing!';
            // Optionally stop capture if prompt is missing
            // stopWebcam();
            return;
        }

        try {
            const backendResponse = await fetch('/api/caption', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    image_data: base64Image,
                    // ollama_api_url: currentApiUrl, // Removed
                    prompt: currentInstruction
                }),
            });

            const data = await backendResponse.json();

            if (!backendResponse.ok) {
                throw new Error(data.error || `Server error: ${backendResponse.status}`);
            }

            if (data.caption) {
                responseTextarea.value = data.caption;
                const currentRefreshRate = parseInt(refreshIntervalSelect.value, 10);
                statusElement.textContent = `Capturing every ${currentRefreshRate / 1000}s...`;
                clearError(); // Clear previous errors if successful
            } else {
                responseTextarea.value = "No caption received or error in response.";
                statusElement.textContent = 'Response issue.';
            }
        } catch (error) {
            console.error('Error during caption generation:', error);
            displayError(`Failed to get caption: ${error.message}`);
            responseTextarea.value = `Error: ${error.message}`;
            statusElement.textContent = 'Captioning error!';
        }
    }

    statusElement.textContent = 'Idle. Click Start.';
});