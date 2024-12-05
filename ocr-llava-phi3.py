import streamlit as st
import base64
import requests
from PIL import Image
import os
import json

SYSTEM_PROMPT = """Please provide the text in the image without adding any comment or summary."""



def encode_image_to_base64(image_path):
    """Convert an image file to a base64 encoded string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

    """Perform OCR on the given image using Llama 3.2-Vision."""
    base64_image = encode_image_to_base64(image_path)
    response = requests.post(
        "http://localhost:11434/api/chat",  # Ensure this URL matches your Ollama service endpoint
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
        try:
            response_text = response.text
            json_objects = response_text.splitlines()
            combined_result = set()  # Using a set to avoid duplicates
            for json_object in json_objects:
                parsed_json = json.loads(json_object)
                content = parsed_json.get("message", {}).get("content", "")
                if content:
                    combined_result.add(content.strip())  # Add to set to avoid duplicate entries
            return " ".join(combined_result).strip()
        except json.JSONDecodeError as e:
            st.error("Failed to parse JSON response.")
            st.write("Raw Response:", response.text)
            return None
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
        st.write("Response Body:", response.text)  # Additional logging to help debug
        return None

def perform_ocr(image_path):
    """Perform OCR on the given image using Llama 3.2-Vision."""
    base64_image = encode_image_to_base64(image_path)
    response = requests.post(
        "http://localhost:11434/api/chat",  # Ensure this URL matches your Ollama service endpoint
        json={
            "model": "llava-phi3",
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
        try:
            response_text = response.text
            json_objects = response_text.splitlines()
            combined_result = []
            for json_object in json_objects:
                try:
                    parsed_json = json.loads(json_object)
                    content = parsed_json.get("message", {}).get("content", "")
                    if content and content.strip():
                        combined_result.append(content.strip())
                except json.JSONDecodeError:
                    # Skip any lines that are not valid JSON
                    continue
            # Join the lines while ensuring no duplicates or empty strings
            unique_lines = list(dict.fromkeys(combined_result))
            result = " ".join(unique_lines)  # Join lines with a space instead of newline to maintain sentence flow
            return result
        except json.JSONDecodeError as e:
            st.error("Failed to parse JSON response.")
            st.write("Raw Response:", response.text)
            return None
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
        st.write("Response Body:", response.text)  # Additional logging to help debug
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
        # Ensure the 'temp' directory exists
        os.makedirs("temp", exist_ok=True)
        
        with open(os.path.join("temp", uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
            image_path = f.name
        
        # Display the uploaded image
        image = Image.open(image_path)
        st.image(image, caption="Uploaded Image", use_container_width=True)
        
        # Perform OCR when the button is clicked
        if st.button("Run OCR"):
            result = perform_ocr(image_path)
            if result:
                st.subheader("OCR Recognition Result:")
                st.text(result)

if __name__ == "__main__":
    main()