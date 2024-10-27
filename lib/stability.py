import requests, os, json


def text_image(stability_api, prompt, negative_prompt, model_s, style_s, cfg, step):
    if model_s == "Stable Diffusion XL 1.0":
            width = 1024
            height = 1024
            url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
    else:
        width = 512
        height = 512
        url = "https://api.stability.ai/v1/generation/stable-diffusion-v1-6/text-to-image"

    headers ={
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {stability_api}",
    }

    data = {
        "steps": int(step),
        "width": width,
        "height": height,
        "seed": 0,
        "cfg_scale": int(cfg),
        "samples": 4,
        "style_preset": style_s,
        "text_prompts": [
            {
            "text": prompt,
            "weight": 1
            },
        ]
    }

    if negative_prompt:
        negative_prompt = {
            "text": negative_prompt,
            "weight": -1
            }
        data["text_prompts"].append(negative_prompt)

    response = requests.post(url, json=data, headers=headers)

    image_base64 = []
    for i in range(4):
        image_base64.append(json.loads(response.text)['artifacts'][i]['base64'])

    return image_base64

def image_image(stability_api, prompt, negative_prompt, model_s, init_image, cfg, step, strength):
    if model_s == "Stable Diffusion XL 1.0":
        url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/image-to-image"
    else:
        url = "https://api.stability.ai/v1/generation/stable-diffusion-v1-6/image-to-image"

    

    headers ={
        "Accept": "application/json",
        "Authorization": f"Bearer {stability_api}",
    }
    
    data={
    "init_image_mode": "IMAGE_STRENGTH",
    "image_strength": float(strength),
    "steps": int(step),
    "seed": 0,
    "cfg_scale": int(cfg),
    "samples": 4,
    "text_prompts[0][text]": prompt,
    "text_prompts[0][weight]": 1,
    "text_prompts[1][text]": negative_prompt+" ",
    "text_prompts[1][weight]": -1,
}
    
    files = {
        "init_image": init_image
    }

    response = requests.post(url=url, headers=headers, data=data, files=files)

    image_base64 = []
    for i in range(4):
        image_base64.append(json.loads(response.text)['artifacts'][i]['base64'])

    return image_base64