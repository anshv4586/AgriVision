# 🌿 AgriVision AI — Plant Health Advisor

An AI-powered plant disease detection system with real-time Arduino sensor integration.

## 🚀 Features
- 🤖 **AI Image Analysis** — MobileNetV2 model detects Rust, Blight, Spot, Healthy
- 📡 **Live Sensor Data** — Real-time Moisture, Temperature, Humidity from Arduino (COM10)
- 🌾 **Crop-Specific Advice** — Tailored suggestions for 20+ crops
- 🔴 **Smart Alerts** — Auto-generated warnings based on sensor thresholds
- 🎨 **Premium Dark UI** — Glassmorphism design with live data visualization

## 🛠️ Setup

### 1. Install Dependencies
```bash
pip install flask flask-cors tensorflow numpy Pillow pyserial
```

### 2. Set Environment Variable
```bash
set TF_USE_LEGACY_KERAS=1
```

### 3. Run the App
```bash
python app.py
```

### 4. Open Browser
Go to: `http://127.0.0.1:5000/`

## 📁 Project Structure
```
agrivision/
├── app.py              # Flask backend + AI prediction
├── sensor.py           # Arduino serial communication
├── train.py            # Model training script
├── create_model.py     # Model architecture
├── model/
│   └── plant_model.h5  # Trained TensorFlow model
├── templates/
│   └── index.html      # Frontend UI
└── uploads/            # Temporary image uploads
```

## 🔌 Hardware
- Arduino connected to **COM10**
- Sensors: Moisture, DHT11 (Temp + Humidity)
- Output format: `Time(ms), Temp(C), Humidity(%), Moisture(%)`

## 👨‍💻 Built by
**Lazy Coders** — Btech CSE
