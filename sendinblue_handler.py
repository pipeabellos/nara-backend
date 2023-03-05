from __future__ import print_function
import time
import os
import dotenv
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from pprint import pprint

dotenv.load_dotenv()

sendinblue_api = str(os.environ.get("SENDINBLUE_API"))

def create_contact(email, phone, first_name, last_name, list_id=2):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = sendinblue_api

    api_instance = sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(configuration))
    create_contact = sib_api_v3_sdk.CreateContact(email=email, list_ids=[list_id], update_enabled=True, attributes={"FIRSTNAME":first_name, "LASTNAME":last_name, "SMS": phone})

    try:
        api_response = api_instance.create_contact(create_contact)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ContactsApi->create_contact: %s\n" % e)

def send_transactional_email(email, template_id):
    # Configure API key authorization: api-key
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = sendinblue_api

    # Create an instance of the API class
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    # Set up the email parameters
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=[sib_api_v3_sdk.SendSmtpEmailTo(email=email)], template_id=template_id)

    try:
        # Send the email
        api_response = api_instance.send_transac_email(send_smtp_email)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling TransactionalEmailsApi->send_transac_email:" %s)