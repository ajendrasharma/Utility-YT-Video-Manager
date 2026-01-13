import PyInstaller.__main__
import os
import sys

# Define paths
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
entry_point = os.path.join(base_dir, "src", "yt", "main.py")
assets_dir = os.path.join(base_dir, "assets")

# Build commands
build_args = [
    entry_point,
    "--name=YT_AI_Analyst",
    "--onefile",
    "--windowed", # No console window
    f"--add-data={assets_dir}{os.pathsep}assets",
    "--clean",
    "--distpath=deployment/dist",
    "--workpath=deployment/build",
    "--specpath=deployment",
]

if __name__ == "__main__":
    print(f"Starting build from {base_dir}...")
    PyInstaller.__main__.run(build_args)
    print("\nBuild complete! Check deployment/dist/YT_AI_Analyst.exe")
