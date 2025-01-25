import glob
import os
import argparse
import uuid
import shutil

import numpy as np
from PIL import Image
from PIL.Image import Resampling
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.CompositeVideoClip import concatenate_videoclips
from moviepy.video.fx import FadeIn, FadeOut
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip

# Constants
TARGET_SIZE = (720, 1280)  # 9:16 aspect ratio (portrait)
DURATION_PER_FRAME = 3  # Duration for each image (seconds)
INPUT_DIR = "photos/*.jpg"  # Input directory for images
OUTPUT_VIDEO = "video_"  # Output video file
FADE_DURATION = 1  # Duration of fade-in/out effects in seconds
BACKGROUND_MUSIC = "audio/song.mp3"  # Path to the background music file

# HTML Constants
TITLE = "[[TITLE]]"
VIDEO = "[[VIDEO]]"
PARTNER = "[[PARTNER]]"
VALENTINE = "[[VALENTINE]]"
GENDER = "[[GENDER]]"

META_PREVIEW_TITLE = "[[META_PREVIEW_TITLE]]"
META_PREVIEW_URL = "[[META_PREVIEW_URL]]"
META_PREVIEW_IMAGE = "[[META_PREVIEW_IMAGE]]"

ITINERARY = "[[ITINERARY]]"
CUSTOM_MESSAGE = "[[CUSTOM_MESSAGE]]"
FINAL_MESSAGE = "[[FINAL MESSAGE]]"

NO_ITINERARY = """
        <h4 id="noItinerary" class="second-part-text">
          Vei fi notificată în apropierea datei de 14 februarie
          <br />
          despre itinerariul întâlnirii
        </h4>
"""

ITINERARY_DETAILS = """
        <h4
          id="itineraryDetails"
          class="second-part-text"
          style="display: none"
        >
          Ne vedem la ora <span id="ora">[[HOUR]]:[[MINUTE]]</span> pe data de
          <span id="data"> 14 februarie </span> la
          <br />
          <span id="locatie">[[LOCATION]]</span>
        </h4>
"""

default_values = {
    TITLE: "Default Title",
    META_PREVIEW_TITLE: "Default Preview Title",
    META_PREVIEW_URL: "https://default.url",
    META_PREVIEW_IMAGE: "https://default.image",
    CUSTOM_MESSAGE: "Default custom message",
    ITINERARY_DETAILS: "Default itinerary details",
    FINAL_MESSAGE: "Default final message",
    PARTNER: "Default Name",
    VALENTINE: "Valentine",
    GENDER: "partenera"
}


def resize_image(image: Image.Image, target_size: tuple) -> Image.Image:
    img_aspect = image.width / image.height
    target_aspect = target_size[0] / target_size[1]

    # Resize logic: maintaining aspect ratio
    if img_aspect < target_aspect:  # Image is taller
        new_height = target_size[1]
        new_width = round(target_size[1] * img_aspect)
    else:  # Image is wider
        new_width = target_size[0]
        new_height = round(target_size[0] / img_aspect)

    # Resize image
    image = image.resize((new_width, new_height), Resampling.LANCZOS)

    # Create a black background
    black_background = Image.new("RGB", target_size, (0, 0, 0))

    # Center the image on the background
    x_offset = (target_size[0] - new_width) // 2
    y_offset = (target_size[1] - new_height) // 2
    black_background.paste(image, (x_offset, y_offset))

    return black_background


def create_video_with_transitions(images: list) -> concatenate_videoclips:
    clips = []
    fadein = FadeIn(FADE_DURATION)
    fadeout = FadeOut(FADE_DURATION)

    for i in range(len(images)):
        img = images[i]

        # Convert images to NumPy arrays
        img_array = np.array(img)

        # Create a clip for the current image
        clip = ImageSequenceClip([img_array], durations=[DURATION_PER_FRAME])

        # Apply fade-out to the current clip
        if i < len(images) - 1:  # Skip fade-out for the last image
            clip = fadeout.apply(clip)

        # Apply fade-in to the next clip
        if i > 0:  # Skip fade-in for the first image
            clip = fadein.apply(clip)

        # Add to the list of clips
        clips.append(clip)

    # Concatenate all clips
    video = concatenate_videoclips(clips, method="compose")
    return video


