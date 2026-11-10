"""Local-only content editor. Run: python _build/studio.py"""
import argparse
import hashlib
import io
import json
import re
import webbrowser
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tempfile import NamedTemporaryFile
from threading import Lock
from urllib.parse import unquote, urlsplit
from zipfile import ZIP_DEFLATED, ZipFile

from build_all import render_home, render_waterproofing
from content import fill, waterproofing_series

ROOT = Path(__file__).resolve().parent.parent
UI = Path(__file__).with_name("studio")
DRAFT = ROOT / ".ai-local" / "studio-draft.json"
HOST = "127.0.0.1:8765"
ORIGIN = f"http://{HOST}"
LANGS = ("zh", "en")
FILES = {
    (kind, lang): f"content/{lang}/{kind}.json"
    for kind in ("home", "waterproofing")
    for lang in LANGS
}
FIELDS = ("name", "tagline", "desc", "use")
ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
MAX_REQUEST = 1024 * 1024
DRAFT_LOCK = Lock()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def version(value):
    return hashlib.sha256(json_bytes(value)).hexdigest()


def source():
    data = {"home": {}, "waterproofing": {}}
    for (kind, lang), path in FILES.items():
        data[kind][lang] = json.loads((ROOT / path).read_text(encoding="utf-8"))
    return data


def saved_draft():
    if DRAFT.is_file():
        return json.loads(DRAFT.read_text(encoding="utf-8"))
    return None


def save_draft(value):
    DRAFT.parent.mkdir(exist_ok=True)
    ignore = DRAFT.parent / ".gitignore"
    if not ignore.exists():
        ignore.write_text("*\n", encoding="utf-8")
    temporary = None
    try:
        with NamedTemporaryFile(dir=DRAFT.parent, delete=False) as file:
            temporary = Path(file.name)
            file.write(json_bytes(value))
        temporary.replace(DRAFT)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def references():
    links = {}
    paths = list((ROOT / "content").rglob("*.json")) + list((ROOT / "_build").glob("*.py"))
    for path in paths:
        if path == Path(__file__):
            continue
        for code in set(re.findall(r"waterproofing(?:\.html)?#([a-z0-9-]+)", path.read_text(encoding="utf-8"))):
            links.setdefault(code, []).append(path.relative_to(ROOT).as_posix())
    return links


def valid_text(value):
    return isinstance(value, str) and len(value) <= 6000 and "\0" not in value


def validate(data, *, complete=False):
    def check(condition, message):
        if not condition:
            raise ValueError(message)

    check(isinstance(data, dict) and set(data) == {"home", "waterproofing"}, "草稿格式錯誤。")
    for kind in data.values():
        check(isinstance(kind, dict) and set(kind) == set(LANGS), "需要中文與英文兩份資料。")
    ids = {}
    archived = {}
    for lang in LANGS:
        home = data["home"][lang]
        check(isinstance(home, dict) and set(home) == {"h1", "lead"}, "首頁欄位格式錯誤。")
        check(all(valid_text(text) for text in home.values()), "首頁文字格式錯誤或過長。")
        if complete:
            check(all(text.strip() for text in home.values()), f"{lang} 的首頁主標與引言為必填。")
        catalog = data["waterproofing"][lang]
        check(isinstance(catalog, dict) and isinstance(catalog.get("series"), list), "產品清單格式錯誤。")
        ids[lang], archived[lang] = [], []
        for item in catalog["series"]:
            check(isinstance(item, dict), "產品欄位格式錯誤。")
            code = item.get("id")
            check(isinstance(code, str) and len(code) <= 64 and ID.fullmatch(code), "產品代號格式錯誤。")
            ids[lang].append(code)
            check(type(item.get("archived", False)) is bool, f"{code} 的上架狀態格式錯誤。")
            archived[lang].append(item.get("archived", False))
            check(all(valid_text(item.get(key)) for key in FIELDS), f"{code} 的產品文字格式錯誤。")
            check(isinstance(item.get("feat"), list) and all(map(valid_text, item["feat"])),
                  f"{code} 的特點格式錯誤。")
            check(isinstance(item.get("spec"), list) and all(
                isinstance(row, dict) and set(row) == {"k", "v"} and all(map(valid_text, row.values()))
                for row in item["spec"]
            ), f"{code} 的規格格式錯誤。")
            if complete and not item.get("archived", False):
                check(all(item[key].strip() for key in FIELDS), f"{code}（{lang}）請填寫名稱、小標、說明與適用部位。")
                check(all(row["k"].strip() and row["v"].strip() for row in item["spec"]),
                      f"{code}（{lang}）的每筆規格都需要項目與數值。")
        check(len(set(ids[lang])) == len(ids[lang]), "產品代號不可重複。")
    if complete:
        check(ids["zh"] == ids["en"], "中英文的產品代號與排序必須一致。")
        check(archived["zh"] == archived["en"], "中英文的上架狀態必須一致。")


