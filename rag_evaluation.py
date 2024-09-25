from couchbase.cluster import Cluster
from couchbase.auth import PasswordAuthenticator
from couchbase.options import ClusterOptions
from datetime import timedelta


from langchain_couchbase.vectorstores import CouchbaseVectorStore
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

import os
from dotenv import load_dotenv
from tqdm import tqdm
from datasets import Dataset
from create_dataset import example_questions, ground_truth_answers

from ragas.metrics import (
    answer_relevancy,
    faithfulness,
    context_recall,
    context_precision,
)
from ragas import evaluate


def parse_bool(value: str):
    """Parse boolean values from environment variables"""
    return value.lower() in ("yes", "true", "t", "1")


def connect_to_couchbase(connection_string, db_username, db_password):
    """Connect to Couchbase cluster"""

    auth = PasswordAuthenticator(db_username, db_password)
    options = ClusterOptions(auth)
    connect_string = connection_string
    cluster = Cluster(connect_string, options)

    # Wait until the cluster is ready for use.
    cluster.wait_until_ready(timedelta(seconds=5))

    return cluster


def get_vector_store(
    _cluster,
    db_bucket,
    db_scope,
    db_collection,
    _embedding,
    index_name,
) -> CouchbaseVectorStore:
    """Return the Couchbase vector store"""
    vector_store = CouchbaseVectorStore(
        cluster=_cluster,
        bucket_name=db_bucket,
        scope_name=db_scope,
        collection_name=db_collection,
        embedding=_embedding,
        index_name=index_name,
    )
    return vector_store


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


if __name__ == "__main__":
    # Load environment variables
    load_dotenv(".env")
    DB_CONN_STR = os.getenv("DB_CONN_STR")
    DB_USERNAME = os.getenv("DB_USERNAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_BUCKET = os.getenv("DB_BUCKET")
    DB_SCOPE = os.getenv("DB_SCOPE")
    DB_COLLECTION = os.getenv("DB_COLLECTION")
    INDEX_NAME = os.getenv("INDEX_NAME")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    # Setup Langsmith Client
    os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")

    cluster = connect_to_couchbase(DB_CONN_STR, DB_USERNAME, DB_PASSWORD)

    # Fetch ingested document store
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    # Get the vector store
    vector_store = get_vector_store(
        cluster,
        DB_BUCKET,
        DB_SCOPE,
        DB_COLLECTION,
        embeddings,
        INDEX_NAME,
    )

    # Fetch documents from the vector store
    retriever = vector_store.as_retriever()

    system_prompt = """You are a chatbot that can answer questions related to Couchbase. Remember that you can only reply to questions related to Couchbase or Couchbase SDKs and follow this strictly. If the user question is not related to couchbase, simply return "I am sorry, I am afraid I can't answer that". 
        If you cannot answer based on the context provided, respond with a generic answer.
        Answer the question as truthfully as possible using the context below:
        {context}"""

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )

    # Use OpenAI GPT-4o as the LLM for the RAG
    llm = ChatOpenAI(temperature=0, model="gpt-4o")

    # Create a chain to insert relevant documents into prompt to LLM
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    # Test against the Custom dataset
    data = {
        "question": example_questions,
        "ground_truth": ground_truth_answers,
        "answer": [],
        "retrieved_contexts": [],
    }

    for question in tqdm(data["question"]):
        response = rag_chain.invoke({"input": question})
        data["answer"].append(response["answer"])
        data["retrieved_contexts"].append(
            [doc.page_content for doc in response["context"]]
        )

    # Save the results
    dataset = Dataset.from_dict(data)
    dataset.to_csv("rag_results.csv")

    # If you want to load the dataset from the CSV file
    # dataset = Dataset.from_csv("rag_results.csv")
    # dataset.rename_column("context", "retrieved_contexts")

    result = evaluate(
        dataset,
        metrics=[
            context_precision,
            faithfulness,
            answer_relevancy,
            context_recall,
        ],
    )

    df = result.to_pandas()
    print(df.head())

    # Save evaluation results
    df.to_csv("evaluation_results.csv")
