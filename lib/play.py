import requests, json

def audio_generate(text, speed, voice, emotion):
    url = "https://api.play.ht/api/v2/tts"

    if emotion == None:
        voice_guidance = None
        style_guidance = None
    else:
        voice_guidance = 3
        style_guidance = 20

    payload = {
    "text": text,
    "voice": voice,
    "quality": "draft",
    "output_format": "mp3",
    "speed": int(speed),
    "sample_rate": 24000,
    "seed": None,
    "temperature": None,
    "voice_engine": "PlayHT2.0",
    "emotion": emotion,
    "voice_guidance": voice_guidance,
    "style_guidance": style_guidance
    }

    headers={
        "Content-Type":"application/json",
        "Authorization":"60dcdb2a97e64f1d855b2fabe874ad5e",
        "X-USER-ID":"0rzaxSuCiBNwgFCFizegVjB00Wu1",
        # "Accept":"text/event-stream",
    }

    print("start request")
    response = requests.post(url, json=payload, headers=headers)
    print(response.text)
    res = f'''{response.text}'''
    lines = res.strip().split('\n')

# Iterate over the lines to find the completed event
    for index, line in enumerate(lines):
        line = line.strip()
        if line.startswith('event: completed'):
            # Extract the data from the completed event
            data_line = lines[index+1]
            data = json.loads(data_line.split(': ', 1)[1])
            audioURL = data["url"]
            break
    
    return audioURL