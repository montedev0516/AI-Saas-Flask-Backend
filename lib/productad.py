import moviepy.editor as mpe
from io import BytesIO

def video_voiceover_music(video, voiceover, music, customer_logo):
    my_clip = mpe.VideoFileClip(video)
    audio_background = mpe.AudioFileClip(music)
    voice_clip = mpe.AudioFileClip(voiceover)
    service_logo = mpe.ImageClip('../ruiuio-takao/src/assets/images/Adclipz_Logo__Final.png')

    customer_logo = mpe.ImageClip(customer_logo)

    if my_clip.duration < voice_clip.duration:
        video_duration = voice_clip.duration
    else:
        video_duration = 21

    audio_clip = audio_background.subclip(0, video_duration)
    audio_clip = audio_clip.volumex(0.3)

    final_audio = mpe.CompositeAudioClip([voice_clip, audio_clip])
    final_clip = my_clip.set_audio(final_audio)

    logo_margin_x = 10  # Margin from the sides
    logo_margin_y = 10  # Margin from top or bottom
    logo_position = (final_clip.size[0] - 200 - logo_margin_x,  # Right margin
                 final_clip.size[1] - service_logo.size[1]*200/service_logo.size[0] - logo_margin_y)  # Bottom margin
    service_logo = (service_logo
            .resize(width=200)
            .set_opacity(0.5)
            .set_duration(21)
            .set_position(logo_position)
            )
    final_clip = mpe.CompositeVideoClip([final_clip, service_logo])
    logo_position = (logo_margin_x,  # Right margin
                 final_clip.size[1]-customer_logo.size[1]*200/customer_logo.size[0]-logo_margin_y)  # Bottom margin
    customer_logo = (customer_logo
            .resize(width=200)
            .set_opacity(0.5)
            .set_duration(21)
            .set_position(logo_position)
            )
    final_clip = mpe.CompositeVideoClip([final_clip, customer_logo])
    
    return final_clip

def video_voiceover(video, voiceover, customer_logo):
    video_clip = mpe.VideoFileClip(video)
    voice_clip = mpe.AudioFileClip(voiceover)

    final_clip = video_clip.set_audio(voice_clip)
    
    return final_clip