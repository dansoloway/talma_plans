"""
Streamlit UI for browsing compiled TALMA tasks.

Focus area filters use normalized columns focus_area_1 / focus_area_2 only.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
import streamlit as st

from talma_plans.compile_tasks import (
    focus_area_filter_choices,
    load_compiled_tasks,
    tasks_per_focus_group,
)

logging.basicConfig(level=logging.INFO)


@st.cache_data(show_spinner=False)
def _get_tasks(data_path: str) -> pd.DataFrame:
    return load_compiled_tasks(Path(data_path))


def main() -> None:
    st.set_page_config(page_title="TALMA Plans", layout="wide")
    st.title("TALMA task plans")

    default_path = Path(__file__).resolve().parent / "data.xlsx"
    data_path = st.sidebar.text_input("Workbook path", value=str(default_path))

    try:
        df = _get_tasks(data_path)
    except FileNotFoundError:
        st.error(f"File not found: {data_path}")
        return
    except Exception as e:  # noqa: BLE001 — show load errors in UI
        st.exception(e)
        return

    st.sidebar.metric("Tasks", len(df))

    sheets = sorted(df["source_sheet"].dropna().unique().tolist()) if "source_sheet" in df.columns else []
    selected_sheets = st.sidebar.multiselect("Department (sheet)", options=sheets, default=sheets)

    focus_options = focus_area_filter_choices(df)
    selected_focus = st.sidebar.selectbox(
        "Focus area filter",
        options=["(all)"] + focus_options,
        index=0,
    )

    filtered = df.copy()
    if selected_sheets:
        filtered = filtered[filtered["source_sheet"].isin(selected_sheets)]

    if selected_focus and selected_focus != "(all)":
        f1 = filtered["focus_area_1"] if "focus_area_1" in filtered.columns else pd.Series(dtype=object)
        f2 = filtered["focus_area_2"] if "focus_area_2" in filtered.columns else pd.Series(dtype=object)
        mask = (f1 == selected_focus) | (f2 == selected_focus)
        filtered = filtered[mask]

    browse_tab, groups_tab = st.tabs(["Browse tasks", "Tasks per focus group"])

    with browse_tab:
        display_cols = [
            c
            for c in [
                "source_sheet",
                "Task Name",
                "Focus Area",
                "focus_area_raw",
                "focus_area_1",
                "focus_area_2",
                "focus_area_combo",
                "Status",
                "Priority",
            ]
            if c in filtered.columns
        ]
        st.dataframe(filtered[display_cols] if display_cols else filtered, use_container_width=True)

    with groups_tab:
        st.caption(
            "Each task is counted once under its normalized focus group "
            "(same labels as **focus area combo**: one area, or two sorted as `A | B`). "
            "Sidebar filters still apply."
        )
        summary = tasks_per_focus_group(filtered)
        total = int(summary["tasks"].sum()) if len(summary) else 0
        st.metric("Tasks in view", total)
        if len(summary):
            chart_df = summary.set_index("focus_group")
            st.bar_chart(chart_df)
            st.dataframe(summary, use_container_width=True, hide_index=True)
        else:
            st.info("No tasks match the current filters.")


if __name__ == "__main__":
    main()
