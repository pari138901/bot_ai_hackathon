from openai import AzureOpenAI
import pyodbc
import streamlit as st
from streamlit_chat import message
from ml_model import call_ml_endpoint
import json
from datetime import datetime
import pytz
import random

# Database connection parameters
DATABASE_CONFIG = {
    'server': 'pgjr-sqlserver.database.windows.net,1433',
    'database': 'pgjr-sqldb',
    'username': 'rtslabs',
    'password': 'LhcW05#Z',
    'driver': '{ODBC Driver 17 for SQL Server}',
}


# Initialize chat history
chat_history = []

def add_to_chat(role, content):
    chat_history.append({'role': role, 'content': content})

def openai_completion(prompt, engine="gpt-35-turbo", temperature=0.0, max_tokens=1000):
    """
    General function to interact with OpenAI's completion endpoint.
    """
    client = AzureOpenAI(
    azure_endpoint = "https://pgjraistudio4875983533.openai.azure.com/", 
    api_key="68e132221fc9497894d46acf3bc25bf1",  
    api_version="2024-02-15-preview"
    )
    response = client.chat.completions.create(
        model="gpt-35-turbo", # model = "deployment_name"
        messages =prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )
    add_to_chat('assistant', response.choices[0].message.content)
    return response.choices[0].message.content

def process_query(message):
    prefix = "SQL_Query: "
    start_key = "SELECT"
    # for message in reversed(chat_history):
    if prefix in message:
        # Extract the portion of the message after the prefix
        start_index = message.find(prefix) + len(prefix)
        sql_query_portion = message[start_index:].strip()
        # Check if the extracted portion starts with "SELECT"
        if sql_query_portion.upper().startswith(start_key):
            # Find the end of the query, which should be a semicolon
            end_index = sql_query_portion.find(";")
            if end_index != -1:
                # Extract the SQL query, including the semicolon
                sql_query = sql_query_portion[:end_index + 1].strip()
                sql_query = sql_query.replace("\n", " ")
                return sql_query
    return None

def execute_sql_query(sql_query):
    """
    Connects to the database, executes the given SQL query, and returns the result.
    """

    try:
        with pyodbc.connect(
            f"DRIVER={DATABASE_CONFIG['driver']};"
            f"SERVER={DATABASE_CONFIG['server']};"
            f"DATABASE={DATABASE_CONFIG['database']};"
            f"UID={DATABASE_CONFIG['username']};"
            f"PWD={DATABASE_CONFIG['password']}"
        ) as conn:
            cursor = conn.cursor()
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            return rows
    except Exception as e:
        print(f"Database query failed: {e}")
        return None

def generate_sql_sys_msg():
    schema_description = """
        The 'dbo.vw_trips' table contains trip data with the following columns:
        TripID (unique identifier), PickupDateTime (pickup timestamp), 
        PickupLocation_Zone (pickup zone), PickLocation_Borough (pickup borough),
          DropoffDateTime (dropoff timestamp), DropOffLocation_Zone (dropoff zone), 
          DropOffLocation_Borough (dropoff borough), TravelTime (duration), PassengerCount (number of passengers), 
          FareAmount (fare), FeeAmount (additional fees), TotalAmount (total charged).
          Only aggregated data is shown to limit the data displayed in chat.Based on this schema, generate a SQL query to run on an Azure SQL db for the user prompt. make sure to end the query with ';' and it follows the syntax for t-sql. Please response in this format:
          If you have to use limit in the query, use top instead. You can use subquery when needed but donot use cte. SQL_Query: sql_query;
    """
    add_to_chat('system', schema_description)

def generate_sql_query(user_prompt):
    add_to_chat('user',user_prompt)

def generate_chat_response(response_description):
    chat_prompt_response = []
    chat_prompt = f"{response_description}. Please generate a concise and informative reply to the user's question based on this information"

    chat_prompt_response.append({'role': 'system', 'content': chat_prompt})
    # add_to_chat('system',chat_prompt)
    response = openai_completion(chat_prompt_response)
    return response

