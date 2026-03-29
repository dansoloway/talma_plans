"""
Compile department task sheets from the workbook into one normalized dataframe.

Input: ``data.xlsx`` (or path you pass) is read only — focus areas are normalized
in-app; spreadsheet column order for pairs does not matter (see ``focus_areas``).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from talma_plans.focus_areas import parse_focus_areas

# Sheets whose first row is the task table header with a \"Focus Area\" column.
DEFAULT_TASK_SHEETS: tuple[str, ...] = (
    "Pedagogy",
    "Resources - USA",
    "Full Year",
    "Finance",
    "HR",
    "Resource - ISR",
    "Tech",
)

FOCUS_AREA_COLUMN = "Focus Area"


def _apply_focus_columns(df: pd.DataFrame, *, sheet_name: str | None = None) -> pd.DataFrame:
    out = df.copy()
    if FOCUS_AREA_COLUMN not in out.columns:
        out["focus_area_raw"] = None
        out["focus_area_1"] = None
        out["focus_area_2"] = None
        out["focus_area_combo"] = None
        return out

    def _parse(val: object, row_idx: int) -> dict[str, str | None]:
        ctx = f"sheet={sheet_name!s} dataframe_row={row_idx}"
        return parse_focus_areas(val, log_context=ctx)

    col = out[FOCUS_AREA_COLUMN]
    parsed_rows = [_parse(col.iloc[i], i) for i in range(len(col))]
    focus_expanded = pd.DataFrame(parsed_rows)
    for col in ["focus_area_raw", "focus_area_1", "focus_area_2", "focus_area_combo"]:
        if col in out.columns:
            out = out.drop(columns=[col])
    return pd.concat([out, focus_expanded], axis=1)


def compile_sheet(path: str | Path, sheet_name: str) -> pd.DataFrame:
    """Load one task sheet and add normalized focus area columns."""
    df = pd.read_excel(path, sheet_name=sheet_name)
    df["source_sheet"] = sheet_name
    return _apply_focus_columns(df, sheet_name=sheet_name)


def compile_all_task_sheets(
    path: str | Path,
    sheet_names: tuple[str, ...] | None = None,
) -> pd.DataFrame:
    """Load all configured task sheets and concatenate."""
    path = Path(path)
    names = sheet_names if sheet_names is not None else DEFAULT_TASK_SHEETS
    frames = [compile_sheet(path, name) for name in names]
    return pd.concat(frames, axis=0, ignore_index=True)


def load_compiled_tasks(
    path: str | Path | None = None,
    sheet_names: tuple[str, ...] | None = None,
) -> pd.DataFrame:
    """Default entry: compile tasks from ``data.xlsx`` next to the package root."""
    if path is None:
        path = Path(__file__).resolve().parent.parent / "data.xlsx"
    return compile_all_task_sheets(path, sheet_names=sheet_names)


def focus_area_filter_choices(df: pd.DataFrame) -> list[str]:
    """Distinct focus areas for UI filters (union of slot 1 and slot 2)."""
    vals = pd.concat(
        [df["focus_area_1"], df["focus_area_2"]],
        ignore_index=True,
    ).dropna()
    return sorted({str(v) for v in vals.unique()})


def tasks_per_focus_group(
    df: pd.DataFrame,
    *,
    unassigned_label: str = "(Unassigned)",
) -> pd.DataFrame:
    """
    Count tasks per normalized focus group (``focus_area_combo``).

    Each task appears in exactly one group: the deterministic combo from
    parsing, or ``unassigned_label`` when no focus areas were set.
    """
    if df.empty:
        return pd.DataFrame(columns=["focus_group", "tasks"])

    if "focus_area_combo" not in df.columns:
        series = pd.Series([pd.NA] * len(df), index=df.index, dtype=object)
    else:
        series = df["focus_area_combo"]

    labeled = series.fillna(unassigned_label).astype(str).replace("", unassigned_label)
    out = (
        labeled.value_counts()
        .rename_axis("focus_group")
        .reset_index(name="tasks")
        .sort_values(["tasks", "focus_group"], ascending=[False, True])
        .reset_index(drop=True)
    )
    return out


def tasks_per_focus_area_rollup(
    df: pd.DataFrame,
    *,
    unassigned_label: str = "(Unassigned)",
) -> pd.DataFrame:
    """
    Count how many tasks **touch** each distinct focus area (slot 1 or slot 2).

    A task with two different areas adds **one** to each area’s count, so the sum
    of ``tasks`` down the table can exceed the number of rows in ``df``. Tasks
    with no focus areas count once under ``unassigned_label``.
    """
    if df.empty:
        return pd.DataFrame(columns=["focus_area", "tasks"])

    fa1 = df["focus_area_1"] if "focus_area_1" in df.columns else pd.Series(pd.NA, index=df.index)
    fa2 = df["focus_area_2"] if "focus_area_2" in df.columns else pd.Series(pd.NA, index=df.index)

    records: list[str] = []
    for i in range(len(df)):
        areas: list[str] = []
        for v in (fa1.iloc[i], fa2.iloc[i]):
            if pd.notna(v):
                s = str(v).strip()
                if s and s not in areas:
                    areas.append(s)
        if not areas:
            records.append(unassigned_label)
        else:
            records.extend(areas)

    out = (
        pd.Series(records, dtype="string")
        .value_counts()
        .rename_axis("focus_area")
        .reset_index(name="tasks")
        .sort_values(["tasks", "focus_area"], ascending=[False, True])
        .reset_index(drop=True)
    )
    return out
