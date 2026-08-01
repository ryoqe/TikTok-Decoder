import os
import re
import multiprocessing
import yt_dlp
from urllib.parse import urlsplit
from src.utils import log_info, log_error, log_success

TIKTOK_URL_REGEX = re.compile(r'https://[^\s]+', re.IGNORECASE)
TIKTOK_HOSTS = {"tiktok.com", "www.tiktok.com", "m.tiktok.com", "vt.tiktok.com", "vm.tiktok.com", "t.tiktok.com"}

def is_tiktok_url(text: str) -> bool:
    """Check if the text contains one valid HTTPS TikTok URL."""
    if not text:
        return False
    return extract_tiktok_url(text) is not None

def extract_tiktok_url(text: str) -> str | None:
    """Extract one strictly validated TikTok URL."""
    if not text:
        return None
    matches = TIKTOK_URL_REGEX.findall(text)
    if len(matches) != 1:
        return None
    raw = matches[0].rstrip(".,!?;:")
    try:
        parsed = urlsplit(raw)
    except ValueError:
        return None
    if (
        parsed.scheme.lower() != "https"
        or (parsed.hostname or "").lower().rstrip(".") not in TIKTOK_HOSTS
        or parsed.username
        or parsed.password
        or parsed.port not in (None, 443)
        or not parsed.path.startswith("/")
    ):
        return None
    return raw

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
    out_template = (
        f"{custom_filename}.%(ext)s"
        if custom_filename and "%(ext)s" not in custom_filename
        else (custom_filename or "%(id)s.%(ext)s")
    )
    out_path_pattern = os.path.join(output_dir, out_template)

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
        'outtmpl': out_path_pattern,
        'quiet': True,
        'no_warnings': True,
        'overwrites': True,
        'noplaylist': True,
        'concurrent_fragment_downloads': 4,
        'max_filesize': 500 * 1024 * 1024,
        'restrictfilenames': True,
        'socket_timeout': 20,
        'retries': 3,
        'fragment_retries': 3,
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


def _download_worker(result_queue, url, output_dir, custom_filename):
    try:
        result_queue.put(download_tiktok_video(url, output_dir, custom_filename))
    except BaseException as exc:
        result_queue.put({"success": False, "error": f"Ошибка процесса загрузки: {exc}"})


def download_tiktok_video_isolated(url, output_dir, custom_filename, timeout=300):
    """Run yt-dlp in a process that can be forcibly stopped on a deadline."""
    try:
        context = multiprocessing.get_context("fork")
    except ValueError:
        context = multiprocessing.get_context("spawn")
    result_queue = context.Queue(maxsize=1)
    process = context.Process(
        target=_download_worker,
        args=(result_queue, url, output_dir, custom_filename),
        daemon=True,
    )
    process.start()
    process.join(max(1, int(timeout)))
    if process.is_alive():
        process.terminate()
        process.join(10)
        prefix = os.path.basename(custom_filename or "")
        if prefix and os.path.isdir(output_dir):
            for name in os.listdir(output_dir):
                if name.startswith(prefix):
                    try:
                        os.remove(os.path.join(output_dir, name))
                    except OSError:
                        pass
        return {"success": False, "error": "Превышено время ожидания скачивания с TikTok."}
    try:
        return result_queue.get(timeout=2)
    except Exception:
        return {"success": False, "error": "Процесс загрузки завершился без результата."}
