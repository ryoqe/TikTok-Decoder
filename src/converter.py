import subprocess
import os
import time
from src.analyzer import ExploitType
from src.hwaccel import HWAccelDetector
from src.utils import log_info, log_success, log_error, format_size

class VideoConverter:
    def __init__(self, ffmpeg_cmd="ffmpeg"):
        self.ffmpeg_cmd = ffmpeg_cmd

    def convert(self, analysis_data, output_path, target_fps=60, crf=17, preset="ultrafast", use_hwaccel=True, normalize_audio=False, override_method=None, progress_callback=None):
        """Convert/repair video with ultra-fast multithreading and accurate expected duration progress calculation."""
        inp_path = analysis_data["file_path"]
        exploit_type = override_method if (override_method and override_method != "AUTO_DETECT") else analysis_data["exploit_type"]
        trim_dur = analysis_data.get("target_trim_dur", 0)
        pts_scale = analysis_data.get("pts_scale_factor", 1.0)
        has_audio = analysis_data.get("audio_codec", "none") != "none"
        total_duration = float(analysis_data.get("video_duration", 0))
        
        # Calculate expected output duration for accurate 0%-100% progress tracking
        if exploit_type in [ExploitType.METHOD_3_CONTAINER_DOUBLED, ExploitType.METHOD_1_ITSSCALE_PTS]:
            expected_duration = total_duration * (pts_scale if (pts_scale > 0 and pts_scale < 1.0) else 0.5)
        elif exploit_type == ExploitType.METHOD_2_DUMMY_PADDING and trim_dur > 0:
            expected_duration = trim_dur
        else:
            expected_duration = total_duration if total_duration > 0 else 1.0

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Select encoder arguments (GPU vs CPU) with forced multithreading and ultrafast preset
        if use_hwaccel:
            enc_name, enc_args = HWAccelDetector.detect_best_encoder(self.ffmpeg_cmd)
        else:
            enc_name, enc_args = ("libx264", ["-c:v", "libx264", "-crf", str(crf), "-preset", preset, "-tune", "fastdecode", "-threads", "0", "-pix_fmt", "yuv420p"])

        base_flags = [
            self.ffmpeg_cmd,
            "-y",
            "-err_detect", "ignore_err",
            "-max_error_rate", "1.0",
            "-i", inp_path
        ]
        
        if exploit_type == ExploitType.METHOD_3_CONTAINER_DOUBLED:
            if has_audio:
                if normalize_audio:
                    filter_str = f"[0:v]setpts=0.5*PTS,fps={target_fps}[v];[0:a]asetpts=0.5*PTS,loudnorm=I=-16:TP=-1.5:LRA=11[a]"
                else:
                    filter_str = f"[0:v]setpts=0.5*PTS,fps={target_fps}[v];[0:a]asetpts=0.5*PTS[a]"
                cmd = base_flags + [
                    "-filter_complex", filter_str,
                    "-map", "[v]", "-map", "[a]",
                    "-c:a", "aac", "-b:a", "320k", "-ar", "44100"
                ] + enc_args + [output_path]
            else:
                filter_str = f"[0:v]setpts=0.5*PTS,fps={target_fps}[v]"
                cmd = base_flags + [
                    "-filter_complex", filter_str,
                    "-map", "[v]"
                ] + enc_args + [output_path]

        elif exploit_type == ExploitType.METHOD_1_ITSSCALE_PTS:
            if has_audio:
                filter_str = f"[0:v]setpts=0.5*PTS,fps={target_fps}[v];[0:a]asetpts=0.5*PTS[a]"
                cmd = base_flags + [
                    "-filter_complex", filter_str,
                    "-map", "[v]", "-map", "[a]",
                    "-c:a", "aac", "-b:a", "320k", "-ar", "44100"
                ] + enc_args + [output_path]
            else:
                filter_str = f"[0:v]setpts=0.5*PTS,fps={target_fps}[v]"
                cmd = base_flags + [
                    "-filter_complex", filter_str,
                    "-map", "[v]"
                ] + enc_args + [output_path]
            
        elif exploit_type == ExploitType.METHOD_2_DUMMY_PADDING:
            cmd = base_flags + [
                "-t", f"{trim_dur:.3f}",
                "-r", str(target_fps)
            ] + enc_args
            if has_audio:
                cmd += ["-c:a", "aac", "-b:a", "320k"]
            cmd.append(output_path)

        elif exploit_type == ExploitType.METHOD_4_VFR_NOBLUR:
            cmd = base_flags + [
                "-r", str(target_fps)
            ] + enc_args
            if has_audio:
                cmd += ["-c:a", "aac", "-b:a", "320k"]
            cmd.append(output_path)
            
        else:  # STANDARD
            cmd = base_flags + [
                "-r", str(target_fps)
            ] + enc_args
            if has_audio:
                cmd += ["-c:a", "aac", "-b:a", "320k"]
            cmd.append(output_path)
            
        # Add -progress pipe:1 to monitor real-time rendering percentage
        cmd_progress = cmd[:-1] + ["-progress", "pipe:1", "-nostats", cmd[-1]]

        start_time = time.time()
        try:
            # Reading only stdout while stderr is piped can fill the OS buffer and
            # leave FFmpeg blocked near the end on noisy/damaged files.
            process = subprocess.Popen(
                cmd_progress, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace", bufsize=1,
            )
            output_lines = []
            
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    output_lines.append(line)
                    if len(output_lines) > 400:
                        output_lines.pop(0)
                if line and "out_time_us=" in line:
                    try:
                        us_val = int(line.split("=")[1].strip())
                        sec_val = us_val / 1000000.0
                        if expected_duration > 0 and progress_callback:
                            pct = min(99.0, (sec_val / expected_duration) * 100.0)
                            progress_callback(pct)
                    except Exception:
                        pass

            process.wait()
            stderr_out = "".join(output_lines)
            elapsed = time.time() - start_time
            
            if process.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                if progress_callback:
                    progress_callback(100.0)
                out_size = os.path.getsize(output_path)
                return {
                    "success": True,
                    "output_path": output_path,
                    "elapsed_sec": elapsed,
                    "output_size": out_size,
                    "formatted_size": format_size(out_size),
                    "encoder_used": enc_name,
                    "method_applied": exploit_type
                }
            else:
                log_error(f"FFmpeg conversion failed: {stderr_out[-300:]}")
                return {"success": False, "error": stderr_out}
        except Exception as e:
            log_error(f"Exception during conversion: {e}")
            return {"success": False, "error": str(e)}
