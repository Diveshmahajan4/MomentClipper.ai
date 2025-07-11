import os
import threading
import re
import requests
import json
import uuid
from urllib.parse import urlparse
from .supabase_client import (
    get_video_processing, update_video_processing, get_language_dubbing, update_language_dubbing,
    add_cloudinary_url_to_video_processing, add_cloudinary_url_to_language_dubbing
)
from .utils import upload_to_cloudinary, update_supabase
from components.YoutubeDownloader import download_youtube_video
from components.Edit import extractAudio, crop_video, extractAudioDubbed
from components.Transcription import transcribeAudio
from components.LanguageTasks import GetHighlight, getMultipleHighlights
from components.FaceCrop import crop_to_vertical, combine_videos
from components.GenerateCaptions import add_captions
from components.Translation import translate_transcript_with_timestamps
from components.TextToSpeech import transcript_to_speech, merge_audio_with_video

def ensure_directories():
    """Ensure all necessary directories exist"""
    directories = ['media', 'videos', 'media/captioned']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

def process_video_task(video_processing_id):
    """
    Process a video in a background thread
    """
    video_processing = get_video_processing(video_processing_id)
    
    if not video_processing:
        print(f"Error: Video processing with ID {video_processing_id} not found")
        return
    
    try:
        update_video_processing(video_processing_id, {
            'status': 'PROCESSING'
        })
        
        ensure_directories()
        
        vid = download_youtube_video(video_processing.get('youtube_url'))
        if not vid:
            update_video_processing(video_processing_id, {
                'error_message': "Unable to download the video",
                'status': 'FAILED'
            })
            return
            
        vid = vid.replace(".webm", ".mp4")
        update_video_processing(video_processing_id, {
            'original_video_path': vid
        })
        
        audio = extractAudio(vid)
        if not audio:
            update_video_processing(video_processing_id, {
                'error_message': "No audio file found",
                'status': 'FAILED'
            })
            return

        transcriptions = transcribeAudio(audio)
        if len(transcriptions) == 0:
            update_video_processing(video_processing_id, {
                'error_message': "No transcriptions found",
                'status': 'FAILED'
            })
            return
            
        trans_text = ""
        for text, start, end in transcriptions:
            trans_text += (f"{start} - {end}: {text}")

        json_string = getMultipleHighlights(trans_text, video_processing.get('num_shorts', 1))

        highlights_data = json.loads(json_string)

        for i, highlight in enumerate(highlights_data):
            print(f"Generating short {i+1}/{video_processing.get('num_shorts', 1)}")
            print("Num_shorts: ", video_processing.get('num_shorts', 1))
            
            start = highlight.get('start')
            stop = highlight.get('end')
            print("Start: ", start)
            print("Stop: ", stop)
            
            if start == 0 or stop == 0:
                print(f"Error in getting highlight {i+1}, skipping")
                continue
                
            output = f"media/Out_{i}.mp4"
            
            crop_video(vid, output, start, stop)
            
            cropped = f"media/cropped_{i}.mp4"
            crop_to_vertical(output, cropped)
            
            final_path = f"media/final_{video_processing_id}_{i}.mp4"
            combine_videos(output, cropped, final_path)
            
            if video_processing.get('add_captions', True):
                try:
                    captioned_path = f"media/captioned/final_{video_processing_id}_{i}_captioned.mp4"
                    
                    add_captions(
                        final_path,
                        captioned_path,
                        font="PoetsenOne-Regular.ttf",
                        font_size=80,
                        font_color="white",
                        stroke_width=2,
                        stroke_color="black",
                        highlight_current_word=True,
                        word_highlight_color="#29BFFF",
                        line_count=2,
                        padding=40,
                        shadow_strength=1.0,
                        shadow_blur=0.1,
                        use_local_whisper=True,
                        print_info=True
                    )
                    
                    if os.path.exists(captioned_path):
                        final_path = captioned_path
                        print(f"Successfully added captions to short {i+1}")
                    else:
                        print(f"Failed to add captions to short {i+1}, using original video")
                except Exception as e:
                    print(f"Error adding captions to short {i+1}: {str(e)}, using original video")
            else:
                print(f"Captions disabled for this processing task, skipping caption generation")
            
            upload_result = upload_to_cloudinary(final_path, f"user_{video_processing.get('username', 'anonymous')}_{i}")
            if upload_result:
                add_cloudinary_url_to_video_processing(video_processing_id, upload_result['url'], upload_result['public_id'])
                print(f"Uploaded short {i+1}/{video_processing.get('num_shorts', 1)} to Cloudinary: {upload_result['url']}")
            else:
                print(f"Failed to upload short {i+1} to Cloudinary, continuing with others")
        
        video_processing = get_video_processing(video_processing_id)
        if video_processing.get('cloudinary_urls_json'):
            update_video_processing(video_processing_id, {
                'status': 'COMPLETED'
            })
            
            cloudinary_urls = json.loads(video_processing.get('cloudinary_urls_json'))
            urls = [item['url'] for item in cloudinary_urls]
            update_supabase(
                video_processing.get('username', 'anonymous'),
                video_processing.get('youtube_url'),
                urls
            )
            return
        else:
            update_video_processing(video_processing_id, {
                'error_message': "Failed to create any shorts",
                'status': 'FAILED'
            })
    
    except Exception as e:
        update_video_processing(video_processing_id, {
            'status': 'FAILED',
            'error_message': str(e)
        })

