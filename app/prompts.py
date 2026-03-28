"""Mode-specific prompts for structured data extraction."""

PROMPTS = {
    "receipt": """You are an OCR assistant. Extract ALL data from this receipt image.
Return ONLY valid JSON with this exact structure:
{
  "merchant": "store name",
  "date": "YYYY-MM-DD",
  "items": [{"name": "item", "qty": 1, "price": "0.00"}],
  "subtotal": "0.00",
  "tax": "0.00",
  "total": "0.00",
  "payment_method": "cash/card/upi"
}
Use null for any field you cannot read. No markdown, no explanation — JSON only.""",

    "id_card": """You are an OCR assistant. Extract data from this ID card / document image.
Return ONLY valid JSON with this exact structure:
{
  "full_name": "Name",
  "date_of_birth": "YYYY-MM-DD",
  "id_number": "ID",
  "expiry": "YYYY-MM-DD",
  "nationality": "Country",
  "address": "Address if visible"
}
Use null for fields you cannot read. No markdown — JSON only.""",

    "table": """You are an OCR assistant. Extract the table from this image.
Return ONLY valid JSON with this structure:
{
  "headers": ["col1", "col2", "col3"],
  "rows": [
    ["val1", "val2", "val3"],
    ["val1", "val2", "val3"]
  ]
}
If multiple tables exist, return the largest one. No markdown — JSON only.""",

    "generic": """You are an OCR assistant. Extract all text and key-value pairs from this image.
Return ONLY valid JSON:
{
  "raw_text": "all visible text here",
  "key_value_pairs": {"label": "value"},
  "lists": ["item1", "item2"],
  "summary": "one sentence description of the document"
}
No markdown — JSON only.""",
}


def get_prompt(mode: str) -> str:
    return PROMPTS.get(mode, PROMPTS["generic"])
