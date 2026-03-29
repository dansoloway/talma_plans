"""Smoke tests for compilation against the bundled workbook."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from talma_plans.compile_tasks import (
    compile_all_task_sheets,
    focus_area_filter_choices,
    tasks_per_focus_group,
)


def test_compile_data_xlsx_has_normalized_focus_columns() -> None:
    root = Path(__file__).resolve().parent.parent
    path = root / "data.xlsx"
    df = compile_all_task_sheets(path)
    for col in ("focus_area_raw", "focus_area_1", "focus_area_2", "focus_area_combo"):
        assert col in df.columns
    assert len(df) > 0
    choices = focus_area_filter_choices(df)
    assert len(choices) > 0
    # Filter matches slot 1 or 2
    pick = choices[0]
    m = (df["focus_area_1"] == pick) | (df["focus_area_2"] == pick)
    assert m.any()


def test_tasks_per_focus_group() -> None:
    summary = tasks_per_focus_group(
        pd.DataFrame({"focus_area_combo": ["Alumni", "Alumni", "Full Year | PD", None]}),
    )
    assert set(summary["focus_group"]) == {"Alumni", "Full Year | PD", "(Unassigned)"}
    by_name = summary.set_index("focus_group")["tasks"].to_dict()
    assert by_name["Alumni"] == 2
    assert by_name["Full Year | PD"] == 1
    assert by_name["(Unassigned)"] == 1
