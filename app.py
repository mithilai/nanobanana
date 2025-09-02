import streamlit as st
import requests
import base64
import io
from PIL import Image
from dotenv import load_dotenv
import os
import time

load_dotenv()

# FAL.AI Nano Banana endpoint
FAL_API_URL = "https://queue.fal.run/fal-ai/nano-banana/edit"
FAL_API_KEY = os.getenv("FAL_API_KEY")  # put your key here or in st.secrets

CREATE_URL = "https://queue.fal.run/fal-ai/nano-banana/edit"
STATUS_URL = "https://queue.fal.run/fal-ai/nano-banana/requests/{}/status"
RESULT_URL = "https://queue.fal.run/fal-ai/nano-banana/requests/{}"

st.set_page_config(page_title="Nano Banana Virtual Try-On", layout="centered")
st.title("Nano Banana Virtual Try-On (POC)")

# Paste URLs
model_url = st.text_input("Model Image URL (online link)")
cloth_url = st.text_input("Clothing Image URL (online link)")

if st.button("Generate Try-On") and model_url and cloth_url:
    st.info("Submitting job to Fal.ai...")

    headers = {
        "Authorization": f"Key {FAL_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": "make a photo of the model wearing the submitted clothing item and creating the themed background",
        "image_urls": [model_url, cloth_url]
    }

    # Step 1: Create Job
    res = requests.post(CREATE_URL, headers=headers, json=payload)
    if res.status_code != 200:
        st.error(f"Error creating job: {res.text}")
    else:
        request_id = res.json().get("request_id")
        st.write("✅ Job created. Request ID:", request_id)

        # Step 2: Poll Status
        status = "PENDING"
        with st.spinner("Waiting for job to complete..."):
            while status not in ["COMPLETED", "FAILED"]:
                time.sleep(5)
                check = requests.get(STATUS_URL.format(request_id), headers=headers)
                status = check.json().get("status", "UNKNOWN")
                st.write("Current Status:", status)

        # Step 3: Get Result
        if status == "COMPLETED":
            result = requests.get(RESULT_URL.format(request_id), headers=headers).json()
            st.json(result)  # Debug: show response

            img_url = None
            if "images" in result and len(result["images"]) > 0:
                img_url = result["images"][0].get("url")
            elif "image_url" in result:
                img_url = result["image_url"]

            if img_url:
                st.image(img_url, caption="Try-On Result", use_column_width=True)
            else:
                st.error("⚠️ No image found in response.")
        else:
            st.error("❌ Job failed.")