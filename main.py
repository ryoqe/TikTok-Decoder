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

def process_file(file_path, output_dir, analyzer, converter, target_fps=60, crf=16):
    log_header(f"Processing: {os.path.basename(file_path)}")
    analysis = analyzer.analyze(file_path)
    
    if not analysis:
        log_error(f"Failed to analyze video: {file_path}")
        return False
        
    print(f"  • Video Duration: {analysis['video_duration']:.2f}s")
    print(f"  • Audio Duration: {analysis['audio_duration']:.2f}s")
    print(f"  • Frame Count: {analysis['nb_frames']} frames")
    print(f"  • Detected Exploit: {analysis['exploit_type']}")
    
    if analysis['exploit_type'] == ExploitType.METHOD_3_CONTAINER_DOUBLED:
        print("  • Recognized: EditingSource / 30fps Header Hack -> Restoring 60 FPS timeline & natural 1.0x audio")
    elif analysis['exploit_type'] == ExploitType.METHOD_2_DUMMY_PADDING:
        print(f"  • Recognized: LuisAlves10 / Dummy Padding -> Stripping trailing garbage packets beyond {analysis['target_trim_dur']:.2f}s")
    elif analysis['exploit_type'] == ExploitType.METHOD_1_ITSSCALE_PTS:
        print(f"  • Recognized: ut0ku / 120fps-method (-itsscale) -> Rescaling PTS ({analysis['pts_scale_factor']:.6f}) to align high-FPS frames")
    elif analysis['exploit_type'] == ExploitType.METHOD_4_VFR_NOBLUR:
        print("  • Recognized: irgifebry / NoBlur (VFR Jitter) -> Normalizing to Constant Frame Rate (CFR)")
    
    base_name = os.path.basename(file_path)
    name_no_ext, ext = os.path.splitext(base_name)
    out_name = f"repaired_{name_no_ext}.mp4"
    out_path = os.path.join(output_dir, out_name)
    
    log_info(f"Target Repair FPS: {target_fps} | CRF: {crf}")
    result = converter.convert(analysis, out_path, target_fps=target_fps, crf=crf)
    
    if result.get("success"):
        log_success(f"Repaired! Saved to: {out_path} ({result['formatted_size']}, took {result['elapsed_sec']:.1f}s)\n")
        return True
    else:
        log_error(f"Repair failed for {file_path}\n")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="TikTok Video Exploit Decoder & Repair Tool (60/120 FPS Fixer)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-i", "--input", help="Path to input video file or folder (Default: 'input/')", default="input")
    parser.add_argument("-o", "--output", help="Path to output directory (Default: 'output/')", default="output")
    parser.add_argument("-fps", "--target-fps", type=int, help="Target FPS for repaired video (Default: 60)", default=60)
    parser.add_argument("-crf", "--crf", type=int, help="H.264 CRF quality level (Default: 16)", default=16)
    
    args = parser.parse_args()
    
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
        
    log_header(f"Found {len(files_to_process)} video(s) for processing")
    print(f"Input path:  {inp_path}")
    print(f"Output path: {out_dir}\n")
    
    analyzer = VideoAnalyzer()
    converter = VideoConverter()
    
    success_count = 0
    for f in files_to_process:
        if process_file(f, out_dir, analyzer, converter, target_fps=args.target_fps, crf=args.crf):
            success_count += 1
            
    log_header("Processing Complete")
    log_success(f"Successfully repaired {success_count} / {len(files_to_process)} file(s).")
    print(f"Check output folder: {out_dir}")

if __name__ == "__main__":
    main()
