# Evaluate RAG using Ragas

The code examples to evaluate RAG responses using [Ragas](https://ragas.io/) using the LLM (OpenAI) as the judge approach. The RAG pipelines is based off the RAG application in this [repo](https://github.com/couchbase-examples/qa-bot-demo).

> Note that you need Couchbase Server 7.6 or higher for Vector Search.

A detailed tutorial for this demo can be found on the [Developer Portal](https://developer.couchbase.com/tutorial-evaluate-rag-responses-using-ragas)

## How to Run

- Install the dependencies

  `pip install -r requirements.txt`

- Set the environment variables
  Copy the .env.example file and rename it to .env and replace the placeholders with the actual values for your environment.

  ```
  OPENAI_API_KEY=<open-ai-api-key>
  DB_CONN_STR=<connection string for couchbase cluster>
  DB_USERNAME=<your database user>
  DB_PASSWORD=<your database password>
  DB_BUCKET=<your database bucket>
  DB_SCOPE=<your database scope>
  DB_COLLECTION=<your database collection>
  INDEX_NAME=<vector search index name>
  EMBEDDING_MODEL=text-embedding-3-small
  LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
  LANGCHAIN_API_KEY=<your langsmith api key>
  ```

- Run the evaluation script
  `python rag_evaluation.py`

Note: For the RAG pipeline to work, you would need to ingest some documents to answer the questions related to Couchbase. You could do that based on the ingestion script in this [repo](https://github.com/couchbase-examples/qa-bot-demo).

## Adding more Test Data

The test data can be updated by adding more question & answer pairs to the list in the `create_dataset.py` file.