def start_processing_video(video_processing_id):
    """
    Start a background thread to process the video
    """
    thread = threading.Thread(target=process_video_task, args=(video_processing_id,))
    thread.daemon = True
    thread.start()
    return thread 

def is_cloudinary_url(url):
    """
    Check if a URL is a Cloudinary URL
    """
    parsed_url = urlparse(url)
    return 'cloudinary.com' in parsed_url.netloc or 'res.cloudinary.com' in parsed_url.netloc

def download_from_cloudinary(url, output_path):
    """
    Download a video file from Cloudinary
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return output_path
    except Exception as e:
        print(f"Error downloading from Cloudinary: {e}")
        return None

def process_dubbing_task(dubbing_id):
    """
    Process a language dubbing task in a background thread
    
    Steps:
    1. Download the video (from YouTube or Cloudinary)
    2. Extract audio
    3. Transcribe audio
    4. Translate transcript
    5. Generate speech from translated transcript
    6. Merge speech with original video
    7. Add captions (optional)
    8. Upload to Cloudinary
    """
    dubbing = get_language_dubbing(dubbing_id)
    
    if not dubbing:
        print(f"Error: Language dubbing with ID {dubbing_id} not found")
        return
    
    try:
        update_language_dubbing(dubbing_id, {
            'status': 'PROCESSING'
        })
        ensure_directories()
        
        if not os.path.exists('media/dubbed'):
            os.makedirs('media/dubbed')
        
        if is_cloudinary_url(dubbing.get('video_url')):
            print(f"Detected Cloudinary URL: {dubbing.get('video_url')}")
            vid_output_path = f"videos/cloudinary_video_{dubbing_id}.mp4"
            vid = download_from_cloudinary(dubbing.get('video_url'), vid_output_path)
            if not vid:
                update_language_dubbing(dubbing_id, {
                    'error_message': "Unable to download the video from Cloudinary",
                    'status': 'FAILED'
                })
                return
        else:
            print(f"Detected YouTube or other URL: {dubbing.get('video_url')}")
            vid = download_youtube_video(dubbing.get('video_url'))
            if not vid:
                update_language_dubbing(dubbing_id, {
                    'error_message': "Unable to download the video",
                    'status': 'FAILED'
                })
                return
            
            vid = vid.replace(".webm", ".mp4")
        
        update_language_dubbing(dubbing_id, {
            'original_video_path': vid
        })
        
        audio = extractAudioDubbed(vid, dubbing_id)
        if not audio:
            update_language_dubbing(dubbing_id, {
                'error_message': "No audio file found",
                'status': 'FAILED'
            })
            return
            
        transcriptions = transcribeAudio(audio)
        if len(transcriptions) == 0:
            update_language_dubbing(dubbing_id, {
                'error_message': "No transcriptions found",
                'status': 'FAILED'
            })
            return
        
        print(f"Translating transcript from {dubbing.get('source_language')} to {dubbing.get('target_language')}")
        translated_transcript = translate_transcript_with_timestamps(
            transcriptions, 
            source_language=dubbing.get('source_language'),
            target_language=dubbing.get('target_language')
        )
        
        if not translated_transcript:
            update_language_dubbing(dubbing_id, {
                'error_message': "Failed to translate transcript",
                'status': 'FAILED'
            })
            return
        
        dubbed_audio_path = f"media/dubbed/audio_{dubbing_id}.wav"
        print(f"Generating speech from translated transcript using voice: {dubbing.get('voice')}")
        audio_result = transcript_to_speech(
            translated_transcript,
            dubbed_audio_path,
            voice=dubbing.get('voice')
        )
        
        if not audio_result:
            update_language_dubbing(dubbing_id, {
                'error_message': "Failed to generate speech from translated transcript",
                'status': 'FAILED'
            })
            return
        
        dubbed_video_path = f"media/dubbed/video_{dubbing_id}.mp4"
        print("Merging translated audio with original video")
        merge_success = merge_audio_with_video(
            vid,
            dubbed_audio_path,
            dubbed_video_path
        )
        
        if not merge_success:
            update_language_dubbing(dubbing_id, {
                'error_message': "Failed to merge audio with video",
                'status': 'FAILED'
            })
            return
        
        update_language_dubbing(dubbing_id, {
            'dubbed_video_path': dubbed_video_path
        })
        
        final_path = dubbed_video_path
        if dubbing.get('add_captions', True):
            try:
                captioned_path = f"media/captioned/dubbed_{dubbing_id}_captioned.mp4"
                
                translated_text = []
                for text, start, end in translated_transcript:
                    translated_text.append({
                        "start": start,
                        "end": end,
                        "text": text
                    })

                add_captions(
                    dubbed_video_path,
                    captioned_path,
                    font="PoetsenOne-Regular.ttf",
                    font_size=30,
                    font_color="white",
                    stroke_width=2,
                    stroke_color="black",
                    highlight_current_word=True,
                    word_highlight_color="#29BFFF",
                    line_count=2,
                    padding=40,
                    shadow_strength=1.0,
                    shadow_blur=0.1,
                    use_local_whisper=False,  # Use provided segments instead
                    segments=translated_text,
                    print_info=True
                )
                
                if os.path.exists(captioned_path):
                    final_path = captioned_path
                    print("Successfully added captions to dubbed video")
                else:
                    print("Failed to add captions to dubbed video, using non-captioned version")
            except Exception as e:
                print(f"Error adding captions to dubbed video: {str(e)}, using non-captioned version")
        else:
            print("Captions disabled for this dubbing task, skipping caption generation")
        
        upload_result = upload_to_cloudinary(final_path, f"dubbed_{dubbing.get('username', 'anonymous')}_{dubbing.get('target_language')}")
        if upload_result:
            add_cloudinary_url_to_language_dubbing(dubbing_id, upload_result['url'], upload_result['public_id'])
            print(f"Uploaded dubbed video to Cloudinary: {upload_result['url']}")
            
            update_language_dubbing(dubbing_id, {
                'status': 'COMPLETED'
            })
            return
        else:
            update_language_dubbing(dubbing_id, {
                'error_message': "Failed to upload dubbed video to Cloudinary",
                'status': 'FAILED'
            })
    
    except Exception as e:
        update_language_dubbing(dubbing_id, {
            'status': 'FAILED',
            'error_message': str(e)
        })

def start_dubbing_process(dubbing_id):
    """
    Start a background thread to process the language dubbing
    """
    thread = threading.Thread(target=process_dubbing_task, args=(dubbing_id,))
    thread.daemon = True
    thread.start()
    return thread 