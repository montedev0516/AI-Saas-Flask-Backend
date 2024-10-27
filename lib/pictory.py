import requests
import time

client_id = "5rdbjopbhrl3r9kr8jjd6aid2j"
client_secret = "AQICAHj2M6vvARxFsI7YkL0kYPCJprPYkDqIoJSR/Gpb1sUf6wFnT3dUbTJl8V/PBQixTHrRAAAAlDCBkQYJKoZIhvcNAQcGoIGDMIGAAgEAMHsGCSqGSIb3DQEHATAeBglghkgBZQMEAS4wEQQMJChMf4mskcyFVel4AgEQgE4yeQfE4H2b1EWC+Zxn1W0E3Tc7+YjnIpP9o9FwUGvNgX5Bh10fqax5FAez4c98g74vh9FYeV1yrpDSp8+m50DztGvU960CeR3RI+QZ/rA="


def authenticate():
    url = "https://api.pictory.ai/pictoryapis/v1/oauth2/token"

    headers ={
        "Accept":"application/json",
        "Content-Type":"application/json",
        "Authorization": client_id,
    }

    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
    }

    response = requests.post(url, json=payload, headers=headers)
    auth = response.json()["access_token"]

    return auth


def generate_preview(text, auth):
    url = "https://api.pictory.ai/pictoryapis/v1/video/storyboard"

    payload = {
        "videoName": "W3Schools", 
        "videoDescription": "Welcome to W3Schools",
        "language": "en", 
        "audio": {
            "autoBackgroundMusic": True, 
            "backGroundMusicVolume": 0.5, 
            "aiVoiceOver": {
                "speaker": "Jackson", 
                "speed": 100, 
                "amplifyLevel": 0 
            }
        },
        "scenes": [
            {
                "text": text, 
                "voiceOver": False, 
                "splitTextOnNewLine": False, 
                "splitTextOnPeriod": True 
            }
        ]
    }

    headers = {
        "Authorization": auth,
        "X-Pictory-User-Id":client_id,
        "Content-Type":"application/json",
    }

    response = requests.post(url, json=payload, headers=headers)

    job_id = response.json()["jobId"]

    return job_id

def get_preview(job_id, auth):
    url = f"https://api.pictory.ai/pictoryapis/v1/jobs/{job_id}"

    headers = {
        "Authorization": auth,
        "X-Pictory-User-Id": client_id,
    }

    while True:
        response = requests.get(url, headers=headers)
        print(response.json())
        data = response.json()
        if "renderParams" in data["data"]:
            renderParams = data["data"]["renderParams"]
            break
        time.sleep(2)

    for scene in renderParams["scenes"]:
        for text_line in scene["sub_scenes"][0]["text_lines"]:
            text_line["text"] = ""

    return renderParams

def render_video(renderParams, auth):
    url = "https://api.pictory.ai/pictoryapis/v1/video/render" 

    headers = {
        "Authorization": auth,
        "X-Pictory-User-Id":client_id,
        "Content-Type":"application/json",
    }

    payload = renderParams

    response = requests.post(url, json=payload, headers=headers)

    download_id = response.json()["data"]["job_id"]

    return download_id

def get_download_link(auth, download_id):
    url = f"https://api.pictory.ai/pictoryapis/v1/jobs/{download_id}"

    headers = {
        "Authorization": auth,
        "X-Pictory-User-Id":client_id,
    }

    while True:
        response = requests.get(url, headers=headers)
        print(response.text)
        data = response.json()

        if data["data"]["status"] == "completed":
            videoURL = data["data"]["videoURL"]
            break
        time.sleep(10)    

    return videoURL