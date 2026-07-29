import os
import sys
import argparse
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils import (
    log_info, log_success, log_warning, log_error, log_header,
    clean_path, collect_video_files, format_size
)
from src.analyzer import VideoAnalyzer, ExploitType
from src.converter import VideoConverter
from src.batch import BatchProcessor

METHOD_MAP = {
    "auto": "AUTO_DETECT",
    "method1": ExploitType.METHOD_1_ITSSCALE_PTS,
    "method2": ExploitType.METHOD_2_DUMMY_PADDING,
    "method3": ExploitType.METHOD_3_CONTAINER_DOUBLED,
    "method4": ExploitType.METHOD_4_VFR_NOBLUR,
    "standard": ExploitType.METHOD_STANDARD
}

def main():
    parser = argparse.ArgumentParser(
        description="TikTok Video Exploit Decoder & Repair Tool v1.2.0",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-i", "--input", help="Path to input video file or folder (Default: 'input/')", default="input")
    parser.add_argument("-o", "--output", help="Path to output directory (Default: 'output/')", default="output")
    parser.add_argument("-fps", "--target-fps", type=int, help="Target FPS for repaired video (Default: 60)", default=60)
    parser.add_argument("-crf", "--crf", type=int, help="H.264 CRF quality level (Default: 16)", default=16)
    parser.add_argument("-m", "--method", choices=list(METHOD_MAP.keys()), default="auto", help="Manual Exploit Repair Method Override")
    parser.add_argument("--gui", action="store_true", help="Launch Desktop Graphical Interface (GUI)")
    parser.add_argument("--gpu", "--hwaccel", action="store_true", help="Enable GPU Hardware Acceleration", default=True)
    parser.add_argument("--lufs", action="store_true", help="Enable LUFS Audio Normalization")
    parser.add_argument("-j", "--jobs", type=int, help="Parallel worker threads for batch repair", default=2)
    
    args = parser.parse_args()
    
    if args.gui:
        from src.gui_app import launch_gui
        launch_gui()
        return
        
    inp_path = clean_path(args.input)
    out_dir = clean_path(args.output)
    
    if not os.path.isabs(inp_path):
        inp_path = os.path.abspath(inp_path)
    if not os.path.isabs(out_dir):
        out_dir = os.path.abspath(out_dir)
        
    os.makedirs(inp_path if os.path.isdir(inp_path) else os.path.dirname(inp_path), exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)
    
    files_to_process = collect_video_files(inp_path)
    
    if not files_to_process:
        log_warning(f"No valid video files found in: {inp_path}")
        log_info("Please place .mp4 videos inside the 'input/' folder or specify a file path with -i <path>")
        return
        
    log_header(f"TikTok Decoder v1.2.0 - Batch Engine ({len(files_to_process)} video(s))")
    print(f"Input path:  {inp_path}")
    print(f"Output path: {out_dir}")
    print(f"Method Mode: {args.method.upper()}")
    print(f"HW Accel:   {'ENABLED' if args.gpu else 'DISABLED'}")
    print(f"Jobs:       {args.jobs} parallel worker(s)\n")
    
    analyzer = VideoAnalyzer()
    converter = VideoConverter()
    processor = BatchProcessor(analyzer, converter)
    
    override_m = METHOD_MAP.get(args.method.lower(), "AUTO_DETECT")
    
    results = processor.process_batch(
        files_to_process,
        out_dir,
        target_fps=args.target_fps,
        crf=args.crf,
        use_hwaccel=args.gpu,
        override_method=override_m,
        max_workers=args.jobs
    )
    
    success_count = sum(1 for r in results if r.get("success"))
    log_header("Processing Complete")
    log_success(f"Successfully repaired {success_count} / {len(files_to_process)} file(s).")
    print(f"Check output folder: {out_dir}")

if __name__ == "__main__":
    main()
