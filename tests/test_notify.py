import json

import notify
from schema import Listing

CFG = {
    "ntfy": {"server": "https://ntfy.sh", "topic": "t0pic"},
    "push": {"min_score": 70, "high_priority_score": 90,
             "flood_guard": {"max_instant": 3}},
}


def make(i=1, score_title="3BR Somerville", price=2400, **kw):
    kw.setdefault("address", "12 Oak St, Somerville")
    return Listing(source="craigslist", source_id=str(i),
                   url=f"https://example.com/{i}", title=score_title,
                   price=price, beds=3.0, baths=1.0, **kw)


def setup_capture(monkeypatch, tmp_path):
    sent = []
    monkeypatch.setattr(notify, "_post",
                        lambda server, topic, body, headers: sent.append(
                            {"topic": topic, "body": body, "headers": headers}))
    monkeypatch.setattr(notify, "data_dir", lambda slug: tmp_path)
    return sent


def read_log(tmp_path):
    log = tmp_path / "alerts.log"
    if not log.exists():
        return []
    return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]


def test_push_formats_title_and_click(monkeypatch, tmp_path):
    sent = setup_capture(monkeypatch, tmp_path)
    notify.push(make(), 82, ["good fit", "12 min to anchor"], CFG, "x")
    assert len(sent) == 1
    h = sent[0]["headers"]
    assert h["Title"] == "$2,400 · 3bd/1ba · 12 Oak St, Somerville (score 82)"
    assert h["Click"] == "https://example.com/1"
    assert h["Priority"] == "default"
    assert "good fit" in sent[0]["body"]


def test_high_score_maps_to_high_priority(monkeypatch, tmp_path):
    sent = setup_capture(monkeypatch, tmp_path)
    notify.push(make(), 93, ["great"], CFG, "x")
    assert sent[0]["headers"]["Priority"] == "high"


def test_image_attached_and_emoji_title_sanitized(monkeypatch, tmp_path):
    sent = setup_capture(monkeypatch, tmp_path)
    l = make(address=None, score_title="Sunny \U0001f3e1 3BR",
             images=["https://img.example/1.jpg"])
    notify.push(l, 75, [], CFG, "x")
    h = sent[0]["headers"]
    assert h["Attach"] == "https://img.example/1.jpg"
    h["Title"].encode("latin-1")   # must not raise


def test_price_drop_tagged(monkeypatch, tmp_path):
    sent = setup_capture(monkeypatch, tmp_path)
    l = make(raw={"price_drop_from": 2600})
    notify.push(l, 75, ["still nice"], CFG, "x")
    assert "PRICE DROP: was $2,600" in sent[0]["body"]
    assert "moneybag" in sent[0]["headers"]["Tags"]


def test_flood_guard_splits_instant_and_summary(monkeypatch, tmp_path):
    sent = setup_capture(monkeypatch, tmp_path)
    qualifying = [(make(i), 70 + i, [f"r{i}"]) for i in range(6)]
    result = notify.push_all(qualifying, CFG, "x")
    assert result == {"instant": 3, "summarized": 3}
    assert len(sent) == 4                       # 3 instant + 1 summary
    # instant ones are the top scores (75, 74, 73)
    instant_titles = [s["headers"]["Title"] for s in sent[:3]]
    assert all("(score 7" in t for t in instant_titles)
    assert sent[3]["headers"]["Title"] == "+3 more matches"
    assert sent[3]["body"].count("https://example.com/") == 3


def test_no_summary_when_under_cap(monkeypatch, tmp_path):
    sent = setup_capture(monkeypatch, tmp_path)
    result = notify.push_all([(make(1), 80, [])], CFG, "x")
    assert result == {"instant": 1, "summarized": 0}
    assert len(sent) == 1


def test_alert_trail_written(monkeypatch, tmp_path):
    setup_capture(monkeypatch, tmp_path)
    qualifying = [(make(i), 70 + i, ["r"]) for i in range(5)]
    notify.push_all(qualifying, CFG, "x")
    entries = read_log(tmp_path)
    assert len(entries) == 5
    kinds = {e["kind"] for e in entries}
    assert kinds == {"instant", "summary_item"}
    assert all(e["dry_run"] is False for e in entries)


def test_dry_run_logs_but_sends_nothing(monkeypatch, tmp_path):
    sent = setup_capture(monkeypatch, tmp_path)
    notify.push_all([(make(1), 80, ["r"])], CFG, "x", dry_run=True)
    assert sent == []
    entries = read_log(tmp_path)
    assert len(entries) == 1 and entries[0]["dry_run"] is True
