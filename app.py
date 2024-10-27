from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from datetime import timedelta
from dotenv import load_dotenv
from rich.markdown import Markdown
import os, time, datetime, base64, re, requests, json, mammoth
import moviepy.editor as mpe

import lib.leonardo, lib.download, lib.stability, lib.dall, lib.beautifulsoup, lib.pictory, lib.play, lib.heygen, lib.kenburn, lib.productad, pharmacist
from lib.openlib import Open_AI

from uuid import uuid1
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient

app = Flask(__name__)
CORS(app, cors_allowed_origins=['http://localhost:3000'])

# initialize jwt
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
jwt = JWTManager(app)

# Define database and users
app.config['MONGO_URI'] = 'mongodb://localhost:27017'
client = MongoClient(app.config['MONGO_URI'])
db_name = 'ruiu-io'

if db_name not in client.list_database_names():
    db = client[db_name]

db = client[db_name]
collection_name = 'user'

if collection_name not in db.list_collection_names():
    db.create_collection(collection_name)

users = db.user

# Get APIs from dotenv file
load_dotenv()
openai_key = os.getenv("openai_key")
assistant_id = os.getenv("assistant_id")
leonardo_token = os.getenv("leonardo_token")
stability_api = os.getenv("stability_api")
pictory_client_id = os.getenv("pictory_client_id")
pictory_client_secret = os.getenv("pictory_client_secret")

client = Open_AI(api_key=openai_key, assistant_id=assistant_id)
client.assistant_id = str(assistant_id)


# Define upload folder directory
UPLOAD_FOLDER = './static'  # Replace with your upload folder path
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def file_extract():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400

    if file:
        result = mammoth.extract_raw_text(file)
        content = result.value  # Extracted content
    return content

conversation = []

@app.route('/api/blog/text', methods = ['POST'])
def text_blog():
    prompt = request.form.get("prompt")
    print(prompt)
    client.load_thread()
    client.create_message(prompt)
    client.create_run()
    gpt_output = client.output()
    conversation.append(gpt_output)
    markdown = Markdown(gpt_output, code_theme="one-dark")
    print('-------------------MARK-----------------', markdown)

    return jsonify({'result': gpt_output})

@app.route('/api/blog/file', methods=['POST'])
def file_blog():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    print(request.form)
    tone = request.form.get("tone")
    print('-- Start ---', file.filename)
    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400

    if file:
        result = mammoth.extract_raw_text(file)
        content = result.value  # Extracted content
        prompt = content + "; Tone of Voice: " + tone
        print(prompt)
        client.load_thread()
        client.create_message(prompt)
        client.create_run()
        gpt_output = client.output()
        conversation.append(gpt_output)
        markdown = Markdown(gpt_output, code_theme="one-dark")
        print('-------------------MARK-----------------', markdown)

        return jsonify({'result': gpt_output})

@app.route('/api/blog/instruction', methods=['POST'])
def add_instruction():
    instructions = request.json["instructions"]
    print(instructions)
    add_instruction_url = "https://api.openai.com/v1/assistants/..."

    headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + openai_key,
    "OpenAI-Beta": "assistants=v1"
    }

    data ={
    "instructions": "You are a blog generator. You have to generate well-marked blogs. " + instructions,
    "name": "Blog Generator",
    "tools": [{"type": "code_interpreter"}],
    "model": "gpt-4"
    }

    response = requests.post(add_instruction_url, json=data, headers=headers)
    if(response):
        print(response)

    return response.text

