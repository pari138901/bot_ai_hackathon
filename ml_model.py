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
      
    body = str.encode(data)  
  
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
        return result

    except urllib.error.HTTPError as error:  
        print("The request failed with status code: " + str(error.code))  
        print(error.info())  
        print(error.read().decode("utf8", 'ignore'))  

payload = json.dumps({'input_data': {'columns': ['PickupMonth', 'PickupDayOfWeek', 'PickupHour', 'PickupMinute', 'PickupLocationID', 'DropoffLocationID', 'TripDistance'], 'index': [0], 'data': [[3, 1, 13, 45, 45, 132, 24.7]]}})
res = call_ml_endpoint(payload)
# type(res)
# res2 = res.decode("utf-8")
# res2