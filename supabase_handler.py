import requests
import os
import uuid
import time
import dotenv
from nara_endpoints import train

dotenv.load_dotenv()

supabase_anon = os.environ.get("SUPABASE_ANON")

headers = {
  "apikey": str(supabase_anon),
  "Authorization": "Bearer " + str(supabase_anon),
  "Content-Type": "application/json",
  "Prefer": "return=representation"
}
base_url = "https://qmnzwxeqrxmuvutgedtr.supabase.co/rest/v1/"

def create_avatar():
  url = base_url + "hello_avatars"

  payload = {
    "url_path": create_random_string()
  }

  response = requests.post(url, json=payload, headers=headers)

  print(response.json()[0]['id'])
  return response.json()[0]['id'], response.json()[0]['url_path']

def create_files(avatar_id,file_url):
  url = base_url + "hello_files"

  payload = {
    "avatar_id": avatar_id,
    "file_url": file_url,
    "file_type": "TRAINING"
  }
  
  response = requests.post(url, json=payload, headers=headers)

def create_user_avatars(avatar_id,user_phone):
  url = base_url + "hello_user_avatars"

  payload = {
    "avatar_id": avatar_id,
    "user_phone": user_phone
  }
  
  response = requests.post(url, json=payload, headers=headers)

#create random string in format of 0e54d453-5cdf-4ed2-acbb-c2229c9580dc1673467099634
def create_random_string():
    return str(uuid.uuid4()) + str(int(time.time()))

def new_file(user_phone,file_url):
  avatar_id, url_path = create_avatar()
  create_files(avatar_id,file_url)
  create_user_avatars(avatar_id,user_phone)

  return url_path