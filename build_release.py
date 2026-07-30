import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path

# Ensure UTF-8 output encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

VERSION = "v1.2.0"

PROJECT_ROOT = Path(__file__).parent.resolve()
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
RELEASE_DIR = DIST_DIR / f"TikTok-Decoder-{VERSION}-Windows-x64"
ZIP_OUTPUT = DIST_DIR / f"TikTok-Decoder-{VERSION}-Windows-x64.zip"

def clean_previous_builds():
    print("🧹 Cleaning previous build directories...")
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR, ignore_errors=True)
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR, ignore_errors=True)
    print("✓ Cleanup complete.")

def build_executable():
    print(f"📦 Compiling TikTok Decoder standalone executable ({VERSION})...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--name", "TikTok-Decoder",
        "--clean",
        str(PROJECT_ROOT / "main.py")
    ]
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    if result.returncode != 0:
        print("❌ PyInstaller compilation failed!")
        sys.exit(1)
    print("✓ PyInstaller compilation successful.")

def prepare_release_package():
    print("📁 Organizing release files...")
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    
    pyinstaller_out = DIST_DIR / "TikTok-Decoder"
    if pyinstaller_out.exists():
        for item in pyinstaller_out.iterdir():
            dest = RELEASE_DIR / item.name
            if item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)
                
    # Copy essential documentation and helper scripts
    for file_name in ["README.md", "LICENSE", "ROADMAP.md", "run.bat"]:
        src_file = PROJECT_ROOT / file_name
        if src_file.exists():
            shutil.copy2(src_file, RELEASE_DIR / file_name)
            
    # Create input and output folders
    (RELEASE_DIR / "input").mkdir(exist_ok=True)
    (RELEASE_DIR / "output").mkdir(exist_ok=True)
    (RELEASE_DIR / "input" / ".gitkeep").touch()
    (RELEASE_DIR / "output" / ".gitkeep").touch()
    
    print("✓ Release package structured.")

def create_zip_archive():
    print(f"📦 Zipping release archive: {ZIP_OUTPUT.name}...")
    with zipfile.ZipFile(ZIP_OUTPUT, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(RELEASE_DIR):
            for file in files:
                full_path = Path(root) / file
                arcname = full_path.relative_to(DIST_DIR)
                zipf.write(full_path, arcname)
    print(f"✅ Success! Release archive created: {ZIP_OUTPUT}")

def main():
    clean_previous_builds()
    build_executable()
    prepare_release_package()
    create_zip_archive()

if __name__ == "__main__":
    main()
