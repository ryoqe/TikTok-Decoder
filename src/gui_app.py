import os
import sys
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from src.utils import clean_path, collect_video_files, format_size
from src.analyzer import VideoAnalyzer, ExploitType
from src.converter import VideoConverter
from src.hwaccel import HWAccelDetector
from src.batch import BatchProcessor

class TikTokDecoderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TikTok Decoder v1.2.0 - Video Exploit Repair Suite")
        self.root.geometry("980x700")
        self.root.minsize(860, 600)
        
        self.analyzer = VideoAnalyzer()
        self.converter = VideoConverter()
        self.processor = BatchProcessor(self.analyzer, self.converter)
        
        self.queue_files = []
        self.is_processing = False
        
        self._setup_theme()
        self._build_ui()
        self._detect_hw()

    def _setup_theme(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        self.BG_DARK = "#1e1e2e"
        self.BG_PANEL = "#181825"
        self.BG_CARD = "#313244"
        self.TEXT_LIGHT = "#cdd6f4"
        self.TEXT_MUTED = "#a6adc8"
        self.ACCENT_PURPLE = "#cba6f7"
        self.ACCENT_GREEN = "#a6e3a1"
        self.ACCENT_BLUE = "#89b4fa"
        self.ACCENT_RED = "#f38ba8"
        
        self.root.configure(bg=self.BG_DARK)
        
        self.style.configure(".", background=self.BG_DARK, foreground=self.TEXT_LIGHT, font=("Segoe UI", 9))
        self.style.configure("TFrame", background=self.BG_DARK)
        self.style.configure("Panel.TFrame", background=self.BG_PANEL, relief="flat")
        self.style.configure("Card.TFrame", background=self.BG_CARD)
        
        self.style.configure("TLabel", background=self.BG_DARK, foreground=self.TEXT_LIGHT)
        self.style.configure("Panel.TLabel", background=self.BG_PANEL, foreground=self.TEXT_LIGHT)
        self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground=self.ACCENT_PURPLE, background=self.BG_PANEL)
        self.style.configure("SubHeader.TLabel", font=("Segoe UI", 9), foreground=self.TEXT_MUTED, background=self.BG_PANEL)
        
        self.style.configure("TButton", font=("Segoe UI", 9, "bold"), background=self.BG_CARD, foreground=self.TEXT_LIGHT, borderwidth=0)
        self.style.map("TButton", background=[("active", self.ACCENT_PURPLE), ("disabled", "#45475a")], foreground=[("active", "#11111b")])
        
        self.style.configure("Primary.TButton", font=("Segoe UI", 11, "bold"), background=self.ACCENT_GREEN, foreground="#11111b")
        self.style.map("Primary.TButton", background=[("active", "#b4befe")])
        
        self.style.configure("Treeview", background=self.BG_PANEL, foreground=self.TEXT_LIGHT, fieldbackground=self.BG_PANEL, rowheight=26, font=("Segoe UI", 9))
        self.style.configure("Treeview.Heading", background=self.BG_CARD, foreground=self.TEXT_LIGHT, font=("Segoe UI", 9, "bold"))
        self.style.map("Treeview", background=[("selected", self.ACCENT_PURPLE)], foreground=[("selected", "#11111b")])

    def _build_ui(self):
        # 1. Header Frame
        header_frame = ttk.Frame(self.root, style="Panel.TFrame", padding=12)
        header_frame.pack(fill="x", side="top")
        
        title_label = ttk.Label(header_frame, text="🎬 TikTok Decoder v1.2.0", style="Header.TLabel")
        title_label.pack(side="left")
        
        sub_label = ttk.Label(header_frame, text="Automated Exploit Repair & Manual Override Suite", style="SubHeader.TLabel")
        sub_label.pack(side="left", padx=15)
        
        self.hw_label = ttk.Label(header_frame, text="GPU: Detecting...", font=("Segoe UI", 9, "bold"), foreground=self.ACCENT_BLUE, background=self.BG_PANEL)
        self.hw_label.pack(side="right", padx=5)

        # 2. Main Content Split
        main_split = ttk.Frame(self.root, padding=10)
        main_split.pack(fill="both", expand=True)

        # Left Panel - Queue Table & File Buttons
        left_panel = ttk.Frame(main_split, style="Panel.TFrame", padding=8)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 5))

        btn_toolbar = ttk.Frame(left_panel, style="Panel.TFrame")
        btn_toolbar.pack(fill="x", pady=(0, 6))

        ttk.Button(btn_toolbar, text="➕ Add File(s)", command=self._add_files).pack(side="left", padx=2)
        ttk.Button(btn_toolbar, text="📂 Add Folder", command=self._add_folder).pack(side="left", padx=2)
        ttk.Button(btn_toolbar, text="🧹 Clear Queue", command=self._clear_queue).pack(side="left", padx=2)
        ttk.Button(btn_toolbar, text="📁 Open Output", command=self._open_output_dir).pack(side="right", padx=2)

        # Treeview Queue Table
        columns = ("filename", "exploit", "duration", "status")
        self.tree = ttk.Treeview(left_panel, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("filename", text="File Name")
        self.tree.heading("exploit", text="Detected / Selected Exploit Method")
        self.tree.heading("duration", text="Duration")
        self.tree.heading("status", text="Status")

        self.tree.column("filename", width=220)
        self.tree.column("exploit", width=220)
        self.tree.column("duration", width=70, anchor="center")
        self.tree.column("status", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(left_panel, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Right Panel - Control Settings & Options
        right_panel = ttk.Frame(main_split, style="Panel.TFrame", padding=10, width=300)
        right_panel.pack(side="right", fill="y", padx=(5, 0))

        ttk.Label(right_panel, text="🛠️ Repair & Manual Override", font=("Segoe UI", 11, "bold"), style="Panel.TLabel").pack(anchor="w", pady=(0, 8))

        # Manual Method Override Dropdown
        ttk.Label(right_panel, text="Exploit Mode Override:", style="Panel.TLabel").pack(anchor="w", pady=(2, 0))
        self.method_var = tk.StringVar(value="Auto-Detect (Recommended)")
        self.method_options = [
            "Auto-Detect (Recommended)",
            "Method 1: ut0ku (PTS Scaling)",
            "Method 2: LuisAlves10 (Trim Dummy Padding)",
            "Method 3: EditingSource (Header Doubled Trim)",
            "Method 4: NoBlur (VFR CFR Normalizer)",
            "Method 5: Standard (Clean Re-encode)"
        ]
        method_combo = ttk.Combobox(right_panel, textvariable=self.method_var, values=self.method_options, state="readonly")
        method_combo.pack(fill="x", pady=(2, 8))

        # Target FPS
        ttk.Label(right_panel, text="Target Frame Rate:", style="Panel.TLabel").pack(anchor="w", pady=(4, 0))
        self.fps_var = tk.StringVar(value="60 FPS")
        fps_combo = ttk.Combobox(right_panel, textvariable=self.fps_var, values=["60 FPS", "120 FPS"], state="readonly")
        fps_combo.pack(fill="x", pady=(2, 8))

        # Quality Preset
        ttk.Label(right_panel, text="Quality Preset (CRF):", style="Panel.TLabel").pack(anchor="w", pady=(4, 0))
        self.quality_var = tk.StringVar(value="CRF 16 (Ultra Quality)")
        quality_combo = ttk.Combobox(right_panel, textvariable=self.quality_var, values=["CRF 16 (Ultra Quality)", "CRF 18 (High Quality)", "CRF 23 (Balanced)"], state="readonly")
        quality_combo.pack(fill="x", pady=(2, 8))

        # HW Accel Toggle
        self.hw_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(right_panel, text="⚡ Hardware GPU Accel", variable=self.hw_var, style="Panel.TLabel").pack(anchor="w", pady=3)

        # Audio Normalization Toggle
        self.lufs_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(right_panel, text="🔊 LUFS Audio Normalization", variable=self.lufs_var, style="Panel.TLabel").pack(anchor="w", pady=3)

        # Workers Count
        ttk.Label(right_panel, text="Parallel Worker Threads:", style="Panel.TLabel").pack(anchor="w", pady=(8, 0))
        self.workers_var = tk.StringVar(value="2 Threads")
        workers_combo = ttk.Combobox(right_panel, textvariable=self.workers_var, values=["1 Thread", "2 Threads", "4 Threads"], state="readonly")
        workers_combo.pack(fill="x", pady=(2, 10))

        # Start Repair Button
        self.btn_start = ttk.Button(right_panel, text="🚀 START REPAIR", style="Primary.TButton", command=self._start_repair_thread)
        self.btn_start.pack(fill="x", pady=8, ipady=5)

        ttk.Button(right_panel, text="▶️ Play Selected Output", command=self._play_selected).pack(fill="x", pady=2)

        # 3. Bottom Progress Bar & Log Area
        bottom_frame = ttk.Frame(self.root, style="Panel.TFrame", padding=10)
        bottom_frame.pack(fill="x", side="bottom")

        self.progress_var = tk.DoubleVar(value=0)
        self.pbar = ttk.Progressbar(bottom_frame, variable=self.progress_var, maximum=100)
        self.pbar.pack(fill="x", pady=(0, 5))

        self.status_label = ttk.Label(bottom_frame, text="Ready. Add videos to start.", style="Panel.TLabel")
        self.status_label.pack(anchor="w")

    def _detect_hw(self):
        def worker():
            enc_name, _ = HWAccelDetector.detect_best_encoder()
            self.root.after(0, lambda: self.hw_label.configure(text=f"GPU: {enc_name.upper()}"))
        threading.Thread(target=worker, daemon=True).start()

    def _add_files(self):
        paths = filedialog.askopenfilenames(title="Select TikTok Videos", filetypes=[("Video Files", "*.mp4 *.mov *.mkv *.webm")])
        if paths:
            for p in paths:
                self._add_to_queue(p)

    def _add_folder(self):
        folder = filedialog.askdirectory(title="Select Folder with Videos")
        if folder:
            files = collect_video_files(folder)
            for f in files:
                self._add_to_queue(f)

    def _add_to_queue(self, file_path):
        file_path = clean_path(file_path)
        if any(item["path"] == file_path for item in self.queue_files):
            return
            
        analysis = self.analyzer.analyze(file_path)
        exploit_text = analysis["exploit_type"] if analysis else "Unknown"
        dur_text = f"{analysis['video_duration']:.1f}s" if analysis else "-"
        
        item_id = self.tree.insert("", "end", values=(os.path.basename(file_path), exploit_text, dur_text, "Pending"))
        self.queue_files.append({
            "id": item_id,
            "path": file_path,
            "analysis": analysis,
            "status": "Pending"
        })
        self.status_label.configure(text=f"Added {len(self.queue_files)} file(s) to queue.")

    def _clear_queue(self):
        if self.is_processing:
            return
        self.tree.delete(*self.tree.get_children())
        self.queue_files.clear()
        self.progress_var.set(0)
        self.status_label.configure(text="Queue cleared.")

    def _open_output_dir(self):
        out_dir = os.path.abspath("output")
        os.makedirs(out_dir, exist_ok=True)
        os.startfile(out_dir)

    def _play_selected(self):
        selected = self.tree.selection()
        if not selected:
            return
        item_values = self.tree.item(selected[0], "values")
        fname = item_values[0]
        name_no_ext, _ = os.path.splitext(fname)
        out_path = os.path.abspath(os.path.join("output", f"repaired_{name_no_ext}.mp4"))
        if os.path.exists(out_path):
            os.startfile(out_path)
        else:
            messagebox.showwarning("File Not Found", f"Repaired file not found:\n{out_path}")

    def _get_selected_method_override(self):
        sel = self.method_var.get()
        if "Method 1" in sel:
            return ExploitType.METHOD_1_ITSSCALE_PTS
        elif "Method 2" in sel:
            return ExploitType.METHOD_2_DUMMY_PADDING
        elif "Method 3" in sel:
            return ExploitType.METHOD_3_CONTAINER_DOUBLED
        elif "Method 4" in sel:
            return ExploitType.METHOD_4_VFR_NOBLUR
        elif "Method 5" in sel:
            return ExploitType.METHOD_STANDARD
        return "AUTO_DETECT"

    def _start_repair_thread(self):
        if self.is_processing:
            return
        if not self.queue_files:
            messagebox.showinfo("Queue Empty", "Please add video files before starting.")
            return
            
        self.is_processing = True
        self.btn_start.configure(state="disabled")
        self.progress_var.set(0)
        
        threading.Thread(target=self._run_repair, daemon=True).start()

    def _run_repair(self):
        target_fps = 120 if "120" in self.fps_var.get() else 60
        crf = 16 if "16" in self.quality_var.get() else (18 if "18" in self.quality_var.get() else 23)
        use_hw = self.hw_var.get()
        norm_audio = self.lufs_var.get()
        override_m = self._get_selected_method_override()
        
        out_dir = os.path.abspath("output")
        os.makedirs(out_dir, exist_ok=True)
        
        total = len(self.queue_files)
        for i, item in enumerate(self.queue_files):
            self.root.after(0, lambda item_id=item["id"]: self.tree.item(item_id, values=(self.tree.item(item_id, "values")[0], self.tree.item(item_id, "values")[1], self.tree.item(item_id, "values")[2], "Repairing...")))
            self.root.after(0, lambda idx=i, fname=os.path.basename(item["path"]): self.status_label.configure(text=f"Repairing [{idx+1}/{total}]: {fname}"))
            
            base_name = os.path.basename(item["path"])
            name_no_ext, _ = os.path.splitext(base_name)
            out_path = os.path.join(out_dir, f"repaired_{name_no_ext}.mp4")
            
            res = self.converter.convert(
                item["analysis"],
                out_path,
                target_fps=target_fps,
                crf=crf,
                use_hwaccel=use_hw,
                normalize_audio=norm_audio,
                override_method=override_m
            )
            
            status_str = "Done ✅" if res.get("success") else "Failed ❌"
            self.root.after(0, lambda item_id=item["id"], st=status_str: self.tree.item(item_id, values=(self.tree.item(item_id, "values")[0], self.tree.item(item_id, "values")[1], self.tree.item(item_id, "values")[2], st)))
            
            progress_pct = ((i + 1) / total) * 100
            self.root.after(0, lambda pct=progress_pct: self.progress_var.set(pct))
            
        self.root.after(0, self._finish_repair)

    def _finish_repair(self):
        self.is_processing = False
        self.btn_start.configure(state="normal")
        self.status_label.configure(text="All repairs completed successfully! Check output folder.")
        messagebox.showinfo("Complete", "All videos in queue have been processed and saved to 'output/' folder.")

def launch_gui():
    root = tk.Tk()
    app = TikTokDecoderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    launch_gui()
