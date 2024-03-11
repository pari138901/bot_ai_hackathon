import urllib.request
import json
import os
import ssl
from config import ml_key, ml_url

API_KEY = ml_key


def call_ml_endpoint(data):  
    # bypass the server certificate verification on client side
    if True and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context
      
    body = str.encode(json.dumps(data))  
  
    url = ml_url
      
    headers = {  
        'Content-Type': 'application/json',  
        'Authorization': 'Bearer ' + API_KEY,  
        'azureml-model-deployment': 'dreamywatch322w40-1'  
    }  
  
    req = urllib.request.Request(url, body, headers)  
  
    try:  
        response = urllib.request.urlopen(req)  
        result = response.read()  
        print(result)

    except urllib.error.HTTPError as error:  
        print("The request failed with status code: " + str(error.code))  
        print(error.info())  
        print(error.read().decode("utf8", 'ignore'))  