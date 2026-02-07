# FoodScan – Intelligent Food Health Analyzer

FoodScan is an AI-powered food scanning application that combines real-time barcode detection, nutritional lookup, and a strict health recommendation engine based on user health profile and WHO dietary guidelines.

It bridges computer vision, nutrition databases, rule-based medical logic, and LLM-assisted recommendations to deliver accurate food health assessments.

## Features

- Barcode scanning via image upload or live camera

- Personalized health recommendations based on user profile

- Real-time food data fetched from OpenFoodFacts API

- Health rules aligned with WHO dietary guidelines

- AI-assisted decision explanation using Groq LLM

- Deterministic, rule-based logic (no hallucinations)

- Age-aware recommendations (children & elderly)

- Clear decision output with primary health reason

- Lightweight, single-file Streamlit application


## Tech Stack

|Component          |Technology|
|-------------------|----------|
|Frontend UI	      |Streamlit|
|Backend Logic	    |Python|
|Barcode Detection	|OpenCV, Pyzbar|
|Image Processing	  |Pillow, NumPy|
|Food Data API	    |OpenFoodFacts|
|AI Model	          |Groq (LLaMA 3.1)|
|Rule Engine	      |WHO + Medical Logic|
|Deployment Ready	  |Streamlit Cloud / Local|