# ----- Leonardo.ai API ------
@app.route('/api/image/leonardo', methods = ['POST'])
@jwt_required()
def leonardo_generator():
    # Access token identity
    current_user = get_jwt_identity()
    user_id = current_user['_id']
    print("current user--------------->", current_user)

    print("---------Leonardo!!!----------")
    prompt = request.form.get('prompt')
    negative_prompt = request.form.get('negative_prompt')
    model_id = request.form.get('model_id')
    photoReal = request.form.get('photoReal')
    photoRealStrength = request.form.get('photoRealStrength')
    height = request.form.get('height')
    width = request.form.get('width')
    presetStyle = request.form.get('presetStyle')  

    if 'init_image' in request.files:
        init_image = request.files['init_image']
        print("-----init_image!!!-----")
        image_url = lib.leonardo.leonardo_init_image(leonardo_token, prompt, negative_prompt, photoRealStrength, height, width, presetStyle, init_image)
    else:
        image_url = lib.leonardo.leonardo_image(leonardo_token, prompt, negative_prompt, model_id, photoReal, photoRealStrength, height, width, presetStyle)
    
    print("imageUrls-------------->", image_url)

    server_img_url = []
    for i in range(4):                    
        now = datetime.datetime.now()
        now_time = str(now)
        numbers = re.findall(r'\d+', now_time)
        file_id = ''.join(numbers)
        file_name = f"{file_id}.png" # Set file names with the names include generation time

        response = requests.get(image_url['image_url'][i])

        with open(f"static/{user_id}/Images/{file_name}", "wb") as f:
            f.write(response.content)
        server_img_url.append(f"http://localhost:5000/files/{user_id}/Images/{file_name}")
        users.update_one({'_id':user_id}, {'$push': {'Images': file_name}}) # Save file names in its user field of database

    lib.leonardo.delete_image(leonardo_token, image_url['generation_id'])
    print(server_img_url)
    return jsonify({'result': server_img_url})


# ----- Stability.ai API -----
@app.route('/api/image/stability', methods = ['POST'])
@jwt_required()
def stability_generator():
    print("-----Stability!!!-----")
    current_user = get_jwt_identity()
    _id = current_user['_id']

    model_s = request.form.get('model_s')
    style_s = request.form.get('style_s')
    cfg = request.form.get('cfg')
    step = request.form.get('step')
    strength = request.form.get('strength')
    prompt = request.form.get('prompt')
    negative_prompt = request.form.get('negative_prompt')
    model_s = request.form.get('model_s')
    
    if 'init_image' in request.files:
        init_image = request.files['init_image']
        print("-----init_image!!!-----")
        image_base64 = lib.stability.image_image(stability_api, prompt, negative_prompt, model_s, init_image, cfg, step, strength)
    else:
        image_base64 = lib.stability.text_image(stability_api, prompt, negative_prompt, model_s, style_s, cfg, step)
    
    server_img_url =[]
    for i in range(4):
        now = datetime.datetime.now()
        now_time = str(now)
        numbers = re.findall(r'\d+', now_time)
        file_id = ''.join(numbers)
        file_name = f"{file_id}.jpg"

        image_data = base64.b64decode(image_base64[i])
        with open(f"static/{_id}/Images/{file_name}", "wb") as f:
            f.write(image_data)

        server_img_url.append(f"http://localhost:5000/files/{_id}/Images/{file_name}")
        users.update_one({'_id': _id}, {'$push': {'Images': file_name}})

    return jsonify({'result': server_img_url})

# ----- Dall-E-3 API -----
@app.route('/api/image/dall-e-3', methods=['POST'])
@jwt_required()
def dall_generator():
    print("-----Dall-E-3!!!-----")
    current_user = get_jwt_identity()
    _id = current_user['_id']

    prompt = request.form.get('prompt')
    size = request.form.get('size')
    quality = request.form.get('quality')

    server_img_url = []
    for i in range(4):
        img_url = lib.dall.dall_image(openai_key, prompt, size, quality)
        print("imageUrl-------------->", img_url)

        now = datetime.datetime.now()
        now_time = str(now)
        numbers = re.findall(r'\d+', now_time)
        file_id = ''.join(numbers)
        file_name = f"{file_id}.png"

        response = requests.get(img_url)

        with open(f"static/{_id}/Images/{file_name}", "wb") as f:
            f.write(response.content)

        server_img_url.append(f"http://localhost:5000/files{_id}/Images/{file_name}")
        users.update_one({'_id': _id}, {'$push': {'images': file_name}})

    return jsonify({'result': server_img_url})

# Scrape URL
@app.route('/api/video/scrape', methods = ['POST'])
@jwt_required()
def scrape():
    print("-----scrape-----")
    homepage_url = request.form.get('homepage_url')
    print("homepage_url----------->", homepage_url)
    homepage_content = list(["HomePage"] + lib.beautifulsoup.extract_content(homepage_url))
    print(homepage_content)

    return jsonify({"homepage_content": homepage_content})

