from flask import Flask, jsonify, request
from flask_api import status
from PIL import Image
import requests
import io
from model_loader import ModelLoader

app = Flask(__name__)
model_loader = ModelLoader()


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
        return "Invalid url / Corrupted Image", stdatus.HTTP_400_BAD_REQUEST

    answer = model_loader.predict(image)
    return jsonify(answer), status.HTTP_200_OK


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
