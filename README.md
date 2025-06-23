# 📊 Crypto MCP Server

This project is a custom **MCP (Model-Context-Protocol) Server** built to analyze recent **YouTube videos about cryptocurrencies** using Youtube API and provide structured insights on public sentiment, engagement, and trends.

---

## 🔧 Features

- Pulls recent YouTube videos for any given crypto symbol (e.g., BTC, ETH, XRP)
- Filters to show only:
  - Videos published in the last **2 weeks**
  - **English-language** content (`defaultAudioLanguage`)
  - **Long-form videos** (5+ minutes)
- Sorts videos by **highest view count**
- Returns results in clean **Markdown format**
- Easily pluggable into Claude or Cursor using `FastMCP`

---

## 📦 Requirements

- Python 3.10+
- httpx
- python-dotenv

To install dependencies, copy and paste the command below in your virtual environment
```bash
pip install httpx python-dotenv
```

---

## 🔑 .env File

Create a `.env` file with your YouTube Data API v3 key:

```.env
YOUTUBE_API_KEY=your_api_key_here
```

Get your key from: https://console.cloud.google.com/apis/library/youtube.googleapis.com

---

## Running the MCP Server (sample outputs)

# Claude
<img width="1419" alt="Screenshot 2025-06-23 at 12 06 57" src="https://github.com/user-attachments/assets/a453b2cf-b48b-40d5-8936-48ed1a7e5ab1" />

<img width="1287" alt="Screenshot 2025-06-23 at 12 07 16" src="https://github.com/user-attachments/assets/b828e5ea-6566-4a18-9906-0188179edf8b" />

# Cursor
<img width="1561" alt="Screenshot 2025-06-23 at 11 58 37" src="https://github.com/user-attachments/assets/aee191a2-96ab-4a59-a782-94f5aa202eea" />

<img width="1561" alt="Screenshot 2025-06-23 at 11 58 44" src="https://github.com/user-attachments/assets/702a802e-bced-4b3b-8477-f9b17623db25" />










