"""Unit tests for focus area parsing."""

from __future__ import annotations

import logging

import pandas as pd
import pytest

from talma_plans.focus_areas import parse_focus_areas


def test_single_alumni() -> None:
    r = parse_focus_areas("Alumni")
    assert r["focus_area_raw"] == "Alumni"
    assert r["focus_area_1"] == "Alumni"
    assert r["focus_area_2"] is None
    assert r["focus_area_combo"] == "Alumni"


def test_pd_full_year_order_a() -> None:
    r = parse_focus_areas("PD, Full Year")
    assert r["focus_area_1"] == "Full Year"
    assert r["focus_area_2"] == "PD"
    assert r["focus_area_combo"] == "Full Year | PD"


def test_full_year_pd_same_as_above() -> None:
    a = parse_focus_areas("PD, Full Year")
    b = parse_focus_areas("Full Year, PD")
    for key in ("focus_area_1", "focus_area_2", "focus_area_combo"):
        assert a[key] == b[key]


def test_whitespace_trim() -> None:
    r = parse_focus_areas("  PD ,  Full Year  ")
    assert r["focus_area_1"] == "Full Year"
    assert r["focus_area_2"] == "PD"
    assert r["focus_area_combo"] == "Full Year | PD"


def test_empty_string() -> None:
    r = parse_focus_areas("")
    assert r["focus_area_1"] is None
    assert r["focus_area_2"] is None
    assert r["focus_area_combo"] is None
    assert r["focus_area_raw"] is None


def test_none() -> None:
    r = parse_focus_areas(None)
    assert r["focus_area_1"] is None
    assert r["focus_area_2"] is None


def test_pandas_na() -> None:
    r = parse_focus_areas(pd.NA)
    assert r["focus_area_raw"] is None
    assert r["focus_area_1"] is None


def test_three_plus_logs_and_keeps_first_two_alphabetically(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.WARNING)
    r = parse_focus_areas("Alumni, PD, Evaluation")
    assert r["focus_area_1"] == "Alumni"
    assert r["focus_area_2"] == "Evaluation"
    assert r["focus_area_combo"] == "Alumni | Evaluation"
    assert any("More than 2 focus areas" in rec.message for rec in caplog.records)


def test_duplicate_tokens_deduped() -> None:
    r = parse_focus_areas("PD, PD, Full Year")
    assert r["focus_area_1"] == "Full Year"
    assert r["focus_area_2"] == "PD"
