import streamlit as st
from langchain_aws import ChatBedrock, BedrockEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_classic.chains import RetrievalQA

# 1. Setup Bedrock & Chroma
# We use the specific ID for "Claude 3 Sonnet v1 (Legacy)"
llm = ChatBedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    model_kwargs={"temperature": 0.0},
    region_name="us-east-1"
)

embeddings = BedrockEmbeddings(
    model_id="amazon.titan-embed-text-v1",
    region_name="us-east-1"
)

# Load the DB we created in ingest.py
db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

st.set_page_config(page_title="Goliath National Bank", page_icon="🏦")
st.title("🏦 Goliath National Bank - Secure AI")

# 2. Login Simulation (Sidebar)
st.sidebar.header("🔐 Security Clearance")
role = st.sidebar.selectbox("Select Role", ["Intern", "HR Manager", "CFO"])

# 3. Access Control Logic (The "Zero Trust" Filter)
# This dictates exactly which documents the AI is allowed to read.
if role == "Intern":
    # Interns only see public data
    filter_rules = {"access": "public"}
    
elif role == "HR Manager":
    # HR sees Public + HR (but NOT Finance)
    filter_rules = {
        "access": {
            "$in": ["public", "hr"]
        }
    }
    
elif role == "CFO":
    # CFO sees everything
    filter_rules = {
        "access": {
            "$in": ["public", "hr", "finance"]
        }
    }

st.sidebar.write(f"Active Filter: `{filter_rules}`")

# 4. Chat Interface
query = st.chat_input("Ask a question...")

if query:
    st.chat_message("user").write(query)
    
    # Create the Retriever with the specific security filter
    retriever = db.as_retriever(
        search_kwargs={
            "filter": filter_rules, # <--- THIS IS THE KEY SECURITY FEATURE
            "k": 3
        }
    )
    
    # Run the Chain
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    
    # Get response
    try:
        response = qa.run(query)
        st.chat_message("assistant").write(response)
        
        # Debug: Show source docs to prove to your professor that security worked
        with st.expander("🕵️ Security Audit (Source Documents)"):
            # docs = retriever.get_relevant_documents(query)
            docs = retriever.invoke(query)
            for d in docs:
                st.code(f"Source: {d.metadata['source']}\nAccess Level: {d.metadata['access']}\nContent: {d.page_content[:100]}...")
                
    except Exception as e:
        st.error(f"Error communicating with Bedrock: {e}")