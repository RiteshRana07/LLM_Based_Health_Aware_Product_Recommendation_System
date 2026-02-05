%%writefile app.py
import streamlit as st
import cv2
import requests
import numpy as np
from pyzbar.pyzbar import decode
import google.generativeai as genai
from PIL import Image

# ---------------- CONFIG ----------------
st.set_page_config(page_title="FoodScan", layout="centered")

#  Replace with st.secrets["GEMINI_API_KEY"] in production
genai.configure(api_key=st.secrets"GEMINI_API_KEY")

# ---------------- FUNCTIONS ----------------

def scan_barcode(image):
    """
    Detect barcode from RGB image
    """
    img = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    barcodes = decode(img)
    if not barcodes:
        return None, None
    barcode = barcodes[0]
    return barcode.data.decode("utf-8"), barcode

def get_product_from_api(barcode):
    url = f"https://world.openfoodfacts.net/api/v2/product/{barcode}"
    r = requests.get(url)
    if r.status_code != 200:
        return None

    data = r.json()
    if data.get("status") != 1:
        return None

    product = data.get("product", {})
    return {
        "name": product.get("product_name", "Unknown"),
        "nutriments": product.get("nutriments", {}),
        "ingredients": product.get("ingredients_text", "No ingredients present"),
        "labels": product.get("labels", "")
    }

def health_decision(user, product):
    prompt = f"""
You are a food health recommendation system.

User profile:
- Diabetes: {user['diabetes']}
- BP: {user['bp']}
- Heart disease: {user['heart']}
- Age: {user['age']}
- Diet: {user['diet']}

Food nutrition (per 100g):
- Sugar: {product['nutriments'].get('sugars_100g', 0)}
- Salt: {product['nutriments'].get('salt_100g', 0)}
- Saturated Fat: {product['nutriments'].get('saturated-fat_100g', 0)}

Rules:
0. If ingredients is not present -> Not Recommended
1. Diabetes AND sugar > 10 → Not Recommended
2. BP AND salt > 0.6 → Not Recommended
3. Heart disease AND fat > 5 → Consume with Caution
4. Age < 5 AND sugar > 8 → Not Recommended
5. Age 5–12 AND sugar > 8 → Consume with Caution
6. Age > 60 AND salt > 0.5 → Consume with Caution
7. Age > 60 AND fat > 6 → Consume with Caution
8. Else → Recommended
9. Sugar > 10 AND sugar ≤ 15 → Consume with Caution
10. Salt > 1.0 → Not Recommended
11. Salt > 0.6 AND salt ≤ 1.0 → Consume with Caution
12. Saturated fat > 10 → Not Recommended
13. Saturated fat > 5 AND fat ≤ 10 → Consume with Caution
14. Sugar > 10 AND salt > 0.6 → Not Recommended
15. Sugar > 10 AND fat > 5 → Not Recommended
16. Age > 60 AND sugar > 8 AND salt > 0.5 → Not Recommended
17. Age ≤ 12 AND (sugar > 12 OR salt > 0.8) → Not Recommended
18. Else → Recommended

Give a clear recommendation based on the Rules which is mentioned above and strictly go through and follow the Rules:
- Recommended / Consume with caution / Not recommended
- Explain why in simple language with 30 words.
"""
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text

# ---------------- UI ----------------

st.title(" FoodScan – Smart Food Analyzer")

# ---- Health Profile ----
st.subheader(" Health Profile")
age = st.number_input("Age", min_value=1, max_value=120, value=24)
diet = st.selectbox("Diet Type", ["Vegetarian", "Non-Vegetarian"])
diabetes = st.checkbox("Diabetes")
bp = st.checkbox("High Blood Pressure")
heart = st.checkbox("Heart Disease")

user_profile = {
    "age": age,
    "diet": diet,
    "diabetes": diabetes,
    "bp": bp,
    "heart": heart
}

st.divider()

# ---- Scan Mode ----
scan_mode = st.radio("Choose scan method", [" Upload Image", " Camera Scan"])

image = None

# ---- Upload Image ----
if scan_mode == " Upload Image":
    uploaded_file = st.file_uploader(
        "Upload barcode image",
        type=["jpg", "png", "jpeg", "webp"]
    )

    if uploaded_file:
        image_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# ---- Camera Scan ----
elif scan_mode == " Camera Scan":
    camera_image = st.camera_input("Scan barcode using camera")

    if camera_image is not None:
        pil_image = Image.open(camera_image)
        image = np.array(pil_image)

# ---- Process Image ----
if image is not None:
    if image.ndim not in [2, 3]:
        st.error("Invalid image format")
        st.stop()

    st.image(image, caption="Input Image", use_column_width=False)

    barcode_data, barcode_obj = scan_barcode(image)

    if barcode_data:
        st.success(f" Barcode detected: {barcode_data}")

        # draw bounding box
        x, y, w, h = barcode_obj.rect
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        st.image(image, caption="Detected Barcode", use_column_width=True)

        product = get_product_from_api(barcode_data)

        if product:
            st.subheader(" Product Info")
            st.write("**Name:**", product["name"])
            st.write("**Ingredients:**", product["ingredients"])

            st.subheader(" Health Recommendation")
            with st.spinner("Analyzing with AI..."):
                result = health_decision(user_profile, product)

            st.info(result)
        else:
            st.error(" Product not found in OpenFoodFacts")
    else:
        st.error(" No barcode detected. Try better lighting or angle.")
