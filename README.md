# OCR Assistant with Llama 3.2-Vision

This guide will help you set up and run an OCR Assistant using Streamlit, Llama 3.2-Vision, and Ollama. The application allows you to upload an image and analyze it for visible text using an OCR model.

## Prerequisites

- Python 3.8 or higher on your MacOS, Linux, or Windows 

## Installation Instructions

### Step 1: Install Ollama and Llama 3.2-Vision

1. **Install Ollama**
   
   First, you need to install Ollama on your local machine. To do so, run:
   ```bash
   curl -sSfL https://ollama.com/download | sh
   ```
   This command will download and install Ollama.

2. **Install Llama 3.2-Vision**

   To install the Llama 3.2-Vision model, run:
   ```bash
   ollama pull llama3.2-vision
   ```
   This will pull the Llama 3.2-Vision model from the Ollama repository, making it available for your local service.

### Step 2: Set Up the Virtual Environment

1. **Create and Activate a Virtual Environment**

   It is recommended to use a virtual environment for the project to avoid package conflicts. Navigate to the project folder and run the following command to create a virtual environment:
   ```bash
   python -m venv venv
   ```

   To activate the virtual environment:
   - On **Windows**:
     ```bash
     venv\Scripts\activate
     ```
   - On **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

2. **Install the Required Packages**

   With the virtual environment activated, install the necessary dependencies by running:
   ```bash
   pip install -r requirements.txt
   ```

   The `requirements.txt` file contains the following dependencies:
   - `streamlit`
   - `requests`
   - `Pillow`

### Step 3: Run the Ollama Server

To use Llama 3.2-Vision, you need to start the Ollama server:
```bash
ollama serve
```

This command will start the Ollama server on `http://localhost:11434`, allowing the model to be accessed through API requests.

### Step 4: Run the OCR Application

1. **Launch the Streamlit Application**

   To start the OCR Assistant with Llama 3.2-Vision, run the following command in the project folder:
   ```bash
   streamlit run ocr_app.py
   ```

2. **Usage**

   - The Streamlit interface will open in your default browser.
   - Upload an image file (JPG, JPEG, or PNG format).
   - Click the "Run OCR" button to analyze the image for visible text.

## Notes
- Ensure the Ollama server is running before starting the Streamlit app, as the app relies on the server to process images.
- Replace the path to the logo in the code (`path/to/your/logo.png`) if you have a logo to display in the application header.

## Troubleshooting
- **404 Error**: If you encounter a 404 error when trying to use the OCR functionality, ensure the Ollama server is running and accessible at the specified endpoint (`http://localhost:11434/api/chat`).
- **Missing Dependencies**: Ensure all dependencies are installed in the virtual environment by using `pip install -r requirements.txt`.

## License
This project is open-source and available under the MIT License.

# Code Explanation for OCR Assistant with Llama 3.2-Vision

Following provides a line-by-line explanation of the Python code used for building the OCR assistant using Streamlit, Llama 3.2-Vision, and Ollama.


```python
import streamlit as st
import base64
import requests
from PIL import Image
import os
import json
```
- **Import Libraries**: Import required Python libraries, including Streamlit for the UI, `base64` for encoding images, `requests` for making HTTP requests, `PIL` for image handling, `os` for file operations, and `json` for JSON data.

```python
SYSTEM_PROMPT = """You are an advanced OCR tool. Your task is to accurately transcribe the text from the provided image...
"""
```
- **System Prompt**: Defines the guidelines for transcription to be followed by the OCR tool.

### Encode Image to Base64
```python
def encode_image_to_base64(image_path):
    """Convert an image file to a base64 encoded string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
```
- **encode_image_to_base64(image_path)**: This function takes an image path and converts the image to a base64-encoded string.

### Parse Response
```python
def parse_response(response_text):
    """Parse the response text from the model."""
    try:
        json_objects = response_text.splitlines()
        combined_result = []

        for json_object in json_objects:
            try:
                parsed_json = json.loads(json_object)
                content = parsed_json.get("message", {}).get("content", "")
                if content and content.strip():
                    combined_result.append(content.strip())
            except json.JSONDecodeError:
                combined_result.append(json_object.strip())

        return "\n".join(combined_result)

    except Exception as e:
        st.error(f"Error parsing response: {str(e)}")
        return response_text
```
- **parse_response(response_text)**: Parses the response text from the OCR model and handles exceptions if parsing fails.

### Perform OCR
```python
def perform_ocr(image_path):
    """Perform OCR on the given image using Llama 3.2-Vision."""
    base64_image = encode_image_to_base64(image_path)
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "llama3.2-vision",
            "messages": [
                {
                    "role": "user",
                    "content": SYSTEM_PROMPT,
                    "images": [base64_image],
                },
            ],
        }
    )
    if response.status_code == 200:
        return parse_response(response.text)
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
        return None
```
- **perform_ocr(image_path)**: This function sends the encoded image to an OCR endpoint and returns the parsed result.

### Main Function
```python
def main():
    try:
        logo_base64 = base64.b64encode(open('MinimalDevopsLogo.png', 'rb').read()).decode('utf-8')
        st.markdown(
            """
            <div style="display: flex; align-items: center;">
                <img src="data:image/png;base64,{}" width="50" style="margin-right: 10px;"/>
                <h1>OCR Assistant with Llama 3.2-Vision</h1>
            </div>
            """.format(logo_base64), unsafe_allow_html=True
        )
    except FileNotFoundError:
        st.title("OCR Assistant with Llama 3.2-Vision")

    uploaded_file = st.file_uploader("Upload an image file for OCR analysis", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        os.makedirs("temp", exist_ok=True)
        
        with open(os.path.join("temp", uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
            image_path = f.name
        
        image = Image.open(image_path)
        st.image(image, caption="Uploaded Image", use_container_width=True)
        
        if st.button("Run OCR"):
            initial_result = perform_ocr(image_path)
            if initial_result:
                st.subheader("OCR Recognition Result:")
                st.text(initial_result.replace("\n", " "))
```
- **main()**: The main function defines the Streamlit UI. It handles image upload, displays the image, and runs the OCR when the user clicks the button.

```python
if __name__ == "__main__":
    main()
```
- **if __name__ == "__main__": main()**: Runs the `main()` function when the script is executed directly.

## How to Use
1. Install the required libraries:
   ```sh
   pip install streamlit requests pillow
   ```
2. Run the application using Streamlit:
   ```sh
   streamlit run your_script.py
   ```
3. Upload an image, and click on **Run OCR** to perform the OCR analysis.

## Requirements
- Python 3.x
- Streamlit
- Requests
- Pillow (PIL)


This explanation should give you a clear understanding of how each part of the code contributes to the overall OCR assistant functionality. Feel free to experiment by adding more features or making customizations to the code!

