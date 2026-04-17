import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
from tensorflow.keras.models import load_model
import numpy as np

print("Loading model...")
model = load_model("model/plant_model.h5")
print("Model loaded.")
img = np.random.rand(1, 224, 224, 3).astype('float32')
print("Predicting...")
pred = model.predict(img)
print("Predicted:", pred)
