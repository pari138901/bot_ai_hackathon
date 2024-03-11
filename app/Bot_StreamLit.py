from openai import AzureOpenAI
import pyodbc
import streamlit as st
from streamlit_chat import message
from config import DATABASE_CONFIG, a_endpoint, a_key, a_version
from datetime import datetime
from ml_model import call_ml_endpoint
import json
import pytz
import random

# Initialize session state keys if they don't exist
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# Sidebar for clearing conversation
st.sidebar.title("Sidebar")
clear_button = st.sidebar.button("Clear Conversation")

if clear_button:
    # st.session_state['messages'] = []
    st.session_state['messages'] =[]
    st.session_state['generated'] = []
    st.session_state['past'] = []

def add_to_chat(role, content):
    st.session_state['messages'].append({'role': role, 'content': content})

def openai_completion(prompt, engine="gpt-35-turbo", temperature=0.0, max_tokens=1000):
    """
    General function to interact with OpenAI's completion endpoint.
    """
    client = AzureOpenAI(
    azure_endpoint = a_endpoint, 
    api_key=a_key,  
    api_version=a_version
    )
    response = client.chat.completions.create(
        model=engine, # model = "deployment_name"
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
    # for message in reversed(st.session_state['messages']):
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
          Only aggregated data is shown to limit the data displayed in chat. Based on this schema, generate a SQL query to run on an Azure SQL db for the user prompt. 
          If you have to use limit in the query, use top instead. You can use subquery when needed but donot use cte. 
          Make sure to end the query with ';' and it follows the syntax for t-sql. Please response in this format: SQL_Query: sql_query;
    """
    add_to_chat('system', schema_description)

def generate_sql_query(user_input):
    add_to_chat('user',user_input)

def generate_chat_response(sql_description):
    chat_prompt_response = []
    chat_prompt = f"{sql_description}. Please generate a concise and informative reply to the user's question based on this information"

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
    Donot add anything else except the format.
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

def main(user_input):
     # Add user input to session state for display
    st.session_state['past'].append(user_input)

    # Adding user prompt to the list
    add_to_chat('user',user_input)
    get_intent_sys_message()
    intent_response = openai_completion(st.session_state['messages'], temperature=0.0, max_tokens=1500)
    if "intent:'sql'" in intent_response:
        generate_sql_sys_msg()
        query_response = openai_completion(st.session_state['messages'], temperature=0.0, max_tokens=1500)
        st.write(query_response)
        query = process_query(query_response)
        sql_result = execute_sql_query(query)
        formatted_result = ', '.join([str(row) for row in sql_result])
        response_description = f"The user query was: {user_input}. The result of the query is: {formatted_result}."
    elif "intent:'ml_model'" in intent_response:
        payload_data = generate_payload(user_input)
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
        response_description = f"The user query was: {user_input}. The result of the query is: {result_num}."
    
    chat_response = generate_chat_response(response_description)
    st.session_state['generated'].append(chat_response)
    
    # query_response = openai_completion(st.session_state['messages'], temperature=0.0, max_tokens=1500)
    
    # print("Response: ", chat_response)

    # for message in st.session_state['messages']:
    #     print(f"{message['role'].title()}: {message['content']}")

# Streamlit UI Components
with st.container():
    user_input = st.text_area("Your Query:", "", help="Type your query here and press enter.")
    submit_button = st.button("Submit")

if submit_button and user_input:
    main(user_input)

# Displaying the chat history
with st.container():
    # Determine the shorter length to avoid IndexError
    num_messages = min(len(st.session_state['past']), len(st.session_state['generated']))
    
    for i in range(num_messages):
        user_input = st.session_state['past'][i]
        generated_response = st.session_state['generated'][i]

        st.text_area(f"User: {i+1}", value=user_input, disabled=True, key=f"user_{i}")
        st.text_area(f"Assistant: {i+1}", value=generated_response, disabled=True, key=f"assistant_{i}")
