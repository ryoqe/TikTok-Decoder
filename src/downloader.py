import os
import re
import yt_dlp
from src.utils import log_info, log_error, log_success

TIKTOK_URL_REGEX = re.compile(
    r'https?://(?:www\.|vt\.|vm\.|t\.)?tiktok\.com/[^\s]+|https?://v\.douyin\.com/[^\s]+',
    re.IGNORECASE
)

def is_tiktok_url(text: str) -> bool:
    """Check if the text contains a valid TikTok or Douyin URL."""
    if not text:
        return False
    return bool(TIKTOK_URL_REGEX.search(text))

def extract_tiktok_url(text: str) -> str | None:
    """Extract the first TikTok or Douyin URL found in text."""
    if not text:
        return None
    match = TIKTOK_URL_REGEX.search(text)
    return match.group(0) if match else None

def download_tiktok_video(url: str, output_dir: str, custom_filename: str | None = None) -> dict:
    """
    Download video or photo post from TikTok URL using yt-dlp.
    Returns dict: {
        'success': bool,
        'filepath': str,
        'files': list[str],
        'is_image': bool,
        'title': str,
        'uploader': str,
        'duration': float,
        'error': str
    }
    """
    os.makedirs(output_dir, exist_ok=True)
    out_template = custom_filename if custom_filename else "%(id)s.%(ext)s"
    out_path_pattern = os.path.join(output_dir, out_template)

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
        'outtmpl': out_path_pattern,
        'quiet': True,
        'no_warnings': True,
        'overwrites': True,
        'noplaylist': True,
        'concurrent_fragment_downloads': 16,
        'buffersize': 4 * 1024 * 1024,
        'http_chunk_size': 10485760,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    try:
        log_info(f"Downloading TikTok content from: {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # Check for downloaded files
            downloaded_files = []
            
            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                downloaded_files.append(filename)
            else:
                base = os.path.splitext(filename)[0]
                for ext in ['.mp4', '.mkv', '.webm', '.mov', '.avi', '.jpg', '.jpeg', '.png', '.webp']:
                    candidate = base + ext
                    if os.path.exists(candidate) and os.path.getsize(candidate) > 0:
                        downloaded_files.append(candidate)
                        break

            # If yt-dlp extracted multiple images for a photo post
            if not downloaded_files:
                base_dir = os.path.dirname(filename)
                base_name = os.path.basename(os.path.splitext(filename)[0])
                for item in os.listdir(base_dir):
                    if item.startswith(base_name) and os.path.getsize(os.path.join(base_dir, item)) > 0:
                        downloaded_files.append(os.path.join(base_dir, item))

            if downloaded_files:
                primary_file = downloaded_files[0]
                is_image = primary_file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
                log_success(f"TikTok download successful: {primary_file} (is_image={is_image})")
                return {
                    'success': True,
                    'filepath': primary_file,
                    'files': downloaded_files,
                    'is_image': is_image,
                    'title': info.get('title') or 'TikTok Post',
                    'uploader': info.get('uploader') or info.get('uploader_id') or 'TikTok User',
                    'duration': info.get('duration', 0),
                    'error': None
                }
            else:
                log_error("Downloaded TikTok file not found or 0 bytes.")
                return {
                    'success': False,
                    'error': 'Не удалось найти сохраненный медиафайл на диске.'
                }

    except Exception as e:
        err_str = str(e)
        log_error(f"TikTok download error: {err_str}")
        
        # User-friendly error messages for common failure cases
        if "Unsupported URL" in err_str or "is not a valid URL" in err_str:
            user_err = "Предоставлена недействительная или не поддерживаемая ссылка TikTok."
        elif "Private video" in err_str or "video is private" in err_str:
            user_err = "Это видео приватное или удалено автором."
        else:
            user_err = f"Ошибка скачивания с TikTok: {err_str[-150:]}"
            
        return {'success': False, 'error': user_err}
