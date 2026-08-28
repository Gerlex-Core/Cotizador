"""
Digicorp API Router - Handles web scraping, text parsing, and product extraction from digicorp.com.bo
"""

import re
import html
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import urllib.request
import urllib.parse
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

router = APIRouter(prefix="/api/digicorp", tags=["Digicorp"])


class ScrapeUrlPayload(BaseModel):
    url: str


class ParseTextPayload(BaseModel):
    text: str


def clean_text(val: str) -> str:
    if not val:
        return ""
    val = re.sub(r'<[^>]+>', ' ', val)
    val = html.unescape(val)
    return re.sub(r'\s+', ' ', val).strip()


@router.post("/parse-text")
def parse_digicorp_text(payload: ParseTextPayload) -> Dict[str, Any]:
    """
    Intelligently parse product details copied from Digicorp product page text.
    Handles multi-line prices with integer & cents:
    46
    00
    Bs

    33
    70
    Bs
    - 26.7%
    """
    raw_text = payload.text or ""
    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="El texto proporcionado está vacío.")

    code = ""
    brand = ""
    description = ""
    price = 0.0
    discount_percent = 0.0
    warranty = ""

    # ALWAYS extract Código: (e.g. Código:DH-PFM920-5EU-black or Código:SP066)
    # Ignore internal Digicorp numerical SKU (e.g. SKU:1.0.99.50.10420)
    code_match = re.search(r'C[óo]digo\s*:\s*([^\s\n]+)', raw_text, re.IGNORECASE)
    if code_match:
        code = code_match.group(1).strip()
    sku = code

    # Extract Warranty
    warranty_match = re.search(r'Garant[íi]a\s*\n?\s*(\d+\s*d[íi]a\(s\)?|\d+\s*a[ñn]os?)', raw_text, re.IGNORECASE)
    if warranty_match:
        warranty = warranty_match.group(1).strip()

    # Extract Discount Percentage (e.g. - 26.7%)
    disc_match = re.search(r'-\s*(\d+(?:\.\d+)?)\s*%', raw_text)
    if disc_match:
        try:
            discount_percent = float(disc_match.group(1))
        except ValueError:
            discount_percent = 0.0

    # Extract Prices using line-by-line context
    found_prices = []
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]

    for i, line in enumerate(lines):
        clean_line = line.upper()
        if clean_line == 'BS' or clean_line.endswith(' BS') or clean_line.startswith('BS '):
            prev1 = lines[i-1] if i > 0 else ""
            prev2 = lines[i-2] if i > 1 else ""

            # Case 1: prev1 is "00" or "70" (2 digits cents) and prev2 is integer (e.g. 46 \n 00 \n Bs)
            if re.match(r'^\d{2}$', prev1) and re.match(r'^\d+$', prev2):
                try:
                    val = float(f"{prev2}.{prev1}")
                    found_prices.append(val)
                    continue
                except ValueError:
                    pass

            # Case 2: prev1 has thousand dot format (e.g. 1.475 \n Bs -> 1475.0)
            if re.match(r'^\d{1,3}\.\d{3}$', prev1):
                try:
                    val = float(prev1.replace('.', ''))
                    found_prices.append(val)
                    continue
                except ValueError:
                    pass

            # Case 3: prev1 has explicit decimal comma/dot (e.g. 33.70 or 1.475,50)
            if re.match(r'^\d+\.\d{1,2}$', prev1) or re.match(r'^\d+,\d{1,2}$', prev1):
                try:
                    val = float(prev1.replace(',', '.'))
                    found_prices.append(val)
                    continue
                except ValueError:
                    pass

            # Case 4: prev1 is plain integer (e.g. 215 \n Bs -> 215.0)
            if re.match(r'^\d+$', prev1):
                try:
                    val = float(prev1)
                    found_prices.append(val)
                    continue
                except ValueError:
                    pass

            # Case 5: line itself contains number and Bs (e.g. "215 Bs" or "1.475 Bs")
            num_match = re.search(r'(\d+(?:[\.,]\d+)?)', line)
            if num_match:
                s = num_match.group(1)
                try:
                    if re.match(r'^\d{1,3}\.\d{3}$', s):
                        val = float(s.replace('.', ''))
                    else:
                        val = float(s.replace(',', '.'))
                    found_prices.append(val)
                except ValueError:
                    pass

    if found_prices:
        # Take the bottom/last price (discounted offer price if multiple exist)
        price = found_prices[-1]

    # Dynamic Brand Extraction (no static brand lists)
    brand_match = re.search(r'Marca\s*:\s*([^\n]+)', raw_text, re.IGNORECASE)
    if brand_match:
        brand = brand_match.group(1).strip()
    else:
        # Digicorp layout prints brand on line right before "Descripción del Producto"
        before_desc_match = re.search(r'([A-Za-z0-9_\-\.]{2,30})\s*\n\s*Descripci[óo]n del Producto', raw_text, re.IGNORECASE)
        if before_desc_match:
            brand = before_desc_match.group(1).strip()
        elif code and '-' in code:
            parts = code.split('-')
            if len(parts) > 1 and parts[-1].isalpha() and len(parts[-1]) >= 3:
                brand = parts[-1].upper()

    # Extract Description
    desc_match = re.search(r'Descripci[óo]n del Producto\s*\n?\s*([^\n]+)', raw_text, re.IGNORECASE)
    if desc_match:
        description = desc_match.group(1).strip()
    else:
        detalles_match = re.search(r'detalles\s*:\s*([^\n]+)', raw_text, re.IGNORECASE)
        if detalles_match:
            description = detalles_match.group(1).strip()
        else:
            lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
            for line in lines:
                if not line.startswith("http") and not line.startswith("Código") and not line.startswith("SKU") and "Bs" not in line and "Garantía" not in line and not line.startswith("-"):
                    description = line
                    break

    return {
        "status": "success",
        "product": {
            "description": description or "Producto Digicorp",
            "brand": brand,
            "sku": sku or code,
            "price": price,
            "discount_percent": discount_percent,
            "unit": "unidad (u)",
            "warranty": warranty or "1 Año"
        }
    }


