import requests, time, json

def leonardo_image(leonardo_token, prompt, negative_prompt, model_id, photoReal, photoRealStrength, height, width, presetStyle):
    print("prompt-------->",prompt)
    print("token-------->",leonardo_token)
    url = "https://cloud.leonardo.ai/api/rest/v1/generations"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {leonardo_token}",
    }

    if photoReal == "true":
        print("PhotoReal!!!")
        payload = {
            "height": int(height),
            "width": int(width),
            "prompt": prompt,
            "alchemy": True,
            "photoReal": True,
            "photoRealStrength": float(photoRealStrength),
            "presetStyle": presetStyle,
            "num_images": 4,
        }
    else:
        payload = {
            "height": int(height),
            "modelId": model_id,
            "prompt": prompt,
            "width": int(width),
            "negative_prompt":negative_prompt,
            "presetStyle": presetStyle,
            "num_images": 4,
        }

    response = requests.post(url, json=payload, headers=headers)
    print(response.text)
    generation_id = json.loads(response.text)['sdGenerationJob']['generationId']
    print("post-response-------------->", generation_id)

    image_get_url ="https://cloud.leonardo.ai/api/rest/v1/generations/" + generation_id

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {leonardo_token}",
    }

    image_url = []

    while True:
        response = requests.get(image_get_url, headers=headers)
        print(json.loads(response.text))
        generated_images = json.loads(response.text)['generations_by_pk']['generated_images']
        print(generated_images)
        if generated_images != []:
            for i in range(4):
                image_url.append(generated_images[i]['url'])
            break
        else:
            time.sleep(5)
    print(image_url)

    return {'image_url': image_url, 'generation_id':generation_id}

def leonardo_init_image(leonardo_token, prompt, negative_prompt, photoRealStrength, height, width, presetStyle, init_image):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {leonardo_token}",
    }

    url = "https://cloud.leonardo.ai/api/rest/v1/init-image"

    payload = {"extension": "jpg"}

    response = requests.post(url, json=payload, headers=headers)

    print(response.status_code)

    fields = json.loads(response.json()['uploadInitImage']['fields'])

    url = response.json()['uploadInitImage']['url']

    image_id = response.json()['uploadInitImage']['id']

    files = {'file': init_image}

    response = requests.post(url, data=fields, files=files)

    print(response.status_code)

    url = "https://cloud.leonardo.ai/api/rest/v1/generations"

    payload = {
        "height": int(height),
        "init_image_id": image_id, # Setting model ID to Leonardo Creative
        "init_strength": 0.2,
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "width": int(width),
        # "imagePrompts": [image_id], # Accepts an array of image IDs
        "alchemy": True,
        "photoReal": True,
        "photoRealStrength": float(photoRealStrength),
        "presetStyle": presetStyle,
        "num_images": 4,
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.text)

    generation_id = response.json()['sdGenerationJob']['generationId']

    image_get_url ="https://cloud.leonardo.ai/api/rest/v1/generations/" + generation_id

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {leonardo_token}",
    }

    
    image_url = []

    while True:
        response = requests.get(image_get_url, headers=headers)
        print(json.loads(response.text))
        generated_images = json.loads(response.text)['generations_by_pk']['generated_images']
        print(generated_images)
        if generated_images != []:
            for i in range(4):
                image_url.append(generated_images[i]['url'])
            break
        else:
            time.sleep(5)
    print(image_url)

    return {'image_url': image_url, 'generation_id':generation_id}

def delete_image(leonardo_token, id):
    url = f"https://cloud.leonardo.ai/api/rest/v1/generations/{id}"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {leonardo_token}",
    }

    response = requests.delete(url, headers=headers)
    print("Deleted!---------------->", response.text)