def get_intent_sys_message():
    intent_description = """
    I need your help in understanding the user intent when they ask for prompt. I have a sql server which I'm helping user with for reporting and an ML model that informs user
    how long it will take them to travel in New York city. Based on your reply I would understand if i need to invoke the ml model or my sql server.
    If a user asks how long it will take them to travel between 2 locations you need to create a reply 
    in this format:
    intent:'ml_model'
    if the user asks any query where we might involve the following schema
    The 'dbo.vw_trips' table contains trip data with the following columns:
        TripID (unique identifier), PickupDateTime (pickup timestamp), 
        PickupLocation_Zone (pickup zone), PickLocation_Borough (pickup borough),
          DropoffDateTime (dropoff timestamp), DropOffLocation_Zone (dropoff zone), 
          DropOffLocation_Borough (dropoff borough), TravelTime (duration), PassengerCount (number of passengers), 
          FareAmount (fare), FeeAmount (additional fees), TotalAmount (total charged).
    reply in this format:
    intent:'sql'. 
    Donot reply anything else except the format.
    """
    add_to_chat('system',intent_description)

def generate_payload(prompt):
    ai_system_msg = []
    data_payload = []
    est = pytz.timezone('America/New_York')
    now_est = datetime.now(est)
    # Extracting the required values
    month_num = now_est.month
    day_of_week = now_est.isoweekday()  # This will be the full name of the day
    hour_24 = now_est.hour
    minute = now_est.minute
    
    data_payload.extend([month_num,day_of_week, hour_24, minute])

    locationid_description = """
    I need your help in generating the json payload based on the user prompt. I need the following information:
    Pickup LocationID: if in the prompt user asks for pickup location 'Newark Airport', iD is 1. 
    If the pickup location is 'Brooklyn Heights', iD is 33.
    If the pickup location is 'Central Park', iD is 43.
    If the pickup location is 'China Town', iD is 45.
    If the pickup location is 'JFK Airport', iD is 132.
    If the pickup location is 'SoHo', iD is 211.
    Dropoff LocationID: if in the prompt user asks for dropoff location 'Newark Airport', iD is 1. 
    If the Dropoff location is 'Brooklyn Heights', iD is 33.
    If the Dropoff location is 'Central Park', iD is 43.
    If the Dropoff location is 'China Town', iD is 45.
    If the Dropoff location is 'JFK Airport', iD is 132.
    If the Dropoff location is 'SoHo', iD is 211.
    Calculate and fill the result in this format: [Pickup LocationID,Dropoff LocationID ]
    Don't reply anything else except the format. Make sure to only include the values in the list format and maintain the sort order.
    """
    ai_system_msg.append({'role': 'system', 'content': locationid_description})
    ai_system_msg.append({'role': 'user', 'content': prompt})

    # Asking on the location IDs
    response_locationid = openai_completion(ai_system_msg)

    locationids= json.loads(response_locationid)
    data_payload.extend(locationids) 

    # the Trip Distance
    dist = round(random.uniform(17,25),1)
    data_payload.extend([dist])

    return data_payload

def main(user_prompt):
    
    add_to_chat('user',user_prompt)

    get_intent_sys_message()
    intent_response = openai_completion(chat_history, temperature=0.0, max_tokens=1500)
    if "intent:'sql'" in intent_response:
        generate_sql_sys_msg()
        query_response = openai_completion(chat_history, temperature=0.0, max_tokens=1500)
        query = process_query(query_response)
        sql_result = execute_sql_query(query)
        formatted_result = ', '.join([str(row) for row in sql_result])
        response_description = f"The user query was: {user_prompt}. The result of the query is: {formatted_result}."
    elif "intent:'ml_model'" in intent_response:
        payload_data = generate_payload(user_prompt)
        INPUT_DATA = {
            "input_data": {
            "columns": [
                "PickupMonth",
                "PickupDayOfWeek",
                "PickupHour",
                "PickupMinute",
                "PickupLocationID",
                "DropoffLocationID",
                "TripDistance"
            ],
            "index": [0],
            "data": []
            }
        }
        payload = INPUT_DATA
        payload['input_data']['data'] =  [payload_data]
        json_payload = json.dumps(payload)
        result = call_ml_endpoint(json_payload)
        result_num = result.decode("utf-8")
        # formatted_result = 
        response_description = f"The user query was: {user_prompt}. The result of the query is: {result_num}."
        
    chat_response = generate_chat_response(response_description)

    print("Response: ", chat_response)

    
    for message in chat_history:
        print(f"{message['role'].title()}: {message['content']}")


if __name__ == "__main__":
    # user_prompt = "Which are the 3 most busy Borough?"
    user_prompt = "How long will it take to travel from Chinatown to JFK"
    #How many trips are there in the dataset?
    main(user_prompt)
