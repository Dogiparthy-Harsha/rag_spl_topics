import sys
import os

print(f"Python executable: {sys.executable}")
print(f"Path: {sys.path}")

try:
    import langchain
    print(f"Langchain file: {langchain.__file__}")
    print(f"Langchain version: {langchain.__version__}")
    print(f"Langchain dir: {dir(langchain)}")
except ImportError:
    print("Cannot import langchain")

try:
    import langchain.chains
    print("Imported langchain.chains")
except ImportError as e:
    print(f"Cannot import langchain.chains: {e}")

try:
    from langchain_community import chains
    print("Imported langchain_community.chains")
except ImportError as e:
    print(f"Cannot import langchain_community.chains: {e}")
