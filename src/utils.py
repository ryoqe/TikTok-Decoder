import os
import sys
from pathlib import Path

# Optional color support
try:
    import colorama
    colorama.init()
    COLOR_GREEN = colorama.Fore.GREEN
    COLOR_YELLOW = colorama.Fore.YELLOW
    COLOR_RED = colorama.Fore.RED
    COLOR_CYAN = colorama.Fore.CYAN
    COLOR_MAGENTA = colorama.Fore.MAGENTA
    COLOR_RESET = colorama.Style.RESET_ALL
    COLOR_BOLD = colorama.Style.BRIGHT
except ImportError:
    COLOR_GREEN = ""
    COLOR_YELLOW = ""
    COLOR_RED = ""
    COLOR_CYAN = ""
    COLOR_MAGENTA = ""
    COLOR_RESET = ""
    COLOR_BOLD = ""

SUPPORTED_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm", ".m4v"}

def log_info(msg):
    print(f"{COLOR_CYAN}[INFO]{COLOR_RESET} {msg}")

def log_success(msg):
    print(f"{COLOR_GREEN}[SUCCESS]{COLOR_RESET} {msg}")

def log_warning(msg):
    print(f"{COLOR_YELLOW}[WARN]{COLOR_RESET} {msg}")

def log_error(msg):
    print(f"{COLOR_RED}[ERROR]{COLOR_RESET} {msg}")

def log_header(msg):
    print(f"\n{COLOR_BOLD}{COLOR_MAGENTA}=== {msg} ==={COLOR_RESET}")

def clean_path(path_str):
    """Clean quotes, whitespace, and normalize path string."""
    if not path_str:
        return ""
    path_str = path_str.strip().strip('"').strip("'")
    return os.path.abspath(path_str)

def format_size(size_bytes):
    """Format bytes to human readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def collect_video_files(target_path):
    """Collect all valid video files from path or folder."""
    target_path = clean_path(target_path)
    if not os.path.exists(target_path):
        return []
    
    if os.path.isfile(target_path):
        ext = os.path.splitext(target_path)[1].lower()
        if ext in SUPPORTED_EXTENSIONS:
            return [target_path]
        return []
        
    found_files = []
    for root, _, files in os.walk(target_path):
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in SUPPORTED_EXTENSIONS and not f.startswith("repaired_") and not f.startswith("."):
                found_files.append(os.path.join(root, f))
    return sorted(found_files)
