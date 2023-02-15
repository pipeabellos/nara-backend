import requests
import json

base_url = "https://hg-nara.herokuapp.com/api/"

def train(XAVATARPATH):
    url = base_url + "train"
    payload={}
    headers = {
    'X-AVATAR-PATH': XAVATARPATH
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)


def build_prompt(XAVATARPATH, question):
    url = base_url + "prompt/build"
    payload = json.dumps({
        "question": question
    })
    headers = {
        'X-AVATAR-PATH': XAVATARPATH
    }
    print(payload)
    print(headers)

    response = requests.request("POST", url, headers=headers, data=payload)
    data = json.loads(response.text)
    embedding = response.json()['data']['prompt']
    return embedding

