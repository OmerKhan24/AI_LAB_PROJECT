# 🐍 Snakes and Ladders with AI Bots & Power-Ups 🎲

This is a Python-based version of the classic **Snakes and Ladders** game, enhanced with:
- 🧠 AI-controlled players (bots)
- ⚡ Power-up tiles (shield, double move, teleport)
- 🎵 Sound effects
- 🎮 Smooth animations using threading
- 🖥️ Fullscreen support and a clean UI with Tkinter

---

## 🎥 Project Demo Video & Media Folders

Due to GitHub's 100MB per-file size restriction, some files are hosted externally on Google Drive:

📺 **Video Demo:**  
[👉 Click here to watch the video demo](https://drive.google.com/file/d/1OsmpjQ0sc4m11NvfGzMZI3jSiak4FMuO/view?usp=drive_link)

🖼️ **Image-Heavy Folders:**  
The following folders contain many tile screenshots and were also moved to Drive:
- `bluepiecesontile`
- `redpiecesontile`
- `bothPiecesOnTile`
- `noPiecesOnTile`
- `assets/sounds` (if applicable)

📂 **Download all missing media here:**  
[🔗 Click here to access folders on Google Drive](https://drive.google.com/drive/folders/1Y86wH-Q-T35hUNonYFIFjBZ4SlPFUphk?usp=drive_link)

> 💡 All critical assets required to run the game are still included in this repository.

---

## 💡 Features

- Select 2 to 4 players (mix of human and AI)
- Automatic turns for AI players
- Power-ups:
  - Tile 15 – 🛡️ Shield (protects from snakes)
  - Tile 45 – 🚀 Double Move
  - Tile 75 – ✨ Teleport
- Audio feedback for dice rolls and win events
- Fullscreen toggle with `F`, exit with `Esc`
- Clean restart and exit functionality

---

## 👥 Team Members

- **Muhammad Omer Khan (22K-4418)** – AI logic, dice control, player movement, threading
- **Muhib Siddiqui (22K-4428)** – GUI design, canvas rendering, sound integration
- **Salik Ahmed (22K-4403)** – Power-up mechanics, tile logic, game flow improvements

---

## 🛠️ Requirements

- Python 3.10+
- `pygame` for sound
- `tkinter` (usually pre-installed with Python)

---

## 🚀 How to Run

```bash
pip install pygame
python snakeAndLadder.py
