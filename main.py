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

airtable_api = os.environ.get("AIRTABLE_API")


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
    url = "https://api.airtable.com/v0/apppUZDPLKrTBobih/PDFs?view=Grid%20view&filterByFormula={first_message_sent} = ''&32q4321fields%5B%5D=phone"
    response = requests.request("GET", url, headers=headers, data=payload)
    print('---------')
    data = response.json()
    for record in data['records']:
      send_sms('+1' + str(record['fields']['phone']), "pdf_uploaded")

      # get pdf url and train chatgpt
      texts = train_pdf_file(data['records'][0]['fields']['pdf_url'])

      conversationId = ""
      parentMessageId = ""
      index = 0

      for index, text in enumerate(texts):
        init_message = "The following is the {} part of {} parts of a meal plan PDF.  Please respond with \"ok\": \n\n"
        print("INDEX IS " + str(index))
        init_message = init_message.format(index + 1, len(texts))
        message = init_message + text
        print(message)

        response_message, conversation_id, message_id = conversation(
          message, conversationId, parentMessageId)
        print(response_message)
        parentMessageId = message_id
        conversationId = conversation_id
        
        if index == len(texts) - 1:  # check if this is the last loop
            # add an additional loop with a different message
            message = "Those where the last part of the meal plan PDF. From now on, please answer all questions according to the information presented in the sum of all previous parts. If you are not certain about an answer, please abstain from making up any answer according to information outside of the meal plan provided and answer with something similar to \"I can't find any information related to that question in the meal plan provided\"."
            response_message, conversation_id, message_id = conversation(
              message, conversationId, parentMessageId)
            print(response_message)

      update_first_message_sent(record['id'], "PDFs")
      send_sms('+1' + str(record['fields']['phone']), "trained_finished")
      upsert_airtable_conversation(int(record['fields']['phone']), conversationId,
                                   parentMessageId)
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


def upsert_airtable_conversation(phone_number, conversationId,
                                 lastParentMessageId):
  url = "https://api.airtable.com/v0/apppUZDPLKrTBobih/conversations"

  payload = json.dumps({
    "performUpsert": {
      "fieldsToMergeOn": ["phone"]
    },
    "records": [{
      "fields": {
        "phone": phone_number,
        "conversationId": conversationId,
        "lastParentMessageId": lastParentMessageId
      }
    }]
  })
  headers = {
    'Authorization': 'Bearer ' + airtable_api,
    'Content-Type': 'application/json'
  }

  response = requests.request("PATCH", url, headers=headers, data=payload)

  print(response.text)


app = Flask(__name__, static_folder='static', static_url_path='')


# Main app
@app.route("/")
@web.authenticated
def index():
  return f"Hello {web.auth.name}"


@app.route('/new_phone', methods=['POST'])
def handle_webhook():
  # Get the data from the webhook request
  data = request.get_json()
  print(data)
  print(data["webhook"]["id"])

  #new phone record airtable webhook_id=ach2AK5mRBKuuBa39
  if data["webhook"]["id"] == "achstVAIE1UbWlCyR":
    get_number_from_db("onboard")
    print("Webhook received (onboard)")
    return 'Webhook received'

  #new phone record airtable webhook_id=achQedJW1CUFW0IYp
  if data["webhook"]["id"] == "achVOsJ8PVRaHcRwr":
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
    print(active_conversations["records"][0]["fields"]["conversationId"])
    conversationId = active_conversations["records"][0]["fields"][
      "conversationId"]
    parentMessageId = active_conversations["records"][0]["fields"][
      "lastParentMessageId"]

    response_message, conversation_id, message_id = conversation(
      body, conversationId, parentMessageId)
    print(response_message)
    parentMessageId = message_id
    conversationId = conversation_id

    send_sms(str(from_number), "message", response_message)
    upsert_airtable_conversation(int(from_number), conversationId,
                                 parentMessageId)

    # Add a message
    resp = MessagingResponse()
    resp.message(response_message)

  #return str(resp)
  print(request.get_json())

  return ("success")


web.run(app)
if __name__ == '__main__':
  app.run(debug=True)
