import os
import io
from dotenv import load_dotenv
import time
from datetime import datetime
from typing import Iterable

from openai import AzureOpenAI
from openai.types.beta.threads.message_content_image_file import MessageContentImageFile
from openai.types.beta.threads.message_content_text import MessageContentText
from openai.types.beta.threads.messages import MessageFile
from PIL import Image

load_dotenv()

# Load the environment variables
API_KEY = os.getenv("API_KEY")
API_ENDPOINT = os.getenv("API_ENDPOINT")
API_VERSION = os.getenv("API_VERSION")
API_DEPLOYMENT_NAME = os.getenv("API_DEPLOYMENT_NAME")

should_cleanup: bool = False
threads = {}
user_id = "pauldatta"

oai_client = AzureOpenAI(api_key=API_KEY, api_version=API_VERSION, azure_endpoint=API_ENDPOINT)

#australiaeast, eastus, eastus2, francecentral, norwayeast, swedencentral, uksouth
def create_assistant(client=oai_client, model = API_DEPLOYMENT_NAME, name="Math Assistant", instructions="You are an AI assistant that can write code to help answer math questions."):
  # Create an assistant
  assistant = client.beta.assistants.create(
      name=name,
      instructions=instructions,
      tools=[{"type": "code_interpreter"}],
      model=model
  )

  try:
    if threads.get(user_id, None) is None:
        thread = client.beta.threads.create()
        threads[user_id] = thread
    else:
        thread = threads[user_id]
  except:
      thread = client.beta.threads.create()

  return assistant, thread


def retrieve_assistant(assistant_id, client=oai_client):
  assistant = client.beta.assistants.retrieve(assistant_id)
  return assistant

def retrieve_thread(thread_id, client=oai_client):
  thread = client.beta.threads.retrieve(thread_id)
  return thread


def query_assistant(query, assistant, thread, client=oai_client):
  # Add a user question to the thread
  message = client.beta.threads.messages.create(
      thread_id=thread.id,
      role="user",
      content = query
  )

  run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant.id)
  run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
  status = run.status

  while status not in ["completed", "cancelled", "expired", "failed"]:
      time.sleep(5)
      run = client.beta.threads.runs.retrieve(thread_id=thread.id,run_id=run.id)
      status = run.status

  messages = client.beta.threads.messages.list(thread_id=thread.id)
  return messages

assistant, thread = create_assistant(oai_client)    

print(f'Assistant ID', assistant.id)
print(f'Thread ID', thread.id)


def process_assistants_api_response(messages, client=oai_client):
  files = []
  full_path = ""

  download_dir = os.path.join(os.getcwd(), "downloads")
  os.makedirs(download_dir, exist_ok=True)

  md = messages.model_dump()["data"]
  for j in range(len(md[0]["content"])):
    if md[0]["content"][j]['type'] == 'text':
        response = md[0]["content"][j]["text"]["value"]
        break
  
  for i in range(len(md)):
    msg_id = md[i]["id"]
    for j in range(len(md[i]["content"])):
      if md[i]["content"][j]["type"] == 'text':
          if md[i]["content"][j]["text"].get("annotations", None) is not None:
            for annotation in md[i]["content"][j]["text"]["annotations"]:
              if annotation.get("type", None) is not None:
                if annotation["type"] == "file_path":
                    file_data = client.files.content(annotation["file_path"]["file_id"])
                    data_bytes = file_data.read()
                    full_path = os.path.join(download_dir, os.path.basename(annotation["text"]))
                    with open(full_path, "wb") as file:
                        file.write(data_bytes)
                    response = response.replace(annotation["text"], full_path)
                    files.append({'type':'file', 'asset':full_path})
      elif md[i]["content"][j]["type"] == 'image_file':
        file_data = client.files.content(md[i]["content"][j]["image_file"]["file_id"])
        data_bytes = file_data.read()
        full_path = os.path.join(download_dir, os.path.basename(f'{md[i]["content"][j]["image_file"]["file_id"]}.jpg'))
        with open(full_path, "wb") as file:
            file.write(data_bytes)
        files.append({'type':'assistant_image', 'asset':full_path})

    return response, files

def ask_assistant(query, assistant, thread, client = oai_client):
  messages = query_assistant(query, assistant, thread, client = oai_client)
  response, files = process_assistants_api_response(messages, client = oai_client)
  print(f"Assistants API generated {len(files)} files for this answer.\n")
  print(f'Assistant Response', response)
  return response, files


query = """x=r*cos(u)sin(v), y=r*sin(u)sin(v), r=2+sin(7*u+5*v) for 0<u<2π and 0<v<π.
Create a graph of the equation z=r*cos(v)."""
response, files = ask_assistant(query, assistant, thread, client = oai_client)


# Assistant ID asst_5CoR3qyYQ7304RbmXyof5oFw
# Thread ID thread_OvvkEfqAn5W9F5hmMxVZDy0Z
# Assistants API generated 1 files for this answer.

# Assistant Response Here's the 3D plot of the equation z = r*cos(v), where r, x, and y were calculated according to your provided formulas. The plot forms a complex and interesting surface shape in 3D space.