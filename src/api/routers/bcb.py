"""
Router de integración con el Banco Central de Bolivia (BCB - bcb.gob.bo)
Obtiene el Tipo de Cambio Oficial actualizado en tiempo real.
"""

import re
import urllib.request
from typing import Dict, Any
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/bcb", tags=["BCB"])

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


@router.get("/exchange-rate")
def get_bcb_exchange_rate() -> Dict[str, Any]:
    """
    Fetch the official exchange rate (Tipo de Cambio Oficial) live from https://www.bcb.gob.bo/
    """
    url = "https://www.bcb.gob.bo/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'es-ES,es;q=0.9'
    }
    
    req = urllib.request.Request(url, headers=headers)
    
    rate = 12.02
    date_str = ""
    fetched = False

    try:
        with urllib.request.urlopen(req, timeout=8) as response:
            html_content = response.read().decode('utf-8', errors='ignore')

        # Clean HTML text
        text_clean = ""
        if BeautifulSoup:
            soup = BeautifulSoup(html_content, 'html.parser')
            text_clean = soup.get_text(separator='\n')
        else:
            text_clean = re.sub(r'<[^>]+>', '\n', html_content)

        # Regex search for "Tipo de cambio oficial" or "Bolivianos por dólar estadounidense"
        tc_match = re.search(
            r'Tipo de cambio oficial[\s\S]*?(\d+[\.,]\d{2})',
            text_clean,
            re.IGNORECASE
        )
        if not tc_match:
            tc_match = re.search(
                r'Bolivianos por d[óo]lar estadounidense[\s\S]*?(\d+[\.,]\d{2})',
                text_clean,
                re.IGNORECASE
            )
        if not tc_match:
            tc_match = re.search(
                r'Valor Referencial del D[óo]lar[\s\S]*?(\d+[\.,]\d{2})',
                text_clean,
                re.IGNORECASE
            )

        if tc_match:
            raw_rate = tc_match.group(1).replace(',', '.')
            try:
                rate = float(raw_rate)
                fetched = True
            except ValueError:
                pass

        # Try to capture date string
        date_match = re.search(r'([A-ZÁÉÍÓÚÑa-zñáéíóú]+\s+\d+\s+de\s+[A-ZÁÉÍÓÚÑa-zñáéíóú]+\s*,\s*\d{4})', text_clean, re.IGNORECASE)
        if date_match:
            date_str = date_match.group(1).strip()

    except Exception as e:
        print("[BCB FETCH WARNING]", e)

    return {
        "status": "success",
        "exchange_rate": rate,
        "date": date_str,
        "fetched_online": fetched,
        "source": "Banco Central de Bolivia (bcb.gob.bo)"
    }
