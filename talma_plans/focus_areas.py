"""
Focus area normalization.

The source Excel file is not modified. Comma-separated values in the spreadsheet
\"Focus Area\" column are split in Python, trimmed, deduplicated, and ordered
alphabetically so pairs like \"PD, Full Year\" and \"Full Year, PD\" share the
same focus_area_1 / focus_area_2 / focus_area_combo.
"""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


def parse_focus_areas(
    raw_value: Any,
    *,
    log_context: str | None = None,
) -> dict[str, str | None]:
    """
    Parse a spreadsheet \"Focus Area\" cell into normalized fields.

    **3+ values:** after splitting on commas, unique non-empty tokens are sorted
    alphabetically; a warning is logged including the raw cell text and optional
    ``log_context`` (e.g. sheet name + row); only the first two sorted values
    are kept as focus_area_1 and focus_area_2.
    """
    if raw_value is None:
        return {
            "focus_area_raw": None,
            "focus_area_1": None,
            "focus_area_2": None,
            "focus_area_combo": None,
        }

    try:
        if pd.isna(raw_value):
            return {
                "focus_area_raw": None,
                "focus_area_1": None,
                "focus_area_2": None,
                "focus_area_combo": None,
            }
    except TypeError:
        pass

    raw_str = str(raw_value).strip()
    if not raw_str or raw_str.lower() in ("nan", "<na>"):
        return {
            "focus_area_raw": None,
            "focus_area_1": None,
            "focus_area_2": None,
            "focus_area_combo": None,
        }

    parts = [part.strip() for part in raw_str.split(",")]
    parts = [part for part in parts if part]

    unique_parts = sorted(set(parts))

    if len(unique_parts) > 2:
        logger.warning(
            "More than 2 focus areas after split/dedupe; keeping first two "
            "alphabetically. raw=%r sorted_tokens=%s context=%s",
            raw_str,
            unique_parts,
            log_context or "",
        )
        unique_parts = unique_parts[:2]

    fa1 = unique_parts[0] if len(unique_parts) >= 1 else None
    fa2 = unique_parts[1] if len(unique_parts) >= 2 else None

    combo = " | ".join([p for p in [fa1, fa2] if p]) or None

    return {
        "focus_area_raw": raw_str,
        "focus_area_1": fa1,
        "focus_area_2": fa2,
        "focus_area_combo": combo,
    }
