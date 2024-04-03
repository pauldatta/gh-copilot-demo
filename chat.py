import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import requests

load_dotenv()

# Load the environment variables
API_KEY = os.getenv("API_KEY")
API_ENDPOINT = os.getenv("API_ENDPOINT")
API_VERSION = os.getenv("API_VERSION")
API_DEPLOYMENT_NAME = os.getenv("API_DEPLOYMENT_NAME")

oai_client = AzureOpenAI(api_key=API_KEY, api_version=API_VERSION, azure_endpoint=API_ENDPOINT)


def chat_with_openai(prompt):
  response = oai_client.chat.completions.create(
    model=API_DEPLOYMENT_NAME, # model = "deployment_name".
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
  )
  return response.choices[0].message.content 

def main():
  while True:
    prompt = input("You: ")
    if prompt == '\\q':
        break
    response = chat_with_openai(prompt)
    print(f"AI: {response}")

if __name__ == "__main__":
  main()