@router.post("/scrape-url")
def scrape_digicorp_url(payload: ScrapeUrlPayload) -> Dict[str, Any]:
    """
    Fetch and parse a Digicorp product page URL (e.g. https://digicorp.com.bo/producto/SF106P-45-imou).
    Extracts title, code, brand, price and description.
    """
    url = payload.url.strip()
    if not url.startswith("http"):
        url = "https://" + url

    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'es-ES,es;q=0.9'
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"No se pudo acceder a la URL de Digicorp: {str(e)}")

    # Extract title/description
    title = ""
    if BeautifulSoup:
        soup = BeautifulSoup(html_content, 'html.parser')
        title_el = soup.find('h1') or soup.find('h2') or soup.find(class_=re.compile(r'title|product-name', re.I))
        if title_el:
            title = clean_text(title_el.text)

    if not title:
        h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', html_content, re.IGNORECASE | re.DOTALL)
        if h1_match:
            title = clean_text(h1_match.group(1))

    # Extract price
    price = 0.0
    text_content = clean_text(html_content)
    price_match = re.search(r'(\d+(?:\.\d+)?)\s*Bs', text_content, re.IGNORECASE)
    if price_match:
        try:
            price = float(price_match.group(1))
        except ValueError:
            price = 0.0

    # Extract code / SKU from URL if present (e.g. /producto/SF106P-45-imou -> SF106P-45-imou)
    sku = ""
    url_code_match = re.search(r'/producto/([^\?/#]+)', url)
    if url_code_match:
        sku = url_code_match.group(1)

    # Dynamic brand extraction from SKU or page content (no static brand list)
    brand = ""
    brand_match = re.search(r'Marca\s*:\s*([^\n<]+)', html_content, re.IGNORECASE)
    if brand_match:
        brand = clean_text(brand_match.group(1))
    elif sku and '-' in sku:
        parts = sku.split('-')
        if len(parts) > 1 and parts[-1].isalpha() and len(parts[-1]) >= 3:
            brand = parts[-1].upper()

    return {
        "status": "success",
        "product": {
            "description": title or f"Producto Digicorp ({sku})",
            "brand": brand,
            "sku": sku,
            "price": price,
            "unit": "unidad (u)",
            "warranty": "1 Año"
        }
    }
