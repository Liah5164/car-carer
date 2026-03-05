"""Document extraction using Gemini Flash 2.0 via OpenRouter."""

import json
import base64
from pathlib import Path

import httpx
import fitz  # PyMuPDF

from app.config import settings

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemini-flash-2.0"

INVOICE_PROMPT = """Analyse cette facture ou ce devis d'entretien automobile.
Extrais les informations suivantes au format JSON strict :

{
  "doc_type": "invoice" ou "quote",
  "date": "YYYY-MM-DD",
  "mileage": nombre ou null,
  "garage_name": "string ou null",
  "total_cost": nombre ou null,
  "items": [
    {
      "description": "description du travail",
      "category": "une parmi: moteur, freinage, direction, suspension, transmission, echappement, electricite, carrosserie, climatisation, pneus, vidange, filtres, distribution, embrayage, autre",
      "part_name": "nom de la piece ou null",
      "quantity": nombre ou null,
      "unit_price": nombre ou null,
      "labor_cost": nombre ou null,
      "total_price": nombre ou null
    }
  ],
  "notes": "remarques generales ou null"
}

IMPORTANT :
- Les montants sont en euros
- Si une information n'est pas visible, mets null
- Categorise chaque ligne de travail
- Retourne UNIQUEMENT le JSON, sans markdown ni commentaire"""

CT_PROMPT = """Analyse ce proces-verbal de controle technique automobile.
Extrais les informations suivantes au format JSON strict :

{
  "date": "YYYY-MM-DD",
  "mileage": nombre ou null,
  "center_name": "nom du centre ou null",
  "result": "favorable" ou "defavorable" ou "contre_visite",
  "next_due_date": "YYYY-MM-DD ou null",
  "defects": [
    {
      "code": "code du defaut (ex: 1.1.1.a.1) ou null",
      "description": "description du defaut",
      "severity": "mineur" ou "majeur" ou "critique" ou "a_surveiller",
      "category": "categorie generale (direction, freinage, visibilite, eclairage, liaison_sol, structure, equipements, pollution, identification)"
    }
  ],
  "notes": "remarques generales ou null"
}

IMPORTANT :
- "a_surveiller" correspond aux points a controler lors du prochain CT
- Si pas de defauts, retourne une liste vide
- Retourne UNIQUEMENT le JSON, sans markdown ni commentaire"""


def _pdf_to_images(file_path: str) -> list[bytes]:
    """Convert PDF pages to PNG images."""
    doc = fitz.open(file_path)
    images = []
    for page in doc:
        pix = page.get_pixmap(dpi=200)
        images.append(pix.tobytes("png"))
    doc.close()
    return images


def _read_image(file_path: str) -> bytes:
    return Path(file_path).read_bytes()


def _detect_mime(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    return {
        ".pdf": "application/pdf",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }.get(ext, "application/octet-stream")


def _build_image_content(file_path: str) -> list[dict]:
    """Build OpenAI-compatible image_url content parts."""
    mime = _detect_mime(file_path)
    is_pdf = mime == "application/pdf"

    parts = []
    if is_pdf:
        images = _pdf_to_images(file_path)
        for img_bytes in images:
            b64 = base64.b64encode(img_bytes).decode()
            parts.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{b64}"},
            })
    else:
        img_bytes = _read_image(file_path)
        b64 = base64.b64encode(img_bytes).decode()
        parts.append({
            "type": "image_url",
            "image_url": {"url": f"data:{mime};base64,{b64}"},
        })
    return parts


def _call_openrouter(image_parts: list[dict], prompt: str) -> str:
    """Call OpenRouter with image + text prompt, return text response."""
    content = image_parts + [{"type": "text", "text": prompt}]

    resp = httpx.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": content}],
            "max_tokens": 4096,
        },
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


async def extract_document(file_path: str, doc_type_hint: str = "auto") -> dict:
    """Extract structured data from a document using Gemini Flash 2.0 via OpenRouter.

    Args:
        file_path: Path to the uploaded file (PDF or image)
        doc_type_hint: "invoice", "ct_report", "quote", or "auto"

    Returns:
        Extracted structured data as dict
    """
    image_parts = _build_image_content(file_path)

    # Choose prompt based on hint or try auto-detection
    if doc_type_hint == "ct_report":
        prompt = CT_PROMPT
    elif doc_type_hint in ("invoice", "quote"):
        prompt = INVOICE_PROMPT
    else:
        detected = _call_openrouter(
            image_parts,
            "Ce document est-il un controle technique (CT) ou une facture/devis d'entretien ? Reponds UNIQUEMENT par 'ct' ou 'facture'.",
        ).strip().lower()
        prompt = CT_PROMPT if "ct" in detected else INVOICE_PROMPT

    raw_text = _call_openrouter(image_parts, prompt).strip()

    # Clean potential markdown wrapping
    if raw_text.startswith("```"):
        raw_text = raw_text.split("\n", 1)[1] if "\n" in raw_text else raw_text[3:]
    if raw_text.endswith("```"):
        raw_text = raw_text[:-3]
    raw_text = raw_text.strip()

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        return {"error": "Failed to parse extraction result", "raw": raw_text}

    return data