# Generate voiceover for website ad video from OpenAI Assistant
@app.route('/api/video/voiceoverGenerate', methods=['POST'])
@jwt_required()
def voiceover_generate():
    print("-----voiceover-----")
    homepage_content = request.form.get('homepage_content')

    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_key}",
        "OpenAI-Beta": "assistants=v1",
    }

    data = {
      "assistant_id": "asst_2Ldr35ivHKYWTMFAZ5zWGYPg",
      "thread": {
        "messages": [
          {"role": "user", 
           "content": homepage_content,
           }
        ]
      }
    }   

    run_url = "https://api.openai.com/v1/threads/runs"

    response = requests.post(run_url, json=data, headers=headers)

    voiceover_thread_id = response.json()["thread_id"]
    print(voiceover_thread_id)

    # time.sleep(2)
    
    get_url = "https://api.openai.com/v1/threads/"+ voiceover_thread_id + "/messages"

    while True:
        time.sleep(3)
        response = requests.get(get_url, headers=headers)
        print(response.text)
        print(response.json()["data"][0]["role"])
        if response.json()["data"][0]["content"] != [] and response.json()["data"][0]["content"][0]["text"]["value"] != '':
            transcript = response.json()["data"][0]["content"][0]["text"]["value"]
            print(transcript)
            break

    return jsonify({"message": transcript})

# Generate background website video from pictory.ai
@app.route('/api/video/pictory', methods=['POST'])
@jwt_required()
def generate_background_video():
    print("pictory-back-video")
    voiceover = request.form.get("voiceover")

    auth = lib.pictory.authenticate()
    job_id = lib.pictory.generate_preview(voiceover, auth)
    renderParams = lib.pictory.get_preview(job_id, auth)
    download_id = lib.pictory.render_video(renderParams, auth)
    videoURL = lib.pictory.get_download_link(auth, download_id)

    return jsonify({"videoURL": videoURL })

# Generate final website ad video
@app.route('/api/video/final', methods=['POST'])
@jwt_required()
def final_export():
    current_user = get_jwt_identity()
    _id = current_user['_id']

    print("-----final-----")
    avatar_checked = request.form.get("avatarChecked")
    if avatar_checked == 'true':
        x = request.form.get("x")
        y = request.form.get("y")
        H = request.form.get('H')
        W = request.form.get('W')
        h = request.form.get('h')
        w = request.form.get('w')
        scale = request.form.get("scale")
        avatar_style = request.form.get("avatar_style")
        X = -0.5 + (int(x) + int(w)/2)/int(W)
        Y = -0.5 + (int(y) + int(h)/2)/int(H)
        print('(X,Y)------------->', X, Y)
    else:
        x = None
        y = None
        scale = None
        avatar_style = None
    voiceover = request.form.get('voiceover')
    speed = request.form.get('speed')
    voice = request.form.get('voice')
    emotion = request.form.get('emotion')

    music_url = request.form.get('music_url')

    background_video = request.form.get("background_video") 
    avatar_id = request.form.get("avatar_id")

    if emotion == 'None':
        emotion = None
    print('emotion----------->', emotion)
    audioURL = lib.play.audio_generate(voiceover, speed, voice, emotion)

    video_id = lib.heygen.get_video_id(avatar_id, audioURL, background_video, avatar_checked, X, Y, scale, avatar_style)

    video_link = lib.heygen.get_video_link(video_id)

    if music_url != 'None':
        video_clip = mpe.VideoFileClip(video_link)
        music_clip = mpe.AudioFileClip(music_url)

        music_clip = music_clip.subclip(0, video_clip.duration)
        music_clip = music_clip.volumex(0.3)
        audio_clip = video_clip.audio

        final_audio = mpe.CompositeAudioClip([audio_clip, music_clip])
        final_clip = video_clip.set_audio(final_audio)
    else:
        final_clip = mpe.VideoFileClip(video_link)
    
    now = datetime.datetime.now()
    now_time = str(now)
    numbers = re.findall(r'\d+', now_time)
    file_id = ''.join(numbers)
    file_name = f"{file_id}.mp4"

    update = {"$push": {"BusinessVideos":{"$each":[file_name]}}}
    users.update_one({"_id":_id}, update)
    
    output_video_path = f'static/{_id}/Business Videos/{file_name}'
    final_clip.write_videofile(output_video_path)
    server_video_url = f"http://localhost:5000/files/{_id}/Business Videos/{file_name}"

    return jsonify({'video_link':server_video_url})

