from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
import numpy as np
from tensorflow.keras.models import load_model

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your Firebase frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
def root():
    return {"message": "API is running"}


# Load your model ONCE when the app starts
model = load_model("bone_model.keras")

def preprocess_image(image: Image.Image):
    # Resize image, convert to array, normalize - match your model’s input
    image = image.resize((256, 256))
    image_array = np.array(image) / 255.0
    image_array = np.expand_dims(image_array, axis=0)  # Add batch dim
    return image_array


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    print("Received file")
    contents = await file.read()
    print("Read file contents")
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    input_array = preprocess_image(image)
    print("Preprocessed image")
    prediction = model.predict(input_array)
    print(f"Prediction raw output: {prediction}")
    result = prediction_to_text(prediction)
    return {"result": result}


def prediction_to_text(prediction):
    # TODO: Change this to fit your model output
    # Example:
    if prediction[0][0] > 0.5:
        return "Fracture detected"
    else:
        return "No fracture detected"


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        input_array = preprocess_image(image)
        prediction = model.predict(input_array)
        result = prediction_to_text(prediction)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}



