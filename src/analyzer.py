import subprocess
import json
import os
from src.utils import log_warning, log_info

class ExploitType:
    METHOD_1_ITSSCALE_PTS = "METHOD_1_ITSSCALE_PTS"          # ut0ku/120fps-method: PTS scaled, high-fps frames
    METHOD_2_DUMMY_PADDING = "METHOD_2_DUMMY_PADDING"        # LuisAlves10: mvhd/mdhd atom patcher / trailing corrupted dummy packets
    METHOD_3_CONTAINER_DOUBLED = "METHOD_3_CONTAINER_DOUBLED"# EditingSource: 30fps container header with 60fps frame count / timebase hack
    METHOD_4_VFR_NOBLUR = "METHOD_4_VFR_NOBLUR"              # irgifebry/NoBlur: Sample table density hack / VFR timestamp jitter
    METHOD_STANDARD = "METHOD_STANDARD"                      # Standard compliant video

class VideoAnalyzer:
    def __init__(self, ffprobe_cmd="ffprobe"):
        self.ffprobe_cmd = ffprobe_cmd

    def probe(self, file_path):
        """Run ffprobe on file and return JSON dict."""
        cmd = [
            self.ffprobe_cmd,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format", "-show_streams",
            file_path
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(res.stdout)
        except Exception as e:
            log_warning(f"ffprobe failed for {file_path}: {e}")
            return None

    def analyze(self, file_path):
        """Analyze file and return exact exploit classification & metadata metrics."""
        data = self.probe(file_path)
        if not data:
            return None
            
        fmt = data.get("format", {})
        streams = data.get("streams", [])
        
        v_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
        a_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)
        
        if not v_stream:
            return None
            
        v_dur = float(v_stream.get("duration", 0) or fmt.get("duration", 0))
        a_dur = float(a_stream.get("duration", 0)) if a_stream else 0
        nb_frames = int(v_stream.get("nb_frames", 0) or 0)
        r_fps_str = v_stream.get("r_frame_rate", "30/1")
        avg_fps_str = v_stream.get("avg_frame_rate", "30/1")
        
        try:
            r_num, r_den = map(int, r_fps_str.split("/"))
            r_fps = r_num / r_den if r_den != 0 else 30.0
        except Exception:
            r_fps = 30.0

        try:
            avg_num, avg_den = map(int, avg_fps_str.split("/"))
            avg_fps = avg_num / avg_den if avg_den != 0 else r_fps
        except Exception:
            avg_fps = r_fps
            
        exploit_type = ExploitType.METHOD_STANDARD
        target_trim_dur = a_dur if a_dur > 0 else v_dur
        pts_scale_factor = 1.0
        
        # 1. Check Method 3 (EditingSource / Timebase Doubled): 30fps header, 60fps frame count (~1450 frames @ 48s)
        if nb_frames > 0 and r_fps == 30.0 and abs(v_dur - 48.3) < 4.0:
            exploit_type = ExploitType.METHOD_3_CONTAINER_DOUBLED
            target_trim_dur = nb_frames / 60.0
            pts_scale_factor = 0.5

        # 2. Check Method 2 (LuisAlves10 / Dummy Padding): Video duration > Audio duration
        elif a_stream and a_dur > 0 and (v_dur - a_dur) > 2.0:
            exploit_type = ExploitType.METHOD_2_DUMMY_PADDING
            target_trim_dur = a_dur
            pts_scale_factor = 1.0

        # 3. Check Method 4 (irgifebry/NoBlur - VFR Jitter / Sample Table Hack)
        elif abs(r_fps - avg_fps) > 2.0 or (a_stream and a_stream.get("time_base") == "1/22050"):
            exploit_type = ExploitType.METHOD_4_VFR_NOBLUR
            target_trim_dur = a_dur if a_dur > 0 else v_dur
                
        return {
            "file_path": file_path,
            "filename": os.path.basename(file_path),
            "file_size": int(fmt.get("size", 0)),
            "format_duration": float(fmt.get("duration", 0)),
            "video_duration": v_dur,
            "audio_duration": a_dur,
            "nb_frames": nb_frames,
            "container_fps": r_fps,
            "avg_fps": avg_fps,
            "exploit_type": exploit_type,
            "target_trim_dur": target_trim_dur,
            "pts_scale_factor": pts_scale_factor,
            "video_codec": v_stream.get("codec_name", "unknown"),
            "audio_codec": a_stream.get("codec_name", "none") if a_stream else "none"
        }
