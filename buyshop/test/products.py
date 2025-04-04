#!/usr/bin/python3
import requests

# Define the URL of your endpoint
url = 'http://localhost:8000/product/create/'

# Define the headers
headers = {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQzNzg3ODI0LCJpYXQiOjE3NDM3ODQyMjQsImp0aSI6ImMwYjIyMDU0ZmU1MzRhMjU4YWY4MWI2N2FjMGExZDhiIiwidXNlcl9pZCI6ImIxMGJhM2YxLTE1YWYtNDg5MS1iYzBhLTlmNmJmODgzM2RkMyJ9._n5GiE9z-p5TSCExAfYjGRVF_dYv1r7flKkwTkc7ENk',
    'Content-Type': 'application/json'
}

# Define the product data payload
data = {
    "name": "Samsung Galaxy S22",
    "description": "Latest model with stunning camera and battery life",
    "price": 450000,
    "quantity": 10,
    "condition": "new",
    "categories": ["Electronics", "Smartphones"]
}

# Send the POST request
response = requests.post(url, json=data, headers=headers)

# Check if the request was successful
if response.status_code == 201:
    print("Product created successfully!")
    print("Response:", response.json())
else:
    print("Failed to create product.")
    print("Status Code:", response.status_code)
    print("Response:", response.text)
