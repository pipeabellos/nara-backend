import requests
import os

# Your Twilio account information
account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
auth_token = os.environ.get("TWILIO_AUTH_TOKEN")

welcome_message = "👋 Hello! I'm Nara, your AI nutritional assistant.\n\n🍎🥦 Imagine having a full-time healthy friend - someone smart who knows your dietary preferences and has delicious recipe suggestions for you.\n\n👉 But before we get started, I need to understand your preferences. Please take a moment to fill out this short survey: https://airtable.com/shrwrO2q0cepBaffV?hide_phone=true&prefill_phone="

thanks_for_uploading_message = "👋 Thanks for completing the survey! We're setting up your account and will notify you by 📱 SMS when it's ready.\n\nIn the meantime, feel free to 💭 think about any questions you have. I'm excited to 🤝 work with you to help you achieve your health goals!"

trained_finished_message = "🎉 Your Nara account is now ready. As your personal AI nutritional assistant, I'm excited to help you achieve your health goals!\n\n🍽️ If you're not sure where to start, feel free to ask me for recipe suggestions. For example, you could ask, \"What can I eat for lunch today?\" and I'll provide you with a list of delicious and healthy options based on your dietary preferences.\n\n💬 I'm here to support you every step of the way, so don't hesitate to ask me any questions or share your concerns. Let's work together to make healthy eating easy and enjoyable!"

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
  messaging_service_sid = os.environ.get("MESSAGING_SERVICE_SID")

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

  response.raise_for_status()  # raise an exception if the request fails
  
  # Print the response from the server
  print(response.content)

