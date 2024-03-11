# AI Hackathon - Advanced Query Chatbot

## Data Architecture

![alt text](/diagrams/PGJR%20-%20Architecture%20-%20Data%20Processing.png)

From Azure blob storage, historical data was loaded to Azure Data Explorer for discovery, analysis and processing. Using Data Factory, data was exported to Azure SQL and Azure ML Studio to support the LLM model provided to the user. The AutoML feature in Azure ML Studio to streamline the process of building and deploying a ML model for real-time use.

## Core Functionality

The chatbot boasts dual processing capabilities:
- **SQL Database Queries**: For general information requests, it dynamically generates SQL queries to retrieve data from an Azure SQL database, enabling users to interact with stored data using conversational language.
- **Machine Learning Model Invocation**: For specific inquiries about travel times between locations in NYC, it calls an external ML model endpoint, leveraging advanced analytics to provide precise travel insights.

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

### Overcoming Limitations of Embeddings-Based Bots

Embeddings-based approaches, while powerful for capturing semantic meanings, often face challenges in handling specific, data-intensive queries or providing dynamic responses based on real-time data analysis. This project overcomes such limitations by:

- **Enhancing Contextual Understanding**: Leveraging advanced NLP capabilities to interpret the user's intent more accurately and decide the most effective processing path - be it a database query or a machine learning model invocation.
- **Dynamic Data Handling**: Directly querying a SQL database allows for real-time data retrieval, ensuring responses are based on the latest information. This contrasts with embedding-based bots that might rely on static data or predefined responses.
- **Specialized Responses through ML**: For queries that demand more than factual data retrieval—like estimating travel times—this chatbot smartly redirects to an ML model, harnessing its predictive power for responses that require computation or analysis beyond straightforward lookup.


## Running Streamlit

Run 'streamlit run Bot_StreamLit.py'
