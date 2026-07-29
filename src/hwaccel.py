import subprocess
import os
import sys
from src.utils import log_info, log_warning, log_success

class HWAccelDetector:
    _cached_encoder = None

    @classmethod
    def detect_best_encoder(cls, ffmpeg_cmd="ffmpeg"):
        """Test and return the best available H.264 encoder (GPU or CPU fallback) with forced High Bitrate quality."""
        if cls._cached_encoder is not None:
            return cls._cached_encoder

        # Order of preference with forced high bitrate for crystal clear output
        candidates = [
            ("h264_nvenc", ["-c:v", "h264_nvenc", "-preset", "p4", "-cq", "16", "-b:v", "15M", "-maxrate", "25M", "-bufsize", "30M", "-pix_fmt", "yuv420p"]),
            ("h264_qsv", ["-c:v", "h264_qsv", "-global_quality", "16", "-b:v", "15M", "-maxrate", "25M", "-pix_fmt", "yuv420p"]),
            ("h264_amf", ["-c:v", "h264_amf", "-quality", "quality", "-b:v", "15M", "-maxrate", "25M", "-pix_fmt", "yuv420p"]),
            ("h264_mf", ["-c:v", "h264_mf", "-b:v", "15M", "-rate_control", "cbr", "-pix_fmt", "yuv420p"]),
            ("libx264", ["-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p"])
        ]

        for name, args in candidates:
            if name == "libx264":
                cls._cached_encoder = (name, args)
                return cls._cached_encoder
                
            # Test encoding a 1-second dummy color box
            cmd = [
                ffmpeg_cmd, "-y", "-v", "error",
                "-f", "lavfi", "-i", "color=c=black:s=64x64:d=0.1",
                "-frames:v", "1"
            ] + args + ["-f", "null", "-"]
            
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
                if res.returncode == 0:
                    log_success(f"Hardware Acceleration Detected: {name.upper()} (High Quality 15Mbps)")
                    cls._cached_encoder = (name, args)
                    return cls._cached_encoder
            except Exception:
                continue

        cls._cached_encoder = ("libx264", ["-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p"])
        return cls._cached_encoder
