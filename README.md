# AI Hackathon - Bot

## Data Architecture

![alt text](/diagrams/PGJR%20-%20Architecture%20-%20Data%20Processing.png)

From Azure blob storage, historical data was loaded to Azure Data Explorer for discovery, analysis and processing. Using Data Factory, data was exported to Azure SQL and Azure ML Studio to support the LLM model provided to the user. The AutoML feature in Azure ML Studio to streamline the process of building and deploying a ML model for real-time use.

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