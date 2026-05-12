from fastapi import FastAPI, UploadFile, File
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware

from PIL import Image
import easyocr
import numpy as np
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

reader = easyocr.Reader(['en'])

@app.get("/")
def home():
    return {
        "status": "MusicXML AI Backend Running"
    }

@app.post("/convert")
async def convert(file: UploadFile = File(...)):

    contents = await file.read()

    image = Image.open(io.BytesIO(contents)).convert("RGB")

    image_np = np.array(image)

    # OCR detection
    results = reader.readtext(image_np)

    detected_text = []

    for r in results:
        detected_text.append(r[1])

    print("Detected:", detected_text)

    # TEMP fake XML still
    musicxml = f"""<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="3.1">

  <work>
    <work-title>{' '.join(detected_text)}</work-title>
  </work>

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