import streamlit as st
import base64
import requests
from PIL import Image
import os
import json

SYSTEM_PROMPT = """You are an advanced OCR tool. Your task is to accurately transcribe the text from the provided image.
Please follow these guidelines to ensure the transcription is as correct as possible:
1. **Preserve Line Structure**: Transcribe the text exactly as it appears in the image, including line breaks.
2. **Avoid Splitting Words**: Ensure that words are fully formed, even if they appear across two lines or are partially obscured. Join word parts together appropriately to create complete words.
3. **Correct Unnatural Spacing**: Do not add extra spaces between characters in a word. Make sure the words are spaced naturally, without any unwanted breaks or gaps.
4. **Recognize and Correct Word Breaks**: If any word is mistakenly broken into parts, join them correctly to produce a natural, readable word. 
5. **No Additional Comments or Analysis**: Provide only the raw text as it appears in the image, without any additional analysis, comments, or summaries.
6. **Output as a Block of Text**: Output the entire transcribed text as a block, maintaining the line breaks, but ensuring that each word appears as it should, with correct spelling, no character-level splits, and no hyphenations unless they appear naturally in the image."""

def encode_image_to_base64(image_path):
    """Convert an image file to a base64 encoded string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

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

        # Join lines while preserving formatting
        return "\n".join(combined_result)

    except Exception as e:
        st.error(f"Error parsing response: {str(e)}")
        return response_text  # Return raw text if parsing fails

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
                # Remove line breaks and display as a single line
                st.text(initial_result.replace("\n", " "))

if __name__ == "__main__":
    main()
