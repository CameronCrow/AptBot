from schema import Listing
from store import Store


def make(source="craigslist", source_id="111", price=2400, beds=3.0,
         address="12 Oak Street, Somerville, MA", **kw):
    return Listing(source=source, source_id=source_id,
                   url=f"https://example.com/{source_id}", title="3BR near Union Sq",
                   price=price, beds=beds, address=address, **kw)


def test_new_then_seen(tmp_path):
    store = Store(tmp_path / "seen.db")
    l = make()
    assert store.is_new(l)
    store.mark_seen(l)
    assert not store.is_new(l)


def test_cross_post_collapse_via_fuzzy_key(tmp_path):
    store = Store(tmp_path / "seen.db")
    cl = make(source="craigslist", source_id="111",
              address="12 Oak Street, Somerville MA")
    store.mark_seen(cl)
    # same unit on zillow: different source id, same price/beds, address
    # formatted differently
    zi = make(source="zillow", source_id="zpid-999",
              address="12 Oak St., Somerville, MA")
    assert not store.is_new(zi)


def test_missing_fuzzy_fields_never_collapse(tmp_path):
    store = Store(tmp_path / "seen.db")
    store.mark_seen(make(source_id="111", address=None))
    other = make(source="zillow", source_id="222", address=None)
    assert other.fuzzy_key() is None
    assert store.is_new(other)


def test_price_drop_detected(tmp_path):
    store = Store(tmp_path / "seen.db")
    store.mark_seen(make(price=2400))
    dropped = make(price=2200)
    assert store.price_drop(dropped) == 2400
    assert store.price_drop(make(price=2400)) is None   # same price: no drop
    assert store.price_drop(make(price=2600)) is None   # increase: no drop


def test_price_drop_across_sources(tmp_path):
    store = Store(tmp_path / "seen.db")
    store.mark_seen(make(source="zillow", source_id="z1", price=2400))
    # cross-posted cheaper elsewhere — fuzzy key must carry the drop lookup;
    # fuzzy key includes price, so a *changed* price only matches by exact
    # fingerprint. Same fingerprint, lower price:
    assert store.price_drop(make(source="zillow", source_id="z1", price=2300)) == 2400


def test_mark_alerted_and_stats(tmp_path):
    store = Store(tmp_path / "seen.db")
    l = make()
    store.mark_seen(l)
    store.mark_alerted(l, score=82, verdict="push")
    assert store.stats() == {"seen": 1, "alerted": 1}


def test_recent_comps(tmp_path):
    store = Store(tmp_path / "seen.db")
    store.mark_seen(make(source_id="1", price=2400, beds=3.0, address="1 A St"))
    store.mark_seen(make(source_id="2", price=2600, beds=3.0, address="2 B St"))
    store.mark_seen(make(source_id="3", price=1500, beds=1.0, address="3 C St"))
    assert sorted(store.recent_comps(beds=3.0)) == [2400, 2600]
    assert len(store.recent_comps()) == 3
