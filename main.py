from fastapi import FastAPI, UploadFile, File
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware

from PIL import Image
import requests
import io
import os
import base64

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HF_TOKEN = os.getenv("HF_TOKEN")

@app.get("/")
def home():
    return {
        "status": "MusicXML AI Backend Running"
    }

@app.post("/convert")
async def convert(file: UploadFile = File(...)):

    contents = await file.read()

    image = Image.open(io.BytesIO(contents)).convert("RGB")

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")

    image_bytes = buffer.getvalue()

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}"
    }

    # Example AI vision model
    response = requests.post(
        "https://api-inference.huggingface.co/models/microsoft/trocr-base-printed",
        headers=headers,
        data=image_bytes
    )

    ai_result = response.text

    musicxml = f"""<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="3.1">

  <work>
    <work-title>AI Recognition Result</work-title>
  </work>

  <identification>
    <creator type="composer">
      {ai_result[:200]}
    </creator>
  </identification>

  <part-list>
    <score-part id="P1">
      <part-name>Piano</part-name>
    </score-part>
  </part-list>

  <part id="P1">
    <measure number="1">

      <attributes>
        <divisions>1</divisions>

        <key>
          <fifths>0</fifths>
        </key>

        <time>
          <beats>4</beats>
          <beat-type>4</beat-type>
        </time>

        <clef>
          <sign>G</sign>
          <line>2</line>
        </clef>

      </attributes>

      <note>
        <pitch>
          <step>C</step>
          <octave>4</octave>
        </pitch>

        <duration>1</duration>
        <type>quarter</type>
      </note>

    </measure>
  </part>

</score-partwise>
"""

    return PlainTextResponse(
        content=musicxml,
        media_type="application/xml"
    )