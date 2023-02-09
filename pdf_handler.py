import requests, PyPDF2
from io import BytesIO
import json


def conversation(message, context="", lastPrompt=""):
  url = "https://nara-conversation-usc4.zeet-nara.zeet.app/conversation"
  
  payload_data = {
    "message": message
  }
  
  payload_data.update({k: v for k, v in zip(("context", "lastPrompt"), (context, lastPrompt)) if v})
  
  payload = json.dumps(payload_data)
  
  headers = {
    'Content-Type': 'application/json'
  }
  
  response = requests.request("POST", url, headers=headers, data=payload)

  json_response = response.json()
  response_message = json_response['response']
  context = json_response['context']
  last_prompt = json_response['lastPrompt']
  print(json_response)
  return response_message, context


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