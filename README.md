# AI Hackathon - Advanced Query Chatbot

## Data Architecture

![alt text](/diagrams/PGJR%20-%20Architecture%20-%20Data%20Processing.png)

From Azure blob storage, historical data was loaded to Azure Data Explorer for discovery, analysis and processing. Using Data Factory, data was exported to Azure SQL and Azure ML Studio to support the LLM model provided to the user. The AutoML feature in Azure ML Studio to streamline the process of building and deploying a ML model for real-time use.
This project presents an innovative chatbot that intelligently routes user queries to either a SQL database or a machine learning (ML) model based on the nature of the inquiry. Utilizing OpenAI's GPT for natural language understanding, it discerns whether a query pertains to retrieving general data or requires insights on travel times between places in NYC, directing queries to the appropriate processing engine.

## Core Functionality

The chatbot boasts dual processing capabilities:
- **SQL Database Queries**: For general information requests, it dynamically generates SQL queries to retrieve data from an Azure SQL database, enabling users to interact with stored data using conversational language.
- **Machine Learning Model Invocation**: For specific inquiries about travel times between locations in NYC, it calls an external ML model endpoint, leveraging advanced analytics to provide precise travel insights.

Both functionalities are seamlessly integrated into an interactive Streamlit web application, offering users a versatile and intuitive platform for data exploration.

## How It Works

The chatbot intelligently routes user queries to the most appropriate processing engine—either a SQL database for general queries or a machine learning model for specific inquiries about travel times between locations in NYC. Here's a step-by-step breakdown of the process:

1. **User Query Submission**: Users submit their queries through an interactive Streamlit web interface. The interface is designed to accept natural language inputs, making it accessible to users without technical expertise.

2. **Query Interpretation with OpenAI's GPT**: Upon receiving a query, the system leverages OpenAI's GPT to interpret the user's intent. This step involves analyzing the query's content to determine whether it seeks general information stored in the database or requires travel time estimates between specific NYC locations.

    - For general information requests, the AI generates a SQL query tailored to retrieve the relevant data from the Azure SQL database.
    Example Prompts:  'Which are the 3 most busy Borough?', 'How many trips are there in the dataset?'
    - For travel time inquiries, the AI identifies the request as requiring a response from the external machine learning model.
    Example Prompts: 'How long will it take to travel from Chinatown to JFK'

3. **Processing the Query**:
    - **SQL Database Queries**: If the AI determines the query pertains to general information, the generated SQL query is executed against the configured Azure SQL database. The database then returns the requested data, which is captured for response generation.
    - **Machine Learning Model Invocation**: If the query is identified as a travel time inquiry, the system invokes the specified machine learning model endpoint, passing the necessary parameters extracted from the query. The model processes the request and returns travel time estimates.

4. **Generating a Conversational Response**: With the processed data in hand—whether from the SQL database or the ML model—the system uses OpenAI's GPT again to generate a conversational response. This response is designed to present the information or insights in an easily understandable and engaging manner, directly addressing the user's initial query.

This dual-functionality framework ensures that users can access a wide range of information and insights through a single, conversational interface, making data exploration both intuitive and efficient.


## LLM Application

![alt text](/diagrams/PGJR%20-%20Architecture%20-%20User%20Interface.png)

## Running Streamlit

Run 'streamlit run Bot_StreamLit.py'
