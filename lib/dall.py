import requests, json

def dall_image(openai_key, prompt, size, quality):
    url = "https://api.openai.com/v1/images/generations"

    headers ={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_key}",
    }

    data = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": size,
        "quality":quality
    }

    response = requests.post(url, json=data, headers=headers)

    generated_image = json.loads(response.text)['data'][0]['url']

    return generated_image