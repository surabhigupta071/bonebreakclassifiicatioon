from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
import numpy as np
import tensorflow as tf

app = FastAPI()

# Allow all origins for now (change to your frontend URL in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load your trained model on startup
model = tf.keras.models.load_model("bone_model.keras")

def preprocess_image(image: Image.Image):
    # Example preprocessing — adjust to your model's input size
    target_size = (224, 224)  # change to your model's expected input size
    image = image.resize(target_size)
    image_array = np.array(image) / 255.0  # normalize pixel values
    if image_array.shape[-1] == 4:  # if image has alpha channel, remove it
        image_array = image_array[..., :3]
    image_array = np.expand_dims(image_array, axis=0)  # add batch dim
    return image_array

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    processed = preprocess_image(image)

    prediction = model.predict(processed)
    
    # Interpret prediction — this depends on your model output format
    # For example, if it's binary classification (fracture or not):
    pred_prob = prediction[0][0]  # adjust indexing based on output shape
    if pred_prob > 0.5:
        result = f"Fracture detected with confidence {pred_prob:.2f}"
    else:
        result = f"No fracture detected with confidence {1 - pred_prob:.2f}"

    return {"result": result}

