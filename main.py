# main.py  –  turbo + LLM‑translate version
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from groq import Groq
import aiofiles, os
from tempfile import mkstemp

app = FastAPI(title="WhisperProxy")

client = Groq()                             # reads GROQ_API_KEY
ASR_MODEL   = "whisper-large-v3-turbo"      # fastest speech model -> (transcribes fast in the original language.)
LLM_MODEL   = "llama3-8b-8192"              # or "mixtral-8x7b" etc. -> (converts that text to English.)

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    # 1️⃣ create temp file path
    suffix = os.path.splitext(file.filename)[1]
    fd, tmp_path = mkstemp(suffix=suffix)
    os.close(fd)

    # 2️⃣ write upload asynchronously
    async with aiofiles.open(tmp_path, "wb") as out:
        await out.write(await file.read())

    try:
        # 3️⃣ turbo transcription (source language)
        with open(tmp_path, "rb") as audio:
            asr = client.audio.transcriptions.create(
                file=audio,
                model=ASR_MODEL,
                response_format="json",
            )

        # 4️⃣ translate transcription to English via LLM
        chat = client.chat.completions.create(
            model=LLM_MODEL,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional translator. "
                        "Translate the user's message into clear, concise English. "
                        "Preserve numbers, product names, and proper nouns. "
                    ),
                },
                {"role": "user", "content": asr.text},
            ],
        )
        english_text = chat.choices[0].message.content.strip()

    finally:
        # 5️⃣ clean up temp file
        os.remove(tmp_path)

    # 6️⃣ return always‑English text
    return JSONResponse({"text": english_text})