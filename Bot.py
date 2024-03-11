from openai import AzureOpenAI
import os
import pyodbc
import streamlit as st
from streamlit_chat import message

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

def generate_sys_msg():
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

def generate_chat_response(sql_description):
    chat_prompt_response = []
    chat_prompt = f"{sql_description}. Please generate a concise and informative reply to the user's question based on this information"

    chat_prompt_response.append({'role': 'system', 'content': chat_prompt})
    # add_to_chat('system',chat_prompt)
    response = openai_completion(chat_prompt_response)
    return response

def main(user_prompt):
    
    add_to_chat('user',user_prompt)

    query_response = openai_completion(chat_history, temperature=0.0, max_tokens=1500)

    query = process_query(query_response)

    sql_result = execute_sql_query(query)
    
    formatted_result = ', '.join([str(row) for row in sql_result])
    sql_description = f"The user query was: {user_prompt}. The result of the query is: {formatted_result}."
    
    chat_response = generate_chat_response(sql_description)

    print("Response: ", chat_response)

    for message in chat_history:
        print(f"{message['role'].title()}: {message['content']}")

# Example usage
# if __name__ == "__main__":
generate_sys_msg()
user_prompt = "Which are the 3 most busy Borough?"
#How many trips are there in the dataset?

main(user_prompt)
