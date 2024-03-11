# AI Hackathon - Advanced Query Chatbot

## Data Architecture

![alt text](/diagrams/PGJR%20-%20Architecture%20-%20Data%20Processing.png)

From Azure blob storage, historical data was loaded to Azure Data Explorer for discovery, analysis and processing. Using Data Factory, data was exported to Azure SQL and Azure ML Studio to support the LLM model provided to the user. The AutoML feature in Azure ML Studio to streamline the process of building and deploying a ML model for real-time use.

## Core Functionality

The chatbot boasts dual processing capabilities:
- **SQL Database Queries**: For general information requests, it dynamically generates SQL queries to retrieve data from an Azure SQL database, enabling users to interact with stored data using conversational language.
- **Machine Learning Model Invocation**: For specific inquiries about travel times between locations in NYC, it calls an external ML model endpoint, leveraging advanced analytics to provide precise travel insights.
- **Overcoming Limitations of Embeddings-Based Bots:**: Embeddings-based approaches, while powerful for capturing semantic meanings, often face challenges in handling specific, data-intensive queries or providing dynamic responses based on real-time data analysis.

## How It Works

Here's a step-by-step breakdown of the process:

1. **User Query Submission**: Users submit their queries through an interactive Streamlit web interface. The interface is designed to accept natural language inputs, making it accessible to users without technical expertise.

2. **Query Interpretation with OpenAI's GPT**: Upon receiving a query, the system leverages OpenAI's GPT to interpret the user's intent. This step involves analyzing the query's content to determine whether it seeks general information stored in the database or requires travel time estimates between specific NYC locations.

    - For general information requests, the AI generates a SQL query tailored to retrieve the relevant data from the Azure SQL database.
    
    **Example Prompts:**  'Which are the 3 most busy Borough?', 'How many trips are there in the dataset?'

    - For travel time inquiries, the AI identifies the request as requiring a response from the external machine learning model.
    
    **Example Prompts:**  'How long will it take to travel from Chinatown to JFK'

3. **Processing the Query**:
    - **SQL Database Queries**: If the AI determines the query pertains to general information, the generated SQL query is executed against the configured Azure SQL database. The database then returns the requested data, which is captured for response generation.
    - **Machine Learning Model Invocation**: If the query is identified as a travel time inquiry, the system invokes the specified machine learning model endpoint, passing the necessary parameters extracted from the query. The model processes the request and returns travel time estimates.

## LLM Application

![alt text](/diagrams/PGJR%20-%20Architecture%20-%20User%20Interface.png)


## Running Application - CLI

Install `requirements.txt` and initialize app in the terminal

``` bash
pip install -r requirements.txt

streamlit run app/Bot_StreamLit.py
```

## Running Application - Docker

Build docker image and run

``` bash
docker build --no-cache -t pgjr_ai_hackathon:v1 .

docker run --rm -p 8880:8501 pgjr_ai_hackathon:v1
```

## Running Streamlit
```
streamlit run bot_streamlit.py
```
