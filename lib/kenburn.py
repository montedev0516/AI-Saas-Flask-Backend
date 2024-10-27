import cv2
from moviepy.editor import ImageSequenceClip
import numpy as np

def lerp(start, end, progress):
    """Linear interpolation between start and end"""
    return (1 - progress) * start + progress * end

def create_ken_burns_effect(image_files, output_path, zoom_factor=1.3, duration=7, fps=24):
    # Load the image
    image = []
    for image_file in image_files:
        image_data = image_file.read()
        image_array = np.frombuffer(image_data, np.uint8)
        image.append(cv2.imdecode(image_array, cv2.IMREAD_COLOR))
    
    # height, width = image.shape[:2]
    # # Desired final dimensions after zooming
    # target_height = int(height / zoom_factor)
    # target_width = int(width / zoom_factor)


    # height = 765
    # width = 1394

    # target_height = 842
    # target_width = 1542
    
    frames = []
    # Generate frames with incremental cropping for the zoom effect
    height, width = image[0].shape[:2]
    # Desired final dimensions after zooming
    target_height = int(height / zoom_factor)
    target_width = int(width / zoom_factor)
    for i in range(fps * duration):
        progress = i / (fps * duration - 1)  # Normalized progress [0, 1]
        

        crop_width = int(width / zoom_factor)
        crop_height = int(height / zoom_factor)
        print("crop height, width----------->", crop_height, crop_width)

        
        # Smoothly calculate the top left corner of the cropping area
        start_x = int(lerp(0, (width - target_width), progress))
        start_y = int((height-target_height)/2)
        print("start_x_y", start_x, start_y)
        
        # Crop and resize the image
        cropped = image[0][start_y:start_y+crop_height, start_x:start_x+crop_width]
        resized = cv2.resize(cropped, (1366, 768), interpolation=cv2.INTER_LINEAR)
        
        # Convert color back to RGB for moviepy compatibility
        resized_rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)

        frames.append(resized_rgb)
        # frames.reverse()

    height, width = image[1].shape[:2]
    # Desired final dimensions after zooming
    target_height = int(height / zoom_factor)
    target_width = int(width / zoom_factor)

    for i in range(fps * duration):
        progress = i / (fps * duration - 1)  # Normalized progress [0, 1]
        
        # Use linear interpolation to smoothly calculate size of the cropping area
        # crop_width = int(lerp(progress, target_width, width))
        # crop_height = int(lerp(progress, target_height, height))
        crop_width = int(width / 1.1)
        crop_height = int(height / 1.1)
        print("crop height, width----------->", crop_height, crop_width)

        
        # Smoothly calculate the top left corner of the cropping area
        start_x = int((width-crop_width)/2)
        start_y = int(lerp(0, (height - crop_height), progress))
        print("start_x_y", start_x, start_y)
        
        # Crop and resize the image
        cropped = image[1][start_y:start_y+crop_height, start_x:start_x+crop_width]
        resized = cv2.resize(cropped, (1366, 768), interpolation=cv2.INTER_LINEAR)
        
        # Convert color back to RGB for moviepy compatibility
        resized_rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)

        frames.append(resized_rgb)
        # frames.reverse()

    height, width = image[2].shape[:2]
    # Desired final dimensions after zooming
    target_height = int(height / zoom_factor)
    target_width = int(width / zoom_factor)
    for i in range(fps * duration):
        progress = i / (fps * duration - 1)  # Normalized progress [0, 1]
        
        # Use linear interpolation to smoothly calculate size of the cropping area
        crop_width = int(lerp(progress, target_width, width))
        crop_height = int(lerp(progress, target_height, height))
        print("crop height, width----------->", crop_height, crop_width)

        
        # Smoothly calculate the top left corner of the cropping area
        start_x = int(lerp((width - target_width), 0, progress))
        start_y = int(lerp((height - target_height), 0, progress))
        print("start_x_y", start_x, start_y)
        
        # Crop and resize the image
        cropped = image[2][start_y:start_y+crop_height, start_x:start_x+crop_width]
        resized = cv2.resize(cropped, (1366, 768), interpolation=cv2.INTER_LINEAR)
        
        # Convert color back to RGB for moviepy compatibility
        resized_rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)

        frames.append(resized_rgb)
        # frames.reverse()
    
    # Create video clip from frames
    clip = ImageSequenceClip(frames, fps=fps)
    
    # Write the result to the output file
    clip.write_videofile(output_path, codec='libx264')

# Example usage:
