from gates import gate
from schema import Listing

CRITERIA = {
    "budget": {"max_rent": 2000},
    "group": {"size": 3, "seeking": ["whole_unit", "room_in_shared"]},
    "unit": {"beds_min": 3},
    "location": {"areas_no": ["Revere"]},
    "move_in": {"earliest": "2026-08-01", "latest": "2026-09-01"},
}

WHOLE_ONLY = {**CRITERIA, "group": {"size": 3, "seeking": ["whole_unit"]}}


def make(**kw):
    base = dict(source="craigslist", source_id="1", url="u", title="Nice place")
    base.update(kw)
    return Listing(**base)


def test_within_budget_whole_unit_passes():
    ok, _ = gate(make(price=5500, beds=3.0), CRITERIA)
    assert ok


def test_over_unit_ceiling_fails():
    ok, reasons = gate(make(price=6500, beds=3.0), CRITERIA)
    assert not ok and reasons[0].startswith("over_budget")


def test_small_cheap_listing_passes_as_room():
    # 1BR-ish post at $1400: not a 3BR, but plausible as a room in shared
    ok, _ = gate(make(price=1400, beds=1.0), CRITERIA)
    assert ok


def test_small_expensive_listing_fails_both_shapes():
    # 2BR at $4500: under unit ceiling but below beds_min, and too dear for a room
    ok, reasons = gate(make(price=4500, beds=2.0), CRITERIA)
    assert not ok and "no_sought_shape_fits" in reasons


def test_under_beds_min_fails_when_whole_unit_only():
    ok, _ = gate(make(price=1400, beds=1.0), WHOLE_ONLY)
    assert not ok


def test_ambiguous_missing_fields_pass_through():
    ok, _ = gate(make(price=None, beds=None), CRITERIA)
    assert ok
    ok, _ = gate(make(price=None, beds=None), WHOLE_ONLY)
    assert ok


def test_excluded_area_fails():
    ok, reasons = gate(make(price=5000, beds=3.0, address="1 Beach St, Revere MA"),
                       CRITERIA)
    assert not ok and reasons[0].startswith("excluded_area")


def test_excluded_area_matches_title_too():
    ok, _ = gate(make(price=5000, beds=3.0, title="Sunny 3BR in Revere!"), CRITERIA)
    assert not ok


def test_available_after_window_fails():
    ok, reasons = gate(make(price=5000, beds=3.0, available="2026-10-15"), CRITERIA)
    assert not ok and reasons[0].startswith("available_too_late")


def test_available_early_or_missing_passes_to_judge():
    assert gate(make(price=5000, beds=3.0, available="2026-06-01"), CRITERIA)[0]
    assert gate(make(price=5000, beds=3.0, available=None), CRITERIA)[0]


def test_unparseable_available_passes():
    assert gate(make(price=5000, beds=3.0, available="ask me"), CRITERIA)[0]
