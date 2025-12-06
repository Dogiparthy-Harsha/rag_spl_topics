import boto3
import os

def setup_data():
    # 1. Configuration
    # TODO: Change this to a unique name (e.g., rag-assignment-harsha-2025)
    bucket_name = "rag-assignment-harsha-2025" 
    region = "us-east-1"
    
    s3 = boto3.client('s3', region_name=region)

    # 2. Create Bucket
    try:
        if region == "us-east-1":
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        print(f"✅ Bucket created: {bucket_name}")
    except Exception as e:
        print(f"⚠️  Bucket might already exist or error occurred: {e}")

    # 3. Upload Files
    files = [
        "policy_public.txt", 
        "hr_sensitive_salaries.txt", 
        "finance_secret_merger.txt"
    ]

    for filename in files:
        if os.path.exists(filename):
            s3.upload_file(filename, bucket_name, filename)
            print(f"⬆️  Uploaded {filename}")
        else:
            print(f"❌ File not found: {filename} (Did you create it?)")

if __name__ == "__main__":
    setup_data()