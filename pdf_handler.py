import requests, PyPDF2
from io import BytesIO
import json


def conversation(message, phone_number, context="", lastPrompt=""):
  url = "https://nara-conversation-usc4.zeet-nara.zeet.app/conversation"
  
  payload_data = {
    "prompt": message,
    "phone_number": phone_number
  }
  print(payload_data)
  payload_data.update({k: v for k, v in zip(("context", "lastPrompt"), (context, lastPrompt)) if v})
  
  payload = json.dumps(payload_data)
  print(payload)
  headers = {
    'Content-Type': 'application/json'
  }
  
  response = requests.request("POST", url, headers=headers, data=payload)
  print(response.text)
  
  json_response = response.json()
  response_message = json_response['response']
  context = json_response['context']
  last_prompt = json_response['lastPrompt']
  dialogue = json_response['dialogue']
  print(json_response)
  return response_message, context, last_prompt, dialogue


def train_pdf_file(url):
  response = requests.get(url)
  my_raw_data = response.content
  
  with BytesIO(my_raw_data) as data:
      read_pdf = PyPDF2.PdfReader(data)

      chunks = []
      for page in range(len(read_pdf.pages)):
          #print(read_pdf.pages[page].extract_text())
        
          chunks.append(read_pdf.pages[page].extract_text())
      return(chunks)
  
          #text = read_pdf.pages[page].extract_text()
          #chunk_size = 1000
          
          #chunks = textwrap.wrap(text, chunk_size)
          
          #for chunk in chunks:
          #  print(chunk)