import requests

def download_image(url, split_num, extension):
    local_filename = url.split('/')[split_num] + extension
    # NOTE the stream=True parameter
    with requests.get(url, stream=True) as r:
        with open(f"static/{local_filename}", 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
    return local_filename

def download_video(url):
    return "Download is completed!"

def download_audio(url):
    return "Download is completed!"