# Generate ChatGPT answer...
@app.route('/api/conversation/gpt', methods=['POST'])
def conversation_gpt():
    prompt = request.form.get('question')
    ans = pharmacist.pharmacist_assistant(prompt)
    return ans

# Generate product video voiceover from product details using openAI
@app.route('/api/productAd/voiceover', methods=['POST'])
def product_ad_voiceover():
    product_details = request.form.get('product_details')
    print("product_details------------>", product_details)

    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_key}",
        "OpenAI-Beta": "assistants=v1",
    }

    data = {
      "assistant_id": "asst_TIGkEo9xW1KJDyxojKZs5GoB",
      "thread": {
        "messages": [
          {"role": "user", 
           "content": product_details,
           }
        ]
      }
    }   

    run_url = "https://api.openai.com/v1/threads/runs"

    response = requests.post(run_url, json=data, headers=headers)
    print(response.text)

    voiceover_thread_id = response.json()["thread_id"]
    print(voiceover_thread_id)

    time.sleep(2)
    
    get_url = "https://api.openai.com/v1/threads/"+ voiceover_thread_id + "/messages"

    while True:
        time.sleep(3)
        response = requests.get(get_url, headers=headers)
        print(response.json()["data"][0]["role"])
        if response.json()["data"][0]["content"] != [] and response.json()["data"][0]["content"][0]["text"]["value"] != "":
            transcript = response.json()["data"][0]["content"][0]["text"]["value"]
            # print(transcript)
            break
            

    return jsonify({"voiceover": transcript})

# Generate product background video from 3 uploaded images using opencv
@app.route('/api/productAd/back-video', methods=['POST'])
@jwt_required()
def product_ad_video():
    current_user = get_jwt_identity()
    _id = current_user['_id']
    print("-----Product Video!!!-----")
    image_1 = request.files['image_1']
    image_2 = request.files['image_2']
    image_3 = request.files['image_3']

    images = [image_1, image_2, image_3]

    now = datetime.datetime.now()
    now_time = str(now)
    numbers = re.findall(r'\d+', now_time)
    file_id = ''.join(numbers)
    file_name = f"{file_id}.mp4"
    
    output_video_path = f'static/{_id}/{file_name}'
    lib.kenburn.create_ken_burns_effect(images, output_video_path)
    server_video_url = f"http://localhost:5000/files/{_id}/{file_name}"

    return jsonify({"video_url":server_video_url})

# Generate final product video(backVideo+voiceAudio+backMusic)
@app.route('/api/productAd/generate', methods=['POST'])
@jwt_required()
def product_ad_generate():
    print("-----Product video generate!!!-----")
    current_user = get_jwt_identity()
    _id = current_user['_id']

    video_url = request.form.get('video_url')
    music_url = request.form.get('music_url')
    voiceID = request.form.get('voiceID')
    voiceSpeed = request.form.get('voiceSpeed') 
    voiceover = request.form.get('voiceover')

    emotion = request.form.get('emotion')
    if emotion == 'None':
        emotion = None

    customer_logo = request.files['logo']

    print("emotion-------------->", emotion)
    now = datetime.datetime.now()
    now_time = str(now)
    numbers = re.findall(r'\d+', now_time)
    logo_file_id = ''.join(numbers)
    logo_file_name = f"logo-{logo_file_id}.png"
    
    output_customer_logo_path = f'static/{logo_file_name}'
    customer_logo.save(output_customer_logo_path)
    customer_logo = f"http://localhost:5000/files/{logo_file_name}"

    voice_url = lib.play.audio_generate(voiceover, voiceSpeed, voiceID, emotion)
    print(video_url, voice_url, music_url)

    if music_url == 'None':
        video_clip = lib.productad.video_voiceover(video_url, voice_url, customer_logo)
    else:
        video_clip = lib.productad.video_voiceover_music(video_url, voice_url, music_url, customer_logo)


    now = datetime.datetime.now()
    now_time = str(now)
    numbers = re.findall(r'\d+', now_time)
    file_id = ''.join(numbers)
    file_name = f"{file_id}.mp4"

    update = {"$push": {"ProductVideos":{"$each":[file_name]}}}
    users.update_one({"_id":_id}, update)
    
    output_video_path = f'static/{_id}/Product Videos/{file_name}'
    video_clip.write_videofile(output_video_path)
    server_video_url = f"http://localhost:5000/files/{_id}/Product Videos/{file_name}"

    os.remove(f"static/logo-{logo_file_id}.png")

    video_file_name = video_url.split('/')[-2] + '/' + video_url.split('/')[-1]
    os.remove(f"static/{video_file_name}")

    return jsonify({"finalVideo_url": server_video_url})

