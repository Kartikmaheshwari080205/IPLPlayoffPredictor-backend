from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Optional

import requests


ROOT = Path(__file__).resolve().parent
MATCHES_FILE = ROOT / "matches.txt"
H2H_FILE = ROOT / "h2h.txt"
JSON_DIR = ROOT / "ipl_json"
CRICSHEET_URL = "https://cricsheet.org/downloads/ipl_json.zip"

TEAM_ORDER = ["MI", "CSK", "RCB", "KKR", "RR", "DC", "PBKS", "SRH", "GT", "LSG"]
TEAM_SET = set(TEAM_ORDER)

TEAM_ALIASES = {
    "MI": "MI",
    "MUMBAI INDIANS": "MI",
    "CSK": "CSK",
    "CHENNAI SUPER KINGS": "CSK",
    "RCB": "RCB",
    "ROYAL CHALLENGERS BANGALORE": "RCB",
    "ROYAL CHALLENGERS BENGALURU": "RCB",
    "BANGALORE": "RCB",
    "BENGALURU": "RCB",
    "KKR": "KKR",
    "KOLKATA KNIGHT RIDERS": "KKR",
    "RR": "RR",
    "RAJASTHAN ROYALS": "RR",
    "DC": "DC",
    "DELHI CAPITALS": "DC",
    "DELHI DAREDEVILS": "DC",
    "DELHI": "DC",
    "PBKS": "PBKS",
    "PUNJAB KINGS": "PBKS",
    "KINGS XI PUNJAB": "PBKS",
    "PUNJAB": "PBKS",
    "SRH": "SRH",
    "SUNRISERS HYDERABAD": "SRH",
    "SUNRISERS": "SRH",
    "GT": "GT",
    "GUJARAT TITANS": "GT",
    "LSG": "LSG",
    "LUCKNOW SUPER GIANTS": "LSG",
}


def normalize_team_name(raw: str) -> Optional[str]:
    normalized = raw.strip().upper()
    if normalized in TEAM_SET:
        return normalized
    return TEAM_ALIASES.get(normalized)


def detect_newline(text: str) -> str:
    return "\r\n" if "\r\n" in text else "\n"


def download_and_extract_json_archive() -> None:
    if JSON_DIR.exists():
        shutil.rmtree(JSON_DIR)
    JSON_DIR.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_file:
        temp_zip_path = Path(tmp_file.name)

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/zip,application/octet-stream,*/*",
            "Referer": "https://cricsheet.org/",
        }

        response = requests.get(CRICSHEET_URL, headers=headers, stream=True)

        print("Status Code:", response.status_code)
        print("Content-Type:", response.headers.get("Content-Type"))

        if response.status_code != 200:
            raise RuntimeError(f"Download failed: {response.status_code}")

        for chunk in response.iter_content(chunk_size=8192):
            tmp_file.write(chunk)

    if not zipfile.is_zipfile(temp_zip_path):
        with open(temp_zip_path, "rb") as f:
            preview = f.read(300)

        raise ValueError(f"Invalid ZIP download\nPreview:\n{preview}")

    try:
        with zipfile.ZipFile(temp_zip_path) as archive:
            for member in archive.namelist():
                if member.lower().endswith(".json"):
                    archive.extract(member, JSON_DIR)
    finally:
        temp_zip_path.unlink(missing_ok=True)


def load_matches():
    raw = MATCHES_FILE.read_text()
    entries = []

    for line in raw.splitlines():
        if not line.strip() or line.startswith("#"):
            entries.append({"kind": "passthrough", "line": line})
            continue

        t1, t2, mid, res = line.split()
        entries.append({
            "kind": "match",
            "team1": normalize_team_name(t1),
            "team2": normalize_team_name(t2),
            "match_id": mid,
            "result": res
        })

    return entries, "\n"


def write_matches(entries, nl):
    lines = []
    for e in entries:
        if e["kind"] == "passthrough":
            lines.append(e["line"])
        else:
            lines.append(f"{e['team1']} {e['team2']} {e['match_id']} {e['result']}")
    MATCHES_FILE.write_text("\n".join(lines) + "\n")


def load_h2h():
    raw = H2H_FILE.read_text()
    lines = raw.splitlines()

    comments = []
    data = []
    for l in lines:
        if not l.strip() or l.startswith("#"):
            comments.append(l)
        else:
            data.append(l)

    header = data[0].split()[1:]
    matrix = {t: {} for t in TEAM_ORDER}

    for row in data[1:]:
        parts = row.split()
        r = normalize_team_name(parts[0])
        for c, val in zip(header, parts[1:]):
            matrix[r][normalize_team_name(c)] = int(val)

    return comments, matrix, header, "\n"


def write_h2h(comments, matrix, cols, nl):
    lines = comments[:]
    lines.append("TEAM " + " ".join(cols))
    for t in TEAM_ORDER:
        lines.append(f"{t} " + " ".join(str(matrix[t][c]) for c in cols))
    H2H_FILE.write_text("\n".join(lines) + "\n")


def extract_result_from_json(path):
    data = json.load(open(path))
    info = data.get("info", {})

    match_id = str(info.get("event", {}).get("match_number"))
    teams = info.get("teams", [])

    a = normalize_team_name(teams[0])
    b = normalize_team_name(teams[1])

    winner = info.get("outcome", {}).get("winner")
    winner = normalize_team_name(winner) if winner else None

    return match_id, (a, b), winner


def update_from_recent_json(entries, matrix):
    updated = 0
    h2h_updates = 0

    files = sorted(JSON_DIR.glob("*.json"), key=lambda x: int(x.stem), reverse=True)

    seen_any = False

    for f in files:
        match_id, (a, b), winner = extract_result_from_json(f)

        if match_id == "1" and seen_any:
            break
        seen_any = True

        for e in entries:
            if e["kind"] == "match" and e["match_id"] == match_id:
                if e["result"] != "PENDING":
                    continue

                e["result"] = winner if winner else "NR"
                updated += 1

                if winner:
                    loser = b if winner == a else a
                    matrix[winner][loser] += 1
                    h2h_updates += 1
                break

    return updated, h2h_updates


def main():
    entries, nl = load_matches()
    comments, matrix, cols, nl2 = load_h2h()

    download_and_extract_json_archive()
    updated, h2h = update_from_recent_json(entries, matrix)

    write_matches(entries, nl)
    write_h2h(comments, matrix, cols, nl2)

    print("Updated matches:", updated)
    print("H2H updates:", h2h)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())