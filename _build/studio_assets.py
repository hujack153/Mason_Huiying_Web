"""Prepare the online studio using the public site's own page templates."""
import hashlib
import json
import shutil
from pathlib import Path

from build_all import render_home, render_waterproofing
from content import fill
from studio import source, references


def build_studio(output):
    root = Path(__file__).resolve().parent.parent
    admin = Path(output) / "admin"
    shutil.copy2(admin / "index.html", admin / "classic.html")
    for name in ("index.html", "studio.js", "studio.css"):
        shutil.copy2(root / "_build" / "studio" / name, admin / name)
    preview = admin / "preview"
    preview.mkdir()
    tokens = {
        "%%N_WP%%": "__STUDIO_COUNT__",
        "%%N_WP_ZH%%": "__STUDIO_COUNT_ZH__",
        "%%N_WP_EN%%": "__STUDIO_COUNT_EN__",
        "%%n_WP_en%%": "__STUDIO_COUNT_EN_LOWER__",
    }
    for lang in ("zh", "en"):
        pages = {
            "home": render_home(lang, copy={"h1": "__STUDIO_TITLE__", "lead": "__STUDIO_LEAD__"}),
            "waterproofing": render_waterproofing(lang, series=[]),
        }
        for name, html in pages.items():
            html = html.replace('<div class="jump"></div>', '<div class="jump">__STUDIO_JUMP__</div>')
            html = html.replace('<div class="schedule"></div>', '<div class="schedule">__STUDIO_ROWS__</div>')
            for token, marker in tokens.items():
                html = html.replace(token, marker)
            base = "/" if lang == "zh" else "/en/"
            html = fill(html).replace("<head>", f'<head><base href="{base}">', 1)
            (preview / f"{name}_{lang}.html").write_text(html, encoding="utf-8")
    canonical = json.dumps(source(), sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    manifest = {"baseline": hashlib.sha256(canonical.encode("utf-8")).hexdigest(), "references": references()}
    (admin / "deployment.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
