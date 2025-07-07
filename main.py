# main.py  –  turbo_LLM‑translate version
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from groq import Groq
import aiofiles, os, json
from tempfile import mkstemp

app = FastAPI(title="WhisperProxy")

client = Groq()                             # reads GROQ_API_KEY
ASR_MODEL   = "whisper-large-v3-turbo"      # fastest speech model -> (transcribes fast in the original language.)
LLM_MODEL   = "llama3-8b-8192"              # or "mixtral-8x7b" etc. -> (converts that text to English.)
CATEGORIES = ["airline", "hotel", "restaurant", "delivery"]

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    # (1) create temp file path
    suffix = os.path.splitext(file.filename)[1]
    fd, tmp_path = mkstemp(suffix=suffix)
    os.close(fd)

    # (2) write upload asynchronously
    async with aiofiles.open(tmp_path, "wb") as out:
        await out.write(await file.read())

    try:
        # (3) turbo transcription (source language)
        with open(tmp_path, "rb") as audio:
            asr = client.audio.transcriptions.create(
                file=audio,
                model=ASR_MODEL,
                response_format="json",
            )

        # (4) translate transcription to English via LLM
        translator_response = client.chat.completions.create(
            model=LLM_MODEL,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": "Translate to concise English.",
                },
                {"role": "user", "content": asr.text},
            ],
        )
        english_text = translator_response.choices[0].message.content.strip()

        # (5) classify into one of 4 categories ONLY
        classify_prompt = (
            "You are a router that must output JSON ONLY. "
            f"Allowed categories: {', '.join(CATEGORIES)}. "
            "Decide which category the user's sentence belongs to and return: "
            '{"category":"<one of the categories>"}.'
            "Respond with nothing else."
        )
        cat_raw = client.chat.completions.create(
            model=LLM_MODEL, temperature=0, max_tokens=20,
            messages=[
                {"role":"system","content": classify_prompt},
                {"role":"user","content": english_text}
            ]
        ).choices[0].message.content.strip()
        cat_json = json.loads(cat_raw)
        category = cat_json.get("category", "unknown")

    finally:
        # (6) clean up temp file
        os.remove(tmp_path)

    # (7) return always‑English text with it's category
    return JSONResponse({"text": english_text, "category": category})