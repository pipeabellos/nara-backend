from __future__ import print_function
import time
import os
import dotenv
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from pprint import pprint

dotenv.load_dotenv()

sendinblue_api = str(os.environ.get("SENDINBLUE_API"))

def create_contact(email, list_id, phone, first_name, last_name):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = sendinblue_api

    api_instance = sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(configuration))
    create_contact = sib_api_v3_sdk.CreateContact(email="example@example.com", list_ids=[2], update_enabled=True, attributes={"FIRSTNAME":first_name, "LASTNAME":last_name, "SMS": phone})

    try:
        api_response = api_instance.create_contact(create_contact)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ContactsApi->create_contact: %s\n" % e)