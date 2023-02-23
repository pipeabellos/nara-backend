import requests
import os

# Your Twilio account information
account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
auth_token = os.environ.get("TWILIO_AUTH_TOKEN")

welcome_message = "Hello :) I'm Nara, your AI nutritional assistant.\n\nImagine you have a full-time healthy friend. This is a very smart friend that knows your dietary preferences and has delicioius recipe suggestions.\n\nBefore we start, I need to understand your preferences here: https://airtable.com/shrwrO2q0cepBaffV?hide_phone=true&prefill_phone="

thanks_for_uploading_message = "Thanks for uploading your PDF. I am training myself using the provided PDF. Please hand tight, I'll let you know as soon as I'm ready in a couple of minutes."

trained_finished_message = "I've finished training on the provided PDF. You can now take a picture or upload a screenshot of a menu and I'll recommend what you can order."

def send_sms(to_phone_number, step, response_message=""):

  if step == "welcome":
    message = str(welcome_message) + str(to_phone_number)
  elif step == "pdf_uploaded":
    message = thanks_for_uploading_message
  elif step == "trained_finished":
    message = trained_finished_message
  elif step == "message":
    message = response_message
  # The phone number to send the message from (this must be a Twilio phone number)
  from_phone_number = os.environ.get("TWILIO_SENDER_PHONE")

  # Send the SMS message
  response = requests.post(
      f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json',
      auth=(account_sid, auth_token),
      data={
          'To': to_phone_number,
          'From': from_phone_number,
          'Body': message
      }
  )
  
  # Print the response from the server
  print(response.content)

