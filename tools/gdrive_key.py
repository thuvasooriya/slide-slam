#!/usr/bin/env python3
"""Key-aware Google Drive folder downloader.

`gdown` cannot send Drive `resourcekey`s, so it 401s on legacy link-shared
folders. This tool scrapes the server-rendered folder pages the same way a
browser sees them:

- folder listing: ``drive/folders/<id>?resourcekey=<key>`` page HTML contains
  one ``<tr data-id>`` row per item (display name, size) plus full
  ``drive/folders/<id>?resourcekey=<key>`` share links for subfolders, so
  recursion needs no API key, no OAuth, no cookies;
- file download: ``uc?id=<id>&export=download`` (plus ``&resourcekey=`` for
  legacy file IDs), with the standard virus-scan confirm dance.

Only dependency is ``requests``.

Usage:
    python tools/gdrive_key.py list <folder-url>
    python tools/gdrive_key.py download <folder-url> -O <out-dir> [--include PATTERN]
"""

import argparse
import html as _html
import os
import re
import sys
import urllib.parse

import requests

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}


def _norm(s):
    bs = chr(92)
    return (
        s.replace(bs + bs + "/", "/")
        .replace(bs + "/", "/")
        .replace(bs + bs + "u003d", "=")
        .replace(bs + "u003d", "=")
        .replace("%3D", "=")
        .replace("%3d", "=")
    )


def _split_url(url):
    """Return (folder_id, resourcekey or None) for a drive folders URL."""
    q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    key = (q.get("resourcekey") or [None])[0]
    m = re.search(r"/folders/([A-Za-z0-9_-]{20,})", url)
    if not m:
        raise ValueError(f"not a drive folders URL: {url}")
    return m.group(1), key


def _fetch_page(fid, key):
    url = f"https://drive.google.com/drive/folders/{fid}"
    if key:
        url += f"?resourcekey={key}"
    r = requests.get(url, headers=UA, timeout=30)
    r.raise_for_status()
    return r.text


def _file_key(norm, rid, default):
    m = re.search(
        r"drive\.google\.com/file/d/" + re.escape(rid)
        + r"(?:/view)?(?:\?resourcekey=(0-[A-Za-z0-9_-]+))?",
        norm,
    )
    if m:
        return m.group(1) or default
    return default


def list_folder(url):
    """Return (items, subfolders).

    items: list of (name, file_id, size_str or None, file_key or None).
    subfolders: list of (name, subfolder_url_with_key).
    """
    fid, key = _split_url(url)
    html = _fetch_page(fid, key)
    norm = _norm(html)
    keymap = dict(
        re.findall(
            r"drive\.google\.com/drive/folders/([A-Za-z0-9_-]{20,})"
            r"\?resourcekey=(0-[A-Za-z0-9_-]+)",
            norm,
        )
    )
    items, subfolders = [], []
    for m in re.finditer(
        r'<tr[^>]*data-id="([A-Za-z0-9_-]{20,})"[^>]*>(.*?)</tr>', html, re.S
    ):
        rid, body = m.group(1), m.group(2)
        text = _html.unescape(re.sub(r"\|+", "|", re.sub(r"<[^>]+>", "|", body)))
        cells = [c.strip() for c in text.strip("|").split("|") if c.strip()]
        if not cells:
            continue
        name = cells[0]
        size = next(
            (c for c in cells if re.fullmatch(r"[\d.]+\s*(?:GB|MB|KB|B)", c)), None
        )
        if rid in keymap or "Shared folder" in body:
            subkey = keymap.get(rid, key)
            subfolders.append(
                (
                    name,
                    f"https://drive.google.com/drive/folders/{rid}"
                    + (f"?resourcekey={subkey}" if subkey else ""),
                )
            )
        else:
            # File rows lead with the type icon text ("Compressed archive");
            # the real filename is the cell ending in an extension.
            dotted = next(
                (c for c in cells if re.search(r"\.\w{2,5}$", c)), None
            )
            if dotted is not None:
                name = dotted
            # Google-native docs have no downloadable bytes; skip them.
            if "." not in name:
                print(f"skip (google-native, not downloadable): {name}",
                      file=sys.stderr)
                continue
            items.append((name, rid, size, _file_key(norm, rid, key)))
    return items, subfolders


def download_file(fid, dest, key=None):
    params = {"id": fid, "export": "download"}
    if key:
        params["resourcekey"] = key
    sess = requests.Session()
    r = sess.get(
        "https://drive.google.com/uc", params=params, headers=UA,
        stream=True, timeout=60,
    )
    # Large-file virus-scan confirm dance.
    token = None
    for k, v in r.cookies.items():
        if k.startswith("download_warning"):
            token = v
            break
    if token:
        params["confirm"] = token
        r = sess.get(
            "https://drive.google.com/uc", params=params, headers=UA,
            stream=True, timeout=60,
        )
    r.raise_for_status()
    tmp = dest + ".part"
    with open(tmp, "wb") as f:
        for chunk in r.iter_content(1 << 20):
            if chunk:
                f.write(chunk)
    os.replace(tmp, dest)
    return dest


def walk(url):
    """Yield (path_parts, kind, id, size, key) depth-first."""
    items, subfolders = list_folder(url)
    for name, rid, size, fkey in items:
        yield [name], "file", rid, size, fkey
    for name, suburl in subfolders:
        for parts, kind, rid, size, fkey in walk(suburl):
            yield [name] + parts, kind, rid, size, fkey


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("action", choices=["list", "download"])
    ap.add_argument("url", help="drive folders URL (may carry ?resourcekey=)")
    ap.add_argument("-O", "--output", default=".",
                    help="output dir for download")
    ap.add_argument("--include", default=None,
                    help="only download paths containing this substring")
    args = ap.parse_args(argv)
    if args.action == "list":
        for parts, kind, rid, size, _ in walk(args.url):
            suffix = f"  [{kind}" + (f", {size}" if size else "") + "]"
            print("/".join(parts) + suffix)
        return 0
    total = 0
    for parts, kind, rid, size, fkey in walk(args.url):
        if kind != "file":
            continue
        rel = os.path.join(*parts)
        if args.include and args.include not in rel:
            continue
        dest = os.path.join(args.output, rel)
        if os.path.exists(dest):
            print(f"skip (exists): {rel}")
            continue
        parent = os.path.dirname(dest)
        if parent:
            os.makedirs(parent, exist_ok=True)
        print(f"fetching: {rel} ({size or '?'}) [{rid[:8]}...]")
        download_file(rid, dest, fkey)
        total += 1
    print(f"downloaded {total} file(s) to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
