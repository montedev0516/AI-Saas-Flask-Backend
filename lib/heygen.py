import requests, time

x_api_key = "..."

def get_video_id(avatar_id, audio_url, background_video, avatar_checked, X, Y, scale, avatar_style):
    
    url = "https://api.heygen.com/v2/video/generate"

    if avatar_checked == 'false':
        payload = {
        "video_inputs": [
            {
            "voice": {
                "type": "audio",
                "audio_url": audio_url
            },
            "background": {
                "type": "video",
                "url": background_video,
                "play_style":"fit_to_scene"
            }
            }
        ],
        "test": False,
        "aspect_ratio": "16:9"
        }

    else:
        payload = {
        "video_inputs": [
            {
            "character": {
                "type": "avatar",
                "avatar_id": avatar_id,
                "avatar_style": avatar_style,
                "offset":{
                    "x":X,
                    "y":Y,
                },
                "scale":scale,
            },
            "voice": {
                "type": "audio",
                "audio_url": audio_url
            },
            "background": {
                "type": "video",
                "url": background_video,
                "play_style":"fit_to_scene"
            }
            }
        ],
        "test": False,
        "aspect_ratio": "16:9"
        }

    headers ={
        "Content-Type":"application/json",
        "X-Api-Key":x_api_key,
    }

    response = requests.post(url, json=payload, headers=headers)
    print(response.text)

    video_id = response.json()["data"]["video_id"]

    return video_id

def get_video_link(video_id):
    url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"

    headers = {
        "X-Api-Key":x_api_key
    }

    while True:
        response = requests.get(url, headers=headers)
        status = response.json()["data"]["status"]
        print(status)
        if status == "completed":
            video_link = response.json()["data"]["video_url"]
            break
        time.sleep(5)

    return video_link