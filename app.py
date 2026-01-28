import streamlit as st
import requests
import numpy as np
import google.generativeai as genai
from PIL import Image
import os

# ---------------- CONFIG ----------------
st.set_page_config(page_title="FoodScan", layout="centered")

# Gemini API key (set in Render Environment Variables)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# ---------------- FUNCTIONS ----------------

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
        "ingredients": product.get("ingredients_text", ""),
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

Give a clear recommendation:
- Recommended / Consume with caution / Not recommended
- Explain why in simple language.
"""
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text

# ---------------- UI ----------------

st.title("🥗 FoodScan – Smart Food Analyzer")

# ---- Health Profile ----
st.subheader("🧑‍⚕️ Health Profile")
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

# ---- Barcode Input ----
st.subheader("📦 Product Barcode")

barcode_data = st.text_input(
    "Enter barcode number (recommended for accuracy)",
    placeholder="e.g. 8901030695551"
)

# ---- Optional Image Upload (Preview only) ----
uploaded_file = st.file_uploader(
    "Optional: Upload product image (for reference)",
    type=["jpg", "png", "jpeg", "webp"]
)

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

# ---- Process Barcode ----
if barcode_data:
    st.success(f"Barcode entered: {barcode_data}")

    product = get_product_from_api(barcode_data)

    if product:
        st.subheader("📄 Product Info")
        st.write("**Name:**", product["name"])
        st.write("**Ingredients:**", product["ingredients"])

        st.subheader("🧠 Health Recommendation")
        with st.spinner("Analyzing with AI..."):
            result = health_decision(user_profile, product)

        st.info(result)
    else:
        st.error("❌ Product not found in OpenFoodFacts")
