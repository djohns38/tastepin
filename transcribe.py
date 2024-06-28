from moviepy.editor import VideoFileClip
import speech_recognition as sr
import os
import re

def remove_non_ascii(text):
    return ''.join(char for char in text if ord(char) < 128)

def remove_hashtags(text):
    return re.sub(r'#(\S+)', r'\1', text)

def transcribe_video(video_path, caption_clean):
    video = VideoFileClip(video_path)
    audio = video.audio
    audio_path = video_path.replace('.mp4', '.wav')
    audio.write_audiofile(audio_path)

    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
        transcription = recognizer.recognize_google(audio_data)
        
    os.remove(audio_path)
    os.remove(video_path)

    return f"Caption: {caption_clean}\nTranscription: {transcription}"



