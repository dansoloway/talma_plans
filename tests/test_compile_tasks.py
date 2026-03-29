"""Smoke tests for compilation against the bundled workbook."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from talma_plans.compile_tasks import (
    compile_all_task_sheets,
    filter_tasks_by_focus_group,
    focus_area_filter_choices,
    tasks_per_focus_area_rollup,
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


def test_tasks_per_focus_area_rollup_double_counts_two_slot_tasks() -> None:
    rollup = tasks_per_focus_area_rollup(
        pd.DataFrame(
            {
                "focus_area_1": ["Eval External", "Eval External", None],
                "focus_area_2": ["Full Year", "Merhavim", None],
            },
        ),
    )
    by_name = rollup.set_index("focus_area")["tasks"].to_dict()
    assert by_name["Eval External"] == 2
    assert by_name["Full Year"] == 1
    assert by_name["Merhavim"] == 1
    assert by_name["(Unassigned)"] == 1
    assert int(rollup["tasks"].sum()) == 5  # 2+1+1+1, not 3 tasks


def test_filter_tasks_by_focus_group_exact_pair_and_rollup() -> None:
    base = pd.DataFrame(
        {
            "focus_area_combo": ["A | B", "A | B", None],
            "focus_area_1": ["A", "A", None],
            "focus_area_2": ["B", "B", None],
            "source_sheet": ["Pedagogy", "Finance", "HR"],
            "Task Name": ["t1", "t2", "t3"],
        },
    )
    ex = filter_tasks_by_focus_group(base, mode="exact_pair", group_label="A | B")
    assert len(ex) == 2
    assert set(ex["source_sheet"]) == {"Pedagogy", "Finance"}
    un = filter_tasks_by_focus_group(base, mode="exact_pair", group_label="(Unassigned)")
    assert len(un) == 1
    assert un.iloc[0]["source_sheet"] == "HR"

    roll = filter_tasks_by_focus_group(base, mode="rollup_area", group_label="A")
    assert len(roll) == 2
