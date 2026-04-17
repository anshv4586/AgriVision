import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras import layers, models

# Base pretrained model
base_model = MobileNetV2(weights="imagenet", include_top=False, input_shape=(224,224,3))
base_model.trainable = False

# Custom head. Note: Changed Dense output to 20 to properly match the 20 classes array in your app.py!
model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dense(64, activation="relu"),
    layers.Dense(20, activation="softmax")  # 20 classes
])

# Save model
model.save("model/plant_model.h5")

print("✅ Model created successfully!")
