import instaloader
import os
import re
from transcribe import transcribe_video
from chatrequest import get_response
from chatrequest import test_response

base_directory = "InstagramVideos"
L = instaloader.Instaloader(dirname_pattern=os.path.join(base_directory, '{shortcode}'))
L.download_comments = False
L.download_pictures = False
video_path = None
txt_path = None

def check_result_format(result):
    expected_failure = [["false", "false", "false", "false"]]
    cleaned_result = [[item.strip().lower() for item in sublist] for sublist in result]
    return cleaned_result == expected_failure

def remove_non_ascii(text):
    return ''.join(char for char in text if ord(char) < 128)

def remove_hashtags(text):
    return re.sub(r'#(\S+)', r'\1', text)

def download_instagram_video(url):
    # Extract shortcode from URL
    shortcode = url.split("/")[-2]
    post = instaloader.Post.from_shortcode(L.context, shortcode)

    # Download the post
    L.download_post(post, target=shortcode)

    # Path where the files are downloaded
    path = os.path.join(base_directory, shortcode)

    # After download, remove all files except the .mp4 and .txt
    for filename in os.listdir(path):
        if not filename.endswith(".mp4") and not filename.endswith(".txt"):
            os.remove(os.path.join(path, filename))
        if filename.endswith(".mp4"):
            video_path = os.path.join(path, filename)
        elif filename.endswith(".txt"):
            txt_path = os.path.join(path, filename)

    with open(txt_path, 'r') as file:
        caption = file.read()

    caption_clean = remove_non_ascii(caption)
    caption_clean = remove_hashtags(caption_clean)

    test = test_response(caption_clean)
    if check_result_format(test):
        prompt = transcribe_video(video_path, caption_clean)
        response = get_response(prompt)
    else:
        response = test
    return response