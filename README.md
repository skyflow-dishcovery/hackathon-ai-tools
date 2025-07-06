# 🎙️ WhisperProxy – Voice to English Transcription API

This project is a lightweight FastAPI server that receives voice audio (in any language), transcribes it using Groq's Whisper model, and then translates the text into English using a Groq-hosted LLM (LLaMA 3, Mistral, etc.).

Perfect for building multilingual AI agents that always receive English input.

---

## 📦 Features

- 🎧 Transcribe audio using `whisper-large-v3-turbo` (Groq API)
- 🌍 Translate transcribed text into English via LLM
- ⚡ Built for hackathon-speed performance (Groq GPU-accelerated)
- 🌐 Simple `/transcribe` HTTP endpoint
- 🚀 FastAPI + async file handling

## 💻 Installation (Windows)
# 1. Create Virtual Environment
```bash
python -m venv venv
.\venv\Scripts\activate
```

# 2. Install Dependencies
```bash
pip install -r requirements.txt
```

If requirements.txt doesn't exist, install manually:
```bash
pip install fastapi uvicorn aiofiles groq
```

# 3. Set Up API Key (Groq)
You must export your Groq API key as an environment variable.

```powershell
$Env:GROQ_API_KEY="gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```
Get your key at: https://console.groq.com/keys

# 4. Run the Server
```bash
uvicorn main:app --reload --port 8001
```

## Usage
Send a POST request to:
```yaml
POST /transcribe
Form-Data:
  file: your-audio.mp3 / .wav / .ogg
```
## Response:
```json
{
  "text": "I would like to order three Cokes and a jollof rice at 7 PM."
}
```

## 📌 Notes
- Only supports single-file uploads at /transcribe
- Audio should be ≤ 25MB
- Translates any spoken language to English
- You can replace the LLM model or change the behavior in main.py