def preview(data, page, lang):
    count = sum(not item.get("archived", False) for item in data["waterproofing"]["zh"]["series"])
    if page == "home":
        html = render_home(lang, copy=data["home"][lang])
    elif page == "waterproofing":
        html = render_waterproofing(lang, series=waterproofing_series(data["waterproofing"][lang]["series"]))
    else:
        raise ValueError("未知的預覽頁面。")
    base = "/" if lang == "zh" else "/en/"
    return fill(html, n_wp=count).replace("<head>", f'<head><base href="{base}">', 1)


def export(data, original):
    validate(data, complete=True)
    for lang in LANGS:
        for page in ("home", "waterproofing"):
            preview(data, page, lang)
    output = io.BytesIO()
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        changed = False
        for (kind, lang), path in FILES.items():
            if data[kind][lang] != original[kind][lang]:
                archive.writestr(path, json_bytes(data[kind][lang]))
                changed = True
        if not changed:
            raise ValueError("目前沒有可匯出的內容變更。")
    return output.getvalue()


class StudioHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        if urlsplit(self.path).path.startswith("/assets/"):
            self.send_header("Content-Security-Policy", "script-src 'none'; object-src 'none'")
        super().end_headers()

    def reply(self, body, content_type, status=HTTPStatus.OK, *, filename=None):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        if filename:
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.end_headers()
        self.wfile.write(body)

    def json(self, data, status=HTTPStatus.OK):
        self.reply(json_bytes(data), "application/json; charset=utf-8", status)

    def do_GET(self):
        if self.headers.get("Host") != HOST:
            self.send_error(HTTPStatus.FORBIDDEN)
            return
        path = urlsplit(self.path).path
        if path == "/api/state":
            with DRAFT_LOCK:
                original = source()
                draft = saved_draft()
            self.json({
                "source": original,
                "baseline": version(original),
                "draft": draft,
                "revision": version(draft),
                "references": references(),
            })
            return
        if path in ("/", "/index.html", "/studio.js", "/studio.css"):
            self.directory = str(UI)
        elif path.startswith("/assets/") or path == "/favicon.ico":
            directory = ROOT if path.startswith("/assets/") else ROOT / "static"
            allowed = ROOT / "assets" if path.startswith("/assets/") else directory
            candidate = (directory / unquote(path).lstrip("/")).resolve()
            if not candidate.is_relative_to(allowed) or not candidate.is_file():
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            self.directory = str(directory)
        else:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        super().do_GET()

    def do_HEAD(self):
        self.send_error(HTTPStatus.METHOD_NOT_ALLOWED)

    def do_POST(self):
        if self.headers.get("Host") != HOST or self.headers.get("Origin") != ORIGIN:
            self.json({"error": "此操作只接受本機編輯器送出的請求。"}, HTTPStatus.FORBIDDEN)
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            if self.headers.get_content_type() != "application/json" or not 0 < length <= MAX_REQUEST:
                raise ValueError("請求格式錯誤或草稿太大。")
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict):
                raise ValueError("請求格式錯誤。")
            self.handle_action(urlsplit(self.path).path, payload)
        except (ValueError, TypeError) as error:
            self.json({"error": str(error)}, HTTPStatus.BAD_REQUEST)

    def handle_action(self, path, payload):
        data = payload.get("data")
        if path == "/api/preview":
            validate(data)
            lang = payload.get("lang")
            if lang not in LANGS:
                raise ValueError("未知的語言。")
            html = preview(data, payload.get("page"), lang)
            self.reply(html.encode("utf-8"), "text/html; charset=utf-8")
            return
        if path not in ("/api/save", "/api/discard", "/api/export"):
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        with DRAFT_LOCK:
            self.handle_draft_action(path, payload, data)

    def handle_draft_action(self, path, payload, data):
        original = source()
        baseline = version(original)
        draft = saved_draft()
        if payload.get("baseline") != baseline or payload.get("revision") != version(draft):
            self.json({"error": "來源或草稿已有更新。請重新載入編輯器確認內容。"}, HTTPStatus.CONFLICT)
            return
        if path == "/api/discard":
            DRAFT.unlink(missing_ok=True)
            self.json({"revision": version(None), "source": original, "baseline": baseline})
            return
        if draft and draft.get("baseline") != baseline:
            self.json({"error": "這份草稿使用較早的來源。請備份草稿後再重設。"}, HTTPStatus.CONFLICT)
            return
        if path == "/api/save":
            validate(data)
            draft = {"baseline": baseline, "data": data}
            save_draft(draft)
            self.json({"revision": version(draft)})
        else:
            if not draft or data != draft["data"]:
                raise ValueError("請先儲存目前的草稿。")
            self.reply(export(data, original), "application/zip", filename="huiying-content.zip")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--open", action="store_true", help="Open the studio in the default browser")
    args = parser.parse_args()
    with ThreadingHTTPServer(("127.0.0.1", 8765), StudioHandler) as server:
        print(f"Studio: {ORIGIN}", flush=True)
        if args.open:
            webbrowser.open(ORIGIN)
        server.serve_forever()
