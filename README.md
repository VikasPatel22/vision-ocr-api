# vision-ocr-api

> **Extract structured JSON from any image — receipts, ID cards, tables, or generic text — powered by Cloudflare AI Vision or Anthropic Claude.**

A FastAPI service with two backends: Cloudflare AI (free tier) or Anthropic Claude as fallback. Upload an image, get clean structured JSON back.

---

## Features

- **4 extraction modes** — receipt, id_card, table, generic
- **Dual AI backend** — Cloudflare AI (free) or Anthropic Claude fallback
- **Pydantic validation** — AI output is typed and validated before response
- **URL support** — pass a public image URL instead of uploading
- **OpenAPI docs** — auto-generated Swagger UI at `/docs`
- **Dockerized** — one command to run anywhere

---

## Quick Start

```bash
git clone https://github.com/VikasPatel22/vision-ocr-api
cd vision-ocr-api

# Copy and fill env vars
cp .env.example .env

# Run with Docker
docker build -t vision-ocr-api .
docker run -p 8000:8000 --env-file .env vision-ocr-api

# Or with Python directly
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs` for the interactive API.

---

## Usage

```bash
# Extract receipt data
curl -X POST http://localhost:8000/extract \
  -F "file=@receipt.jpg" \
  -F "mode=receipt"

# Extract from URL
curl "http://localhost:8000/extract/url?image_url=https://example.com/receipt.jpg&mode=receipt"
```

### Example Response (receipt mode)

```json
{
  "mode": "receipt",
  "filename": "receipt.jpg",
  "structured": {
    "merchant": "Reliance Fresh",
    "date": "2024-03-15",
    "items": [
      {"name": "Milk 1L", "qty": 2, "price": "56.00"},
      {"name": "Bread", "qty": 1, "price": "35.00"}
    ],
    "subtotal": "147.00",
    "tax": "0.00",
    "total": "147.00",
    "payment_method": "UPI"
  },
  "model_used": "@cf/llava-1.5-7b-hf"
}
```

---

## Extraction Modes

| Mode | Extracts |
|------|----------|
| `receipt` | merchant, date, line items, totals, payment method |
| `id_card` | name, DOB, ID number, expiry, nationality |
| `table` | headers array + rows array |
| `generic` | raw text, key-value pairs, summary |

---

## Environment Variables

```env
CF_ACCOUNT_ID=your_cloudflare_account_id
CF_API_TOKEN=your_cloudflare_api_token
ANTHROPIC_API_KEY=sk-ant-...   # fallback if CF not set
```

---

## File Structure

```
vision-ocr-api/
├── app/
│   ├── main.py            # FastAPI app, /extract endpoints
│   ├── vision.py          # CF AI / Anthropic caller
│   ├── schemas.py         # Pydantic models
│   └── prompts.py         # Mode-specific extraction prompts
├── examples/
│   ├── receipt.jpg
│   └── table.png
├── Dockerfile
└── README.md
```

---

## License

MIT © Vikas Patel
