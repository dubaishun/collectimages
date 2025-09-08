# 🖼️ Web Image Scraper

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

A powerful Python GUI tool for scraping images from web pages with intelligent image recognition and batch downloading capabilities.

## ✨ Features

- 🎯 **Smart Image Detection** - Automatically identifies valid images and filters out ads/icons
- 📱 **Intuitive GUI** - User-friendly tkinter-based interface
- 🔄 **Sequential Download** - Downloads images in the exact order they appear on the webpage
- 👀 **Image Preview** - Click any image in the list to preview it
- 📊 **Progress Monitoring** - Real-time progress tracking for scraping and downloading
- 🔍 **Advanced Filtering** - Supports multiple image formats and dynamic loading
- 📝 **Detailed Logging** - Complete operation logs and error reporting
- 🎨 **Centered Window** - Auto-centers on screen startup

## 🚀 Quick Start

### Requirements

- Windows 10/11
- Python 3.7+

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/web-image-scraper.git
cd web-image-scraper
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the application
```bash
python image_scraper.py
```

### Usage

1. Enter the webpage URL in the input field
2. Click "Fetch Images" to analyze the webpage
3. Select download folder
4. Click "Download All Images in Order" to start batch download

## 🔧 Core Technologies

- **GUI Framework**: tkinter
- **HTTP Requests**: requests
- **HTML Parsing**: BeautifulSoup4
- **Image Processing**: Pillow
- **Multi-threading**: threading

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Suguang Network Software Development**
- Website: [suguang.cc](https://suguang.cc)

---

⭐ If this project helps you, please consider giving it a star!