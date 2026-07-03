"""Profile loading. A profile is profiles/<slug>/{criteria,sources,notify}.yaml
plus optional secrets.yaml (gitignored; holds the ntfy topic)."""

from __future__ import annotations

from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROFILES_DIR = PROJECT_ROOT / "profiles"
DATA_DIR = PROJECT_ROOT / "data"


def list_profiles() -> list[str]:
    if not PROFILES_DIR.is_dir():
        return []
    return sorted(
        p.name for p in PROFILES_DIR.iterdir()
        if p.is_dir() and not p.name.startswith("_")
    )


def _load_yaml(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def resolve_slug(slug: str | None) -> str:
    """Explicit slug, or the only existing profile."""
    if slug:
        if not (PROFILES_DIR / slug).is_dir():
            raise SystemExit(f"no such profile: {slug} (have: {', '.join(list_profiles()) or 'none'})")
        return slug
    profiles = list_profiles()
    if len(profiles) == 1:
        return profiles[0]
    raise SystemExit(f"--profile required (have: {', '.join(profiles) or 'none'})")


def load_profile(slug: str | None) -> dict:
    slug = resolve_slug(slug)
    pdir = PROFILES_DIR / slug
    profile = {
        "slug": slug,
        "dir": pdir,
        "criteria": _load_yaml(pdir / "criteria.yaml"),
        "sources": _load_yaml(pdir / "sources.yaml"),
        "notify": _load_yaml(pdir / "notify.yaml"),
    }
    secrets_path = pdir / "secrets.yaml"
    if secrets_path.exists():
        secrets = _load_yaml(secrets_path)
        ntfy = profile["notify"].setdefault("ntfy", {})
        ntfy.update(secrets.get("ntfy") or {})
    return profile


def data_dir(slug: str) -> Path:
    d = DATA_DIR / slug
    d.mkdir(parents=True, exist_ok=True)
    return d
