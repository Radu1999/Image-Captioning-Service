# Image-Captioning-Service

To run the service:

1. Build image captioning service docker image:

``cd src && docker build -t captioning-service``

2. Build redis docker image

``cd redis && docker build -t my-redis``

3. Run docker-compose

``docker-compose up -d``

The service will be available at 127.0.0.1:5000/predict
