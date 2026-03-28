"""
Vision OCR API — FastAPI service that extracts structured data from images
using Cloudflare AI's vision models. Supports receipts, ID cards, tables, and generic text.
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
import base64

from .vision import extract_from_image
from .schemas import ExtractionMode, ExtractionResult

app = FastAPI(
    title="Vision OCR API",
    description="Extract structured data from images using Cloudflare AI Vision.",
    version="1.0.0",
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/extract", response_model=ExtractionResult)
async def extract(
    file: UploadFile = File(..., description="Image file (JPEG, PNG, WebP)"),
    mode: ExtractionMode = Query(
        ExtractionMode.generic,
        description="Extraction mode: receipt | id_card | table | generic",
    ),
):
    """
    Upload an image and extract structured data from it.

    - **receipt** — line items, totals, merchant, date
    - **id_card** — name, DOB, ID number, expiry
    - **table** — rows and columns as JSON array
    - **generic** — raw text + key-value pairs
    """
    if file.content_type not in ("image/jpeg", "image/png", "image/webp"):
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported image type: {file.content_type}. Use JPEG, PNG, or WebP.",
        )

    image_bytes = await file.read()
    if len(image_bytes) > 10 * 1024 * 1024:  # 10 MB limit
        raise HTTPException(status_code=413, detail="Image too large (max 10 MB).")

    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    result = await extract_from_image(
        image_b64=image_b64,
        content_type=file.content_type,
        mode=mode,
        filename=file.filename or "upload",
    )
    return result


@app.post("/extract/url", response_model=ExtractionResult)
async def extract_from_url(
    image_url: str = Query(..., description="Public URL of the image"),
    mode: ExtractionMode = Query(ExtractionMode.generic),
):
    """Extract structured data from a public image URL."""
    import httpx
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(image_url)
            resp.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch image: {e}")

    image_b64 = base64.b64encode(resp.content).decode("utf-8")
    content_type = resp.headers.get("content-type", "image/jpeg").split(";")[0]

    result = await extract_from_image(
        image_b64=image_b64,
        content_type=content_type,
        mode=mode,
        filename="url_image",
    )
    return result
