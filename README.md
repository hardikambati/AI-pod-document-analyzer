# 📦 POD Image Analyzer

A FastAPI-based backend service that leverages Gemini AI API to extract structured delivery information from Proof of Delivery (POD) images.

---

## 🚀 Features

- Analyze POD images using **Gemini API**
- Extract critical delivery metadata:
  - `text_quality_score`
  - `courier_partner`
  - `awb_number`
  - `recipient_name`
  - `recipient_address`
  - `recipient_signature`
  - `recipient_stamp`
  - `delivery_date`
  - `handwritten_notes`

---

## 🛠️ Tech Stack

- **FastAPI** – Web framework for Python
- **Gemini API** – Google's AI processing model
- **Pydantic** – Data validation and parsing
- **Uvicorn** – ASGI server for running FastAPI

---

## Spinning up the server

1. Install dependencies in virtual environment
```
pip install -r requirements.txt
```
2. Spin up the server
```
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
3. Open docs
```
http://localhost:8000/docs
```