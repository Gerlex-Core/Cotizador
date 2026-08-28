"""
History API Router - Recent files and quotation history endpoints.
"""

from typing import List, Dict, Any
from fastapi import APIRouter

from ...logic.history.history_manager import HistoryManager

router = APIRouter(prefix="/api/history", tags=["History"])
history_manager = HistoryManager()


@router.get("/recent")
def get_recent_files() -> List[str]:
    """Get list of recent file paths."""
    return history_manager.get_recent()


@router.get("/full")
def get_full_history() -> List[Dict[str, Any]]:
    """Get detailed history items."""
    return history_manager.get_history()
