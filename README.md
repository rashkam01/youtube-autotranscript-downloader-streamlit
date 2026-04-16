# YouTube Gujarati Transcript Extractor

A Streamlit app that fetches a Gujarati auto-transcript from any YouTube video
and exports it as a clean, readable PDF with configurable timestamps.

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
streamlit run app.py
```

The app opens in your browser at `http://localhost:8501`.

---

## How it works

1. **Paste a YouTube URL** (any format) or bare video ID.
2. Choose your **timestamp interval** (default 15 minutes).
3. Click **Extract Transcript**.
   - If a Gujarati transcript (`gu`) exists (manual or auto-generated), it is fetched.
   - Otherwise a clear error message is shown: *"Gujarati auto-transcript unavailable"*.
4. A live **preview** of the first few sections appears in the app.
5. Click **Download Gujarati Transcript PDF** to save the file.

---

## PDF layout

- **Title block** — video ID, URL, language code, timestamp interval.
- **Sections** — one per interval (e.g. every 15 min), headed by a blue `[MM:SS]`
  or `[HH:MM:SS]` timestamp.
- Clean `Helvetica` body text, A4 page size, generous margins.

---

## Dependencies

| Package | Purpose |
|---|---|
| `streamlit` | Web UI |
| `youtube-transcript-api` | Fetch transcripts from YouTube |
| `reportlab` | Generate PDF |

---

## Cloud deployment (optional)

Deploy for free on **Streamlit Community Cloud**:
1. Push the folder to a GitHub repo.
2. Go to <https://share.streamlit.io> → "New app" → select your repo.
3. Set `app.py` as the main file. Done!
