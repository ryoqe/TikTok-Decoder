import os
import concurrent.futures
from src.utils import log_info, log_success, log_error, log_header

class BatchProcessor:
    def __init__(self, analyzer, converter):
        self.analyzer = analyzer
        self.converter = converter

    def process_single(self, file_path, output_dir, target_fps=60, crf=16, use_hwaccel=True, override_method=None):
        analysis = self.analyzer.analyze(file_path)
        if not analysis:
            return {"file_path": file_path, "success": False, "error": "Analysis failed"}
            
        base_name = os.path.basename(file_path)
        name_no_ext, _ = os.path.splitext(base_name)
        out_name = f"repaired_{name_no_ext}.mp4"
        out_path = os.path.join(output_dir, out_name)
        
        res = self.converter.convert(
            analysis, out_path,
            target_fps=target_fps,
            crf=crf,
            use_hwaccel=use_hwaccel,
            override_method=override_method
        )
        res["file_path"] = file_path
        res["analysis"] = analysis
        return res

    def process_batch(self, file_list, output_dir, target_fps=60, crf=16, use_hwaccel=True, override_method=None, max_workers=2, progress_callback=None):
        log_header(f"Starting Multi-Threaded Batch Repair ({len(file_list)} files, {max_workers} workers)")
        results = []
        completed_count = 0
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {
                executor.submit(
                    self.process_single, f, output_dir, target_fps, crf, use_hwaccel, override_method
                ): f for f in file_list
            }
            
            for future in concurrent.futures.as_completed(future_to_file):
                f = future_to_file[future]
                completed_count += 1
                try:
                    res = future.result()
                    results.append(res)
                    if res.get("success"):
                        log_success(f"[{completed_count}/{len(file_list)}] Repaired: {os.path.basename(f)}")
                    else:
                        log_error(f"[{completed_count}/{len(file_list)}] Failed: {os.path.basename(f)}")
                except Exception as exc:
                    log_error(f"File {f} generated an exception: {exc}")
                    results.append({"file_path": f, "success": False, "error": str(exc)})
                    
                if progress_callback:
                    progress_callback(completed_count, len(file_list), f)
                    
        return results
