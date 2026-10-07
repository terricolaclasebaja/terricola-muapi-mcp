import os
import time
import requests
from typing import Optional
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

BASE = "https://api.muapi.ai/api/v1"
app = FastAPI(title="Terricola MuAPI Chain Bridge")

class ImageChain(BaseModel):
    source_request_id: str
    prompt: str
    model: str = "nano-banana-2-edit"
    aspect_ratio: str = "9:16"
    num_images: int = Field(1, ge=1, le=4)

def poll(request_id: str, key: str):
    headers = {"x-api-key": key}
    url = f"{BASE}/predictions/{request_id}/result"
    for _ in range(240):
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code not in (200, 201):
            raise HTTPException(r.status_code, r.text)
        data = r.json()
        if data.get("status") == "completed":
            return data
        if data.get("status") == "failed":
            raise HTTPException(502, data.get("error", "MuAPI task failed"))
        time.sleep(1)
    raise HTTPException(504, "MuAPI polling timeout")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chain/image-edit")
def chain_image_edit(req: ImageChain, x_api_key: Optional[str] = Header(None)):
    key = x_api_key or os.getenv("MUAPIAPP_API_KEY")
    if not key:
        raise HTTPException(401, "MuAPI API key required")

    previous = poll(req.source_request_id, key)
    outputs = previous.get("outputs") or []
    if not outputs:
        raise HTTPException(502, "Previous request has no output")

    source = outputs[0]
    if isinstance(source, dict):
        source = source.get("url")
    if not isinstance(source, str):
        raise HTTPException(502, "Previous output is not a URL")

    payload = {
        "prompt": req.prompt,
        "image_url": source,
        "aspect_ratio": req.aspect_ratio,
        "num_images": req.num_images,
    }
    r = requests.post(
        f"{BASE}/{req.model}",
        headers={"x-api-key": key, "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    if r.status_code not in (200, 201):
        raise HTTPException(r.status_code, r.text)
    submitted = r.json()
    new_id = submitted.get("request_id")
    if not new_id:
        raise HTTPException(502, "MuAPI returned no request_id")

    result = poll(new_id, key)
    return {
        "request_id": new_id,
        "status": result.get("status"),
        "outputs": result.get("outputs", []),
        "source_request_id": req.source_request_id,
    }