def replace_placeholders_in_html(user_uuid):
    parser = argparse.ArgumentParser()

    parser.add_argument('--title', help='Document Title')
    parser.add_argument('--preview_title', help='Preview Title')
    parser.add_argument('--preview_url', help='Preview URL')
    parser.add_argument('--preview_image', help='Preview Image')
    parser.add_argument('--custom_message', help='Custom Message')
    parser.add_argument('--itinerary_details', help='Itinerary Details')
    parser.add_argument('--final_message', help='Final Message')
    parser.add_argument('--valentine', help='Valentine`s Name')
    parser.add_argument('--partner', help='Partner`s Name')
    parser.add_argument('--gender', help='Partner`s Gender')

    args = parser.parse_args()

    file_path = "/var/www/html/index_" + str(args.partner).lower() + "-" + str(args.valentine).lower() + "-" + user_uuid.__str__() + ".html"
    shutil.copy("/var/www/html/index.html", file_path)

    with open(file_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    html_content = html_content.replace(TITLE, args.title or default_values[TITLE])
    html_content = html_content.replace(META_PREVIEW_TITLE, args.preview_title or default_values[META_PREVIEW_TITLE])
    html_content = html_content.replace(META_PREVIEW_URL, args.preview_url or default_values[META_PREVIEW_URL])
    html_content = html_content.replace(META_PREVIEW_IMAGE, args.preview_image or default_values[META_PREVIEW_IMAGE])
    html_content = html_content.replace(CUSTOM_MESSAGE, args.custom_message or default_values[CUSTOM_MESSAGE])
    html_content = html_content.replace(ITINERARY_DETAILS, args.itinerary_details or default_values[ITINERARY_DETAILS])
    html_content = html_content.replace(FINAL_MESSAGE, args.final_message or default_values[FINAL_MESSAGE])
    html_content = html_content.replace(PARTNER, args.partner or default_values[PARTNER])
    html_content = html_content.replace(GENDER, "partenerul meu" if args.gender == "M" else "partenera mea")
    html_content = html_content.replace(VALENTINE, args.valentine or default_values[VALENTINE])
    html_content = html_content.replace(VIDEO, "video/video_" + user_uuid.__str__() + ".mp4")

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(html_content)


def main():
    user_uuid = str(uuid.uuid4())[:8]
    tmp_folder = f"tmp_{user_uuid}"

    os.makedirs(tmp_folder)

    # Process and resize images
    replace_placeholders_in_html(user_uuid)

    images = []
    image_counter = 0
    for file in sorted(glob.glob(INPUT_DIR)):
        image_counter = image_counter + 1
        img = Image.open(file).convert("RGBA")
        resized_img = resize_image(img, TARGET_SIZE)
        output_path = os.path.join(tmp_folder, os.path.basename(file))
        resized_img.save(output_path, "JPEG")  # Save resized image as JPEG
        images.append(resized_img)

    print(f"Resizing complete. Resized images saved to: {tmp_folder}")

    # Create video with fade transitions
    video = create_video_with_transitions(images)

    # Add background music
    audio = AudioFileClip(BACKGROUND_MUSIC)
    video = video.with_audio(audio)

    # Ensure the audio matches the video duration
    video = video.with_duration(video.duration)

    # Save the final video
    video.write_videofile("/var/www/html/video/" + OUTPUT_VIDEO + user_uuid.__str__() + ".mp4", codec="libx264", fps=24,
                          audio_codec="aac")

    print(f"Video with fade transitions and audio saved as {OUTPUT_VIDEO + user_uuid.__str__()}.mp4")

    shutil.rmtree(tmp_folder)


if __name__ == "__main__":
    main()
