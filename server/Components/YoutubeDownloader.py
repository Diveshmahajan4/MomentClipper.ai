import os
import yt_dlp
from pathlib import Path

def get_video_info(url):
    """Get video information without downloading"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info
    except Exception as e:
        print(f"Error getting video info: {str(e)}")
        return None

def safe_get_filesize(fmt):
    """Safely get filesize from format, handling None values"""
    filesize = fmt.get('filesize')
    if filesize is None:
        filesize = fmt.get('filesize_approx')
    return filesize if filesize is not None else 0

def safe_get_height(fmt):
    """Safely get height from format, handling None values"""
    height = fmt.get('height')
    return height if height is not None else 0

def safe_get_bitrate(fmt):
    """Safely get bitrate from format, handling None values"""
    bitrate = fmt.get('abr')
    return bitrate if bitrate is not None else 0

def select_best_format(formats, max_size_mb=500):
    """Select the best video format under the size limit"""
    video_formats = []
    
    for fmt in formats:
        vcodec = fmt.get('vcodec', 'none')
        acodec = fmt.get('acodec', 'none')
        
        if vcodec != 'none':
            video_formats.append(fmt)
    
    if not video_formats:
        return None
    
    video_formats.sort(key=safe_get_height, reverse=True)
    
    for fmt in video_formats:
        filesize = safe_get_filesize(fmt)
        if filesize > 0:  
            size_mb = filesize / (1024 * 1024)
            if size_mb < max_size_mb:
                return fmt
    
    return video_formats[0] if video_formats else None

def download_youtube_video(url):
    """Download video using manual format selection (similar to original pytubefix logic)"""
    try:
        info = get_video_info(url)
        if not info:
            raise Exception("Could not get video information")
        
        title = info.get('title', 'Unknown')
        title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        formats = info.get('formats', [])
        
        if not formats:
            raise Exception("No formats available")
        
        selected_format = select_best_format(formats, max_size_mb=500)
        
        if not selected_format:
            raise Exception("No suitable video format found")
        
        videos_dir = Path('videos')
        videos_dir.mkdir(exist_ok=True)
        
        print(f"Downloading video: {title}")
        
        has_video = selected_format.get('vcodec', 'none') != 'none'
        has_audio = selected_format.get('acodec', 'none') != 'none'
        
        if has_video and has_audio:
            print("Downloading progressive format (video + audio)...")
            ydl_opts = {
                'format': str(selected_format['format_id']),
                'outtmpl': str(videos_dir / '%(title)s.%(ext)s'),
                'noplaylist': True,
            }
        else:
            print("Downloading video and audio separately...")
            
            audio_formats = []
            for fmt in formats:
                acodec = fmt.get('acodec', 'none')
                vcodec = fmt.get('vcodec', 'none')
                if acodec != 'none' and vcodec == 'none':  
                    audio_formats.append(fmt)
            
            if not audio_formats:
                audio_formats = [fmt for fmt in formats if fmt.get('acodec', 'none') != 'none']
            
            if audio_formats:
                audio_formats.sort(key=safe_get_bitrate, reverse=True)
                best_audio = audio_formats[0]
                
                format_selector = f"{selected_format['format_id']}+{best_audio['format_id']}"
                print(f"Using format selector: {format_selector}")
                
                ydl_opts = {
                    'format': format_selector,
                    'outtmpl': str(videos_dir / '%(title)s.%(ext)s'),
                    'noplaylist': True,
                    'merge_output_format': 'mp4',  
                }
            else:
                print("No audio stream found, downloading video only...")
                ydl_opts = {
                    'format': str(selected_format['format_id']),
                    'outtmpl': str(videos_dir / '%(title)s.%(ext)s'),
                    'noplaylist': True,
                }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        downloaded_files = list(videos_dir.glob("*.mp4")) + list(videos_dir.glob("*.webm")) + list(videos_dir.glob("*.mkv"))
        if downloaded_files:
            output_file = max(downloaded_files, key=os.path.getctime)
            print(f"Downloaded: {title} to 'videos' folder")
            print(f"File path: {output_file}")
            return str(output_file)
        else:
            raise Exception("Download completed but file not found")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def download_youtube_video_simple(url):
    """Simplified version that lets yt-dlp handle format selection automatically"""
    try:        
        info = get_video_info(url)
        if not info:
            raise Exception("Could not get video information")
        
        title = info.get('title', 'Unknown')
        title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        
        videos_dir = Path('videos')
        videos_dir.mkdir(exist_ok=True)
        
        print(f"Downloading video: {title}")
        
        ydl_opts = {
            'format': 'best[filesize<500M]/best[height<=720]/best',  
            'outtmpl': str(videos_dir / '%(title)s.%(ext)s'),
            'noplaylist': True,
            'merge_output_format': 'mp4',
            'ignoreerrors': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        downloaded_files = list(videos_dir.glob("*.mp4")) + list(videos_dir.glob("*.webm")) + list(videos_dir.glob("*.mkv"))
        if downloaded_files:
            output_file = max(downloaded_files, key=os.path.getctime)
            print(f"Downloaded: {title} to 'videos' folder")
            print(f"File path: {output_file}")
            return str(output_file)
        else:
            raise Exception("Download completed but file not found")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

if __name__ == "__main__":
    youtube_url = input("Enter YouTube video URL: ")
    
    print("\nChoose download method:")
    print("1. Advanced format selection (mimics original pytubefix logic)")
    print("2. Simple download (recommended - lets yt-dlp handle format selection)")
    
    choice = input("Enter choice (1 or 2, default is 2): ").strip()
    
    if choice == "1":
        download_youtube_video(youtube_url)
    else:
        download_youtube_video_simple(youtube_url)