import streamlit as st
import base64
import requests
from PIL import Image
import os
import json

def encode_image_to_base64(image_path):
    """Convert an image file to a base64 encoded string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def perform_ocr(image_path):
    """Perform OCR on the given image using the provided API."""
    base64_image = encode_image_to_base64(image_path)

    # API request payload
    payload = {
        "model": "llava-phi-3-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Please provide the text in the image without adding any comment or summary"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                ]
            }
        ],
        "temperature": 0.7,
        "max_tokens": -1,
        "stream": False
    }

    # Send POST request to the API
    response = requests.post(
        "http://localhost:1234/v1/chat/completions",
        headers={"Content-Type": "application/json"},
        json=payload,
    )

    if response.status_code == 200:
        try:
            response_json = response.json()
            # Extract the content from the response
            choices = response_json.get("choices", [])
            if choices and "message" in choices[0] and "content" in choices[0]["message"]:
                return choices[0]["message"]["content"].strip()
            else:
                return "No text found in the image."
        except json.JSONDecodeError:
            st.error("Failed to parse JSON response.")
            st.write("Raw Response:", response.text)
            return None
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
        return None

def main():
    try:
        st.title("OCR Assistant with llava-phi-3-mini")
    except FileNotFoundError:
        st.title("OCR Assistant")

    uploaded_file = st.file_uploader("Upload an image file for OCR analysis", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        os.makedirs("temp", exist_ok=True)

        with open(os.path.join("temp", uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
            image_path = f.name

        image = Image.open(image_path)
        st.image(image, caption="Uploaded Image", use_container_width=True)

        if st.button("Run OCR"):
            result = perform_ocr(image_path)
            if result:
                st.subheader("OCR Recognition Result:")
                # Remove line breaks and display as a single line
                st.text(result.replace("\n", " "))

if __name__ == "__main__":
    main()
