# Youtube Video Manager

**Youtube Video Manager** is a high-performance, desktop-based YouTube media manager and archive tool built with Python and PySide6. It provides a premium, modular interface for downloading videos, extracting high-quality transcripts, and managing a permanent local library.

## 🚀 Key Features

- **Smart Downloader**: Fetch videos in up to 1080p with selectable audio tracks and formats.
- **Transcript Extraction**: Download subtitles/captions (manual or auto-generated) as `.srt` files for analysis or accessibility.
- **Library Explorer**: A dedicated management tab with:
  - Native video playback integration.
  - Real-time library statistics (Videos count, Storage usage, SRT coverage).
  - Secure deletion of files and history records.
- **Dual Themes**: Seamlessly switch between **Dark Mode** and **Modern Light Mode** (`Ctrl+L`).
- **Menu Bar & Shortcuts**: Full keyboard control for power users (Fetch: `Ctrl+F`, Download: `Ctrl+D`, etc.).
- **Robust Persistence**: Local JSON-based diary ensures your download history is never lost.

## 🛠️ Installation & Setup

This project is optimized for [uv](https://github.com/astral-sh/uv).

### Prerequisites

- Python 3.12+
- Windows (Optimized for Win 10/11)
- `uv` installed (`pip install uv`)

### Quick Start

1. **Clone the repository**:
   ```powershell
   git clone https://github.com/ajendrasharma/Utility-YT-Video-Manager.git
   cd Utility-YT-Video-Manager
   ```
2. **Setup virtual environment & sync dependencies**:
   ```powershell
   uv sync
   ```
3. **Run the application**:
   ```powershell
   uv run yt
   ```

## ⌨️ Shortcuts

| Action                  | Shortcut   |
| :---------------------- | :--------- |
| **Fetch Metadata**      | `Ctrl + F` |
| **Download Video**      | `Ctrl + D` |
| **Download Transcript** | `Ctrl + T` |
| **Toggle Theme**        | `Ctrl + L` |
| **Refresh Library**     | `F5`       |
| **Exit**                | `Ctrl + Q` |

## 📦 Deployment (Build .exe)

Generate a standalone Windows executable without requiring Python on the target machine:

```powershell
uv run python deployment/build_exe.py
```

Output located at: `deployment/dist/Utility_YT_Video_Manager.exe`.

## 🧪 Development

### Project Structure

```text
src/yt/
├── main.py            # Main entry point & Window orchestration
├── workers.py         # Threaded download & thumbnail logic
├── diary.py           # Database (JSON) & File resolution logic
└── ui/
    └── explorer_tab.py # Dedicated Library management widget
```

### Running Tests

```powershell
uv run pytest
```

## 📄 License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.
