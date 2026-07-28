import subprocess
import os
import time
from src.analyzer import ExploitType
from src.utils import log_info, log_success, log_error, format_size

class VideoConverter:
    def __init__(self, ffmpeg_cmd="ffmpeg"):
        self.ffmpeg_cmd = ffmpeg_cmd

    def convert(self, analysis_data, output_path, target_fps=60, crf=16, preset="medium"):
        """Convert/repair video based on analysis result."""
        inp_path = analysis_data["file_path"]
        exploit_type = analysis_data["exploit_type"]
        trim_dur = analysis_data["target_trim_dur"]
        pts_scale = analysis_data["pts_scale_factor"]
        has_audio = analysis_data["audio_codec"] != "none"
        
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        base_flags = [
            self.ffmpeg_cmd,
            "-y",
            "-err_detect", "ignore_err",
            "-max_error_rate", "1.0",
            "-i", inp_path
        ]
        
        if exploit_type == ExploitType.METHOD_3_CONTAINER_DOUBLED:
            # EditingSource: Scale video PTS 0.5x to 60 FPS, trim container duration, keep audio 1.0x natural speed
            filter_str = f"[0:v]setpts=0.5*PTS,fps={target_fps}[v]"
            cmd = base_flags + [
                "-t", str(trim_dur),
                "-filter_complex", filter_str,
                "-map", "[v]"
            ]
            if has_audio:
                cmd += ["-map", "0:a:0", "-c:a", "aac", "-b:a", "192k"]
            cmd += [
                "-c:v", "libx264", "-crf", str(crf), "-preset", preset,
                output_path
            ]

        elif exploit_type == ExploitType.METHOD_1_ITSSCALE_PTS:
            # ut0ku/120fps-method: Rescale PTS to align valid high-FPS frames to audio duration
            filter_str = f"[0:v]setpts={pts_scale:.8f}*PTS,fps={target_fps}[v]"
            cmd = base_flags + [
                "-t", str(trim_dur),
                "-filter_complex", filter_str,
                "-map", "[v]"
            ]
            if has_audio:
                cmd += ["-map", "0:a:0", "-c:a", "copy"]
            cmd += [
                "-c:v", "libx264", "-crf", str(crf), "-preset", preset,
                output_path
            ]
            
        elif exploit_type == ExploitType.METHOD_2_DUMMY_PADDING:
            # LuisAlves10: Trim corrupted trailing packets beyond audio duration WITHOUT distorting video speed
            cmd = base_flags + [
                "-t", str(trim_dur),
                "-r", str(target_fps),
                "-c:v", "libx264", "-crf", str(crf), "-preset", preset
            ]
            if has_audio:
                cmd += ["-c:a", "copy"]
            cmd.append(output_path)

        elif exploit_type == ExploitType.METHOD_4_VFR_NOBLUR:
            # irgifebry/NoBlur: Eliminate VFR jitter, re-encode to strict Constant Frame Rate (CFR)
            cmd = base_flags + [
                "-r", str(target_fps),
                "-c:v", "libx264", "-crf", str(crf), "-preset", preset
            ]
            if has_audio:
                cmd += ["-c:a", "aac", "-b:a", "192k"]
            cmd.append(output_path)
            
        else:  # STANDARD
            cmd = base_flags + [
                "-r", str(target_fps),
                "-c:v", "libx264", "-crf", str(crf), "-preset", preset
            ]
            if has_audio:
                cmd += ["-c:a", "copy"]
            cmd.append(output_path)
            
        start_time = time.time()
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            elapsed = time.time() - start_time
            
            if res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                out_size = os.path.getsize(output_path)
                return {
                    "success": True,
                    "output_path": output_path,
                    "elapsed_sec": elapsed,
                    "output_size": out_size,
                    "formatted_size": format_size(out_size)
                }
            else:
                log_error(f"FFmpeg conversion failed: {res.stderr[-300:]}")
                return {"success": False, "error": res.stderr}
        except Exception as e:
            log_error(f"Exception during conversion: {e}")
            return {"success": False, "error": str(e)}
