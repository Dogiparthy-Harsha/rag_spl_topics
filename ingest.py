import boto3
import io
import os
from langchain_aws import BedrockEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

# 1. Configuration
# TODO: Update this to match your actual bucket name!
BUCKET_NAME = "rag-assignment-harsha-2025" 
BEDROCK_MODEL_ID = "amazon.titan-embed-text-v1"

# 2. Initialize AWS & PII Engines
s3 = boto3.client('s3', region_name="us-east-1")
embeddings = BedrockEmbeddings(model_id=BEDROCK_MODEL_ID, region_name="us-east-1")
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

def scrub_pii(text):
    """
    Detects emails/phones and replaces them with <REDACTED>
    """
    # Analyze for email and phone numbers
    results = analyzer.analyze(text=text, entities=["EMAIL_ADDRESS", "PHONE_NUMBER"], language='en')

    # Redact identified entities
    anonymized_result = anonymizer.anonymize(
        text=text,
        analyzer_results=results,
        operators={"DEFAULT": OperatorConfig("replace", {"new_value": "<REDACTED>"})}
    )
    return anonymized_result.text

def process_and_index():
    print(f"📥 Downloading from S3 bucket: {BUCKET_NAME}...")

    try:
        response = s3.list_objects_v2(Bucket=BUCKET_NAME)
        if 'Contents' not in response:
            print("⚠️ Bucket is empty or does not exist.")
            return
    except Exception as e:
        print(f"❌ Error accessing bucket: {e}")
        return

    documents = []

    # Loop through S3 objects
    for obj in response['Contents']:
        key = obj['Key']
        print(f"   Processing: {key}")

        # Download file content into memory
        file_stream = io.BytesIO()
        s3.download_fileobj(BUCKET_NAME, key, file_stream)
        raw_text = file_stream.getvalue().decode('utf-8')

        # Scrub PII
        clean_text = scrub_pii(raw_text)

        # Determine Access Level based on filename (The "Role" Logic)
        access = "public" # default
        if "hr" in key: 
            access = "hr"
        elif "finance" in key: 
            access = "finance"
            
        # Create Document object with metadata
        doc = Document(
            page_content=clean_text, 
            metadata={"access": access, "source": key}
        )
        documents.append(doc)

    # Indexing into ChromaDB
    print("🧠 Generating Embeddings with Amazon Titan...")
    if documents:
        vector_db = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory="./chroma_db"
        )
        print("✅ Ingestion Complete. Vector DB saved locally in './chroma_db'.")
    else:
        print("⚠️ No documents to index.")

if __name__ == "__main__":
    process_and_index()