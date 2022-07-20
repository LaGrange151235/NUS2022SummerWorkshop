#!/bin/bash
source ./venv/bin/activate
cd rasa
rasa run -m ./models/ --port 5002 --endpoints configs/endpoints.yml --credentials configs/credentials.yml --enable-api --cors "*"