# Pull files from server directory via URL
@app.route('/files/<path:filename>')
def serve_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Get image history from database
@app.route('/api/image/history', methods = ['GET'])
@jwt_required()
def get_image_history():
    current_user = get_jwt_identity()
    _id = current_user['_id']

    user = users.find_one({"_id":current_user['_id']})
    print("currentUser--------------->", user)

    if not user['Images']:
        return jsonify({'msg':'No history'})
    
    files = user['Images']
    files = [f"http://localhost:5000/files/{_id}/Images/"+file for file in files]

    return jsonify({'histories':files})

# Get Business Video History from DB
@app.route('/api/video/business/history', methods=['GET'])
@jwt_required()
def get_business_video_history():
    current_user = get_jwt_identity()
    _id = current_user['_id']
    user = users.find_one({"_id":current_user['_id']})

    if not user['BusinessVideos']:
        return jsonify({'msg':'No history'})
    
    files = user['BusinessVideos']
    files = [f"http://localhost:5000/files/{_id}/Business Videos/"+file for file in files]

    return jsonify({'histories': files})

# Get Product Video History from DB
@app.route('/api/video/product/history', methods=['GET'])
@jwt_required()
def get_product_video_history():
    current_user = get_jwt_identity()
    _id = current_user['_id']
    user = users.find_one({"_id":current_user['_id']})

    if not user['ProductVideos']:
        return jsonify({'msg':'No history'})
    
    files = user['ProductVideos']
    files = [f"http://localhost:5000/files/{_id}/Product Videos/"+file for file in files]

    return jsonify({'histories': files})

@app.route('/api/login', methods = ['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    user = users.find_one({"email": email})

    if user and check_password_hash(user['password'], password):
        access_token = create_access_token(identity={'email':email, '_id':user['_id']}, expires_delta=timedelta(hours=1))
        return jsonify({"user":user, "access_token":access_token})
    
    return jsonify({"msg": "Invalid email or password"}), 401

@app.route('/api/signup', methods=['POST'])
def signup():
    _id=str(uuid1().hex)

    email = request.json.get('email')
    password = request.json.get('password')
    firstname = request.json.get('firstname')
    lastname = request.json.get('lastname')

    print('name------------->', firstname, lastname)
    print('email, password-------------->', email, password)

    # Password Encryption
    hashed_password = generate_password_hash(password)

    # Create user profile
    content = {"_id":_id, "firstname":firstname, "lastname": lastname, "email":email, "password":hashed_password, "BusinessVideos":[], "ProductVideos":[], "Images":[], "assistant":{"assistant_id":"", "instruction":""}}
    # content=dict(request.json)
    # content.update({ "_id":_id, "files":[] })
    
    if users.find_one({"email": email}):
        return {"message": "This user already exist"}, 401
    
    result =users.insert_one(content)

    
    if not result.inserted_id:
        return {"message":"Failed to insert"}, 500
        
    print('_id-------------->', result.inserted_id, result)
    os.makedirs(f'static/{_id}', exist_ok=True)  
    os.makedirs(f'static/{_id}/Business Videos', exist_ok=True)  
    os.makedirs(f'static/{_id}/Product Videos', exist_ok=True)  
    os.makedirs(f'static/{_id}/Images', exist_ok=True)  
    return {
        "message":"Success", 
        "data":{
            "id":result.inserted_id
            }
        }, 200
 
@app.route('/api/loadUser', methods = ['GET'])
@jwt_required()
def load_user():
    current_user = get_jwt_identity()

    return jsonify(current_user)

if __name__ == '__main__':
    print("Flask backend server is running!")
    app.run()