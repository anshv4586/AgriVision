import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.resnet import preprocess_input
import keras

@keras.saving.register_keras_serializable(name='preprocess_input')
def custom_preprocess_input(x):
    return preprocess_input(x)


app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ Load model
model = load_model("model/best_resnet.h5", custom_objects={'preprocess_input': custom_preprocess_input})

# ✅ Class labels
classes = ["Blight", "Healthy", "Spot"]

# ✅ Disease explanations
DISEASE_INFO = {
    "Rust":    "Fungal disease caused by high humidity. Spreads rapidly via spores and causes orange/brown pustules on leaves, severely reducing photosynthesis.",
    "Blight":  "Severe infection that damages leaves, stems and fruits. Can wipe out an entire crop quickly. Usually caused by Phytophthora or Alternaria species.",
    "Spot":    "Leaf spot disease caused by bacteria or fungi. Manifests as dark circular spots with yellow halos. Thrives in warm, wet conditions.",
    "Healthy": "Plant is healthy and growing well. Continue regular care — maintain optimal watering, nutrient balance and monitor for early signs of stress."
}

# ✅ Crop-specific suggestions
CROP_SUGGESTIONS = {
    "Rice":     { "Rust": ["Maintain water level","Avoid high humidity","Use fungicide spray"], "Blight": ["Improve drainage","Avoid excess nitrogen","Remove infected plants"], "Spot": ["Apply fungicide","Increase plant spacing"], "Healthy": ["Maintain irrigation schedule"] },
    "Wheat":    { "Rust": ["Apply propiconazole","Use resistant seeds"], "Blight": ["Remove infected leaves","Balanced fertilizer"], "Spot": ["Spray copper fungicide"], "Healthy": ["Regular monitoring"] },
    "Maize":    { "Blight": ["Use Mancozeb spray","Avoid waterlogging"], "Spot": ["Remove infected leaves","Improve airflow"], "Rust": ["Apply fungicide"], "Healthy": ["Maintain soil nutrients"] },
    "Sugarcane":{ "Rust": ["Use resistant variety","Apply fungicide"], "Blight": ["Improve drainage","Remove infected leaves"], "Spot": ["Avoid overwatering"], "Healthy": ["Regular irrigation"] },
    "Mustard":  { "Rust": ["Spray sulfur fungicide"], "Blight": ["Remove infected parts"], "Spot": ["Improve air circulation"], "Healthy": ["Maintain soil moisture"] },
    "Barley":   { "Rust": ["Use resistant seeds","Apply fungicide"], "Blight": ["Balanced fertilization"], "Spot": ["Spray treatment"], "Healthy": ["Regular monitoring"] },
    "Potato":   { "Blight": ["Apply Mancozeb","Avoid leaf wetness"], "Spot": ["Remove infected leaves"], "Rust": ["Control humidity"], "Healthy": ["Maintain soil nutrients"] },
    "Tomato":   { "Blight": ["Use fungicide","Avoid water on leaves"], "Spot": ["Remove infected leaves","Improve airflow"], "Rust": ["Control humidity"], "Healthy": ["Use organic compost"] },
    "Spinach":  { "Spot": ["Apply fungicide"], "Blight": ["Avoid overwatering"], "Rust": ["Improve ventilation"], "Healthy": ["Maintain moisture"] },
    "Coriander":{ "Spot": ["Spray neem oil"], "Blight": ["Remove infected leaves"], "Rust": ["Avoid humidity"], "Healthy": ["Maintain irrigation"] },
    "Cabbage":  { "Blight": ["Apply fungicide"], "Spot": ["Remove affected leaves"], "Rust": ["Improve airflow"], "Healthy": ["Use organic fertilizer"] },
    "Marigold": { "Spot": ["Apply fungicide"], "Blight": ["Remove infected flowers"], "Rust": ["Reduce humidity"], "Healthy": ["Maintain soil moisture"] },
    "Rose":     { "Spot": ["Spray fungicide"], "Blight": ["Remove infected parts"], "Rust": ["Use sulfur spray"], "Healthy": ["Regular pruning"] },
    "Bougainvillea":{ "Spot": ["Avoid overwatering"], "Blight": ["Improve drainage"], "Rust": ["Maintain airflow"], "Healthy": ["Minimal watering"] },
    "Tulip":    { "Blight": ["Remove infected bulbs"], "Spot": ["Apply fungicide"], "Rust": ["Avoid humidity"], "Healthy": ["Maintain soil conditions"] },
    "Chrysanthemum":{ "Spot": ["Spray fungicide"], "Blight": ["Remove infected parts"], "Rust": ["Control humidity"], "Healthy": ["Maintain sunlight"] },
    "Dahlia":   { "Spot": ["Apply fungicide"], "Blight": ["Remove infected parts"], "Rust": ["Reduce humidity"], "Healthy": ["Regular watering"] },
    "Petunia":  { "Spot": ["Spray fungicide"], "Blight": ["Improve airflow"], "Rust": ["Control humidity"], "Healthy": ["Maintain sunlight"] },
    "Sunflower":{ "Rust": ["Apply fungicide"], "Blight": ["Remove infected heads"], "Spot": ["Improve spacing"], "Healthy": ["Maintain soil nutrients"] },
    "Other":    { "Rust": ["Apply fungicide","Reduce humidity"], "Blight": ["Remove infected parts"], "Spot": ["Avoid overwatering"], "Healthy": ["Maintain conditions"] },
}

def preprocess_image(img_path):
    img = Image.open(img_path).convert("RGB")
    img = img.resize((224, 224))
    img = np.array(img, dtype=np.float32)  # Removed / 255.0, ResNet's internal preprocess_input handles scaling
    img = np.expand_dims(img, axis=0)
    return img

try:
    from sensor import get_sensor_data
except ImportError:
    print("Warning: Could not import sensor module")
    def get_sensor_data():
        return None

@app.route("/sensor")
def sensor():
    data = get_sensor_data()

    if data:
        return jsonify(data)
    else:
        return jsonify({
            "temp": 0,
            "humidity": 0,
            "moisture": 0,
            "alerts": []
        })

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        file = request.files["image"]
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # 🔥 Prediction
        img = preprocess_image(filepath)
        pred = model.predict(img)

        class_index = int(np.argmax(pred))
        confidence = float(np.max(pred)) * 100
        disease = classes[class_index]

        # 🔥 Severity logic
        if confidence > 85:
            severity = "High"
        elif confidence > 70:
            severity = "Medium"
        else:
            severity = "Low"

        # 🌱 Crop-specific suggestions
        crop = request.form.get("crop", "Other")
        suggestions = CROP_SUGGESTIONS.get(crop, CROP_SUGGESTIONS["Other"]).get(disease, [])
        
        # 🐛 DEBUG
        print(f"DEBUG predict -> crop='{crop}' disease='{disease}' suggestions={suggestions}")

        return jsonify({
            "disease": disease,
            "confidence": round(confidence, 2),
            "severity": severity,
            "description": DISEASE_INFO.get(disease, "No information available for this condition."),
            "suggestions": suggestions
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # 🔥 use_reloader=False is REQUIRED when using Serial ports
    app.run(debug=True, use_reloader=False)
