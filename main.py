from twilio.twiml.messaging_response import MessagingResponse
import requests
import json
import os, shutil
import stripe
from flask import Flask, render_template, render_template_string, flash, redirect, url_for, request, jsonify
from flask.helpers import send_from_directory
from werkzeug.utils import secure_filename
from replit import db, web
from functools import wraps
from sms_handler import send_sms
from pdf_handler import train_pdf_file, conversation
from supabase_handler import new_file
from nara_endpoints import train, build_prompt
import dotenv

dotenv.load_dotenv()

airtable_api = str(os.environ.get("AIRTABLE_API"))
supabase_anon = str(os.environ.get("SUPABASE_ANON"))


def get_number_from_db(step, from_number=''):
  payload = {}
  headers = {'Authorization': 'Bearer ' + airtable_api}

  if step == "onboard":
    url = "https://api.airtable.com/v0/apppUZDPLKrTBobih/Users?view=Grid%20view&filterByFormula={first_message_sent} = ''&32q4321fields%5B%5D=phone"

    response = requests.request("GET", url, headers=headers, data=payload)
    print('---------')
    data = response.json()
    for record in data['records']:
      update_first_message_sent(record['id'], "Users")
      send_sms('+1' + str(record['fields']['phone']), "welcome")
      print(record)
    print('---------')

  elif step == "pdf_uploaded":
    url = "https://api.airtable.com/v0/apppUZDPLKrTBobih/PDFs?view=Grid%20view&filterByFormula=AND({first_message_sent} = '',{meal%20plan%20PDF} != '')&32q4321fields%5B%5D=phone"
    response = requests.request("GET", url, headers=headers, data=payload)
    print('---------')
    data = response.json()
    for record in data['records']:
      send_sms('+1' + str(record['fields']['phone']), "pdf_uploaded")
      
      # create avatar
      XAVATARPATH = new_file(record['fields']['phone'], data['records'][0]['fields']['pdf_url'])
      # train avatar
      train(XAVATARPATH)

      # update airtable and send sms
      update_first_message_sent(record['id'], "PDFs")
      send_sms('+1' + str(record['fields']['phone']), "trained_finished")
      upsert_airtable_conversation(int(record['fields']['phone']), context="NA",
                                   lastPrompt="NA", dialogue="")
      print(record)
    print('---------')

  elif step == "conversation":
    url = "https://api.airtable.com/v0/apppUZDPLKrTBobih/conversations?view=Grid%20view&filterByFormula={phone}=" + str(from_number)
    response = requests.request("GET", url, headers=headers, data=payload)
    print('---------')
    data = response.json()
    print(data)
    return (data)


def update_first_message_sent(record_id, table_name):
  url = "https://api.airtable.com/v0/apppUZDPLKrTBobih/" + table_name

  payload = json.dumps(
    {"records": [{
      "id": record_id,
      "fields": {
        "first_message_sent": True
      }
    }]})
  headers = {
    'Authorization': 'Bearer ' + airtable_api,
    'Content-Type': 'application/json'
  }

  response = requests.request("PATCH", url, headers=headers, data=payload)

  print(response.text)


def upsert_airtable_conversation(phone_number, context,
                                 lastPrompt, dialogue):
  url = "https://api.airtable.com/v0/apppUZDPLKrTBobih/conversations"

  payload = json.dumps({
    "performUpsert": {
      "fieldsToMergeOn": ["phone"]
    },
    "records": [{
      "fields": {
        "phone": phone_number,
        "context": context,
        "lastPrompt": lastPrompt,
        "dialogue": dialogue
      }
    }]
  })
  headers = {
    'Authorization': 'Bearer ' + airtable_api,
    'Content-Type': 'application/json'
  }

  response = requests.request("PATCH", url, headers=headers, data=payload)

  print(response.text)

def add_cronjob(webhook_id):
    from crontab import CronTab
    import requests

    # Initialize cron
    cron = CronTab(user='root')

    # Define the curl command
    curl_command = 'curl -X POST "https://api.airtable.com/v0/bases/apppUZDPLKrTBobih/webhooks/' + webhook_id + '/refresh" -H "Authorization: Bearer ' + airtable_api

    # Add the cronjob
    job = cron.new(command=curl_command)

    # Set the time to run the cronjob (midnight every day)
    job.minute.every(0)
    job.hour.every(0)

    # Enable the cronjob
    job.enable()

    # Write the cronjob to the crontab
    cron.write()

def get_xavatarpath(phone_number):

  print(supabase_anon)
  url = "https://qmnzwxeqrxmuvutgedtr.supabase.co/rest/v1/hello_user_avatars?select=avatar_id,hello_avatars(url_path)&user_phone=eq." + str(phone_number) + "&order=created_at.desc&limit=1"

  payload={}
  headers = {
    'apikey': supabase_anon,
    'Authorization': 'Bearer ' + supabase_anon
  }

  response = requests.request("GET", url, headers=headers, data=payload)

  print(response.text)
  
  data = json.loads(response.text)

  return data[0]['hello_avatars']['url_path']


app = Flask(__name__, static_folder='static', static_url_path='')

# Main app
@app.route("/")
@web.authenticated
def index():
  return f"Hello {web.auth.name}"


@app.route('/new_phone', methods=['POST'])
def handle_webhook():
  # Get the data from the webhook request
  print("received webhook")
  data = request.get_json()
  print(data)
  print(data["webhook"]["id"])

  #new phone record airtable webhook_id=achWmGJCahNciLDOH
  if data["webhook"]["id"] == "achWmGJCahNciLDOH":
    get_number_from_db("onboard")
    print("Webhook received (onboard)")
    return 'Webhook received'

  #new phone record airtable webhook_id=achvlHuUTsPpYp4lo
  if data["webhook"]["id"] == "achvlHuUTsPpYp4lo":
    get_number_from_db("pdf_uploaded")
    print("Webhook received (pdf_uploaded)")
    return 'Webhook received'

  print(data["webhook"]["id"])
  print('Not valid webhook')
  return 'Not valid webhook'


@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
  # Start our TwiML response
  from_number = request.values.get('From', None)
  body = request.values.get('Body', None)

  print(from_number)
  active_conversations = get_number_from_db("conversation", from_number)
  #Check if from_number exists in
  if active_conversations["records"] != []:
    print("From number exists in conversation")
    print(active_conversations["records"][0]["fields"]["context"])
    context = active_conversations["records"][0]["fields"][
      "context"]
    lastPrompt = active_conversations["records"][0]["fields"][
      "lastPrompt"]

    response_message, context, lastPrompt, dialogue = conversation(
      body, int(from_number), context, lastPrompt)
    print(response_message)

    send_sms(str(from_number), "message", response_message)
    upsert_airtable_conversation(int(from_number), context,
                                 lastPrompt, dialogue)

    # Add a message
    resp = MessagingResponse()
    resp.message(response_message)

  #return str(resp)
  print(request.get_json())

  return ("success")

@app.route("/prompt", methods=['POST'])
def get_prompt():
  data = request.get_json()
  question = data["question"]
  phone_number = data["phone"]

  XAVATARPATH = get_xavatarpath(phone_number)

  embedding = build_prompt(XAVATARPATH, question)
  
  return embedding

web.run(app)
if __name__ == '__main__':
  app.run(debug=True)
  add_cronjob("achstVAIE1UbWlCyR")
  add_cronjob("achVOsJ8PVRaHcRwr")