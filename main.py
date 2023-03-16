from flask import Flask, jsonify, request
from flask_api import status
import torch
import torchvision.transforms as transforms
from PIL import Image
import requests
import io
from lavis.models import load_model_and_preprocess

app = Flask(__name__)

# Set the device to use
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load the pre-trained model
model, vis_processors, _ = load_model_and_preprocess(name="blip_caption",
                                                     model_type="base_coco", is_eval=True, device=device)
model.to(device)
model.eval()

# Define the route for the POST request
@app.route('/predict', methods=['POST'])
def predict():
    if len(request.json.keys()) != 1:
        return "Pass only image url", status.HTTP_400_BAD_REQUEST

    try:
        image_url = request.json['image']
    except KeyError or AssertionError:
        return "Pass only image url", status.HTTP_400_BAD_REQUEST

    try:
        # Download the image from the URL
        response = requests.get(image_url)
        image_bytes = io.BytesIO(response.content)
        # Convert to a PIL Image object
        image = Image.open(image_bytes)
    except:
        return "Invalid url / Corrupted Image", status.HTTP_400_BAD_REQUEST

    # Forward pass through the model
    with torch.no_grad():
        # vis_processors stores image transforms for "train" and "eval" (validation / testing / inference)
        image = vis_processors["eval"](image).unsqueeze(0).to(device)
        # generate caption
        answer = model.generate({"image": image})

    return jsonify(answer), status.HTTP_200_OK


if __name__ == '__main__':
    app.run(debug=True)
