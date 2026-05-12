#!/usr/bin/env python3
# coding: utf8
"""
Smallest AI Pulse STT — batch transcription for SpeechColab Leaderboard.
Docs: https://docs.smallest.ai/waves/llms-full.txt
API:  POST https://api.smallest.ai/waves/v1/pulse/get_text?language=en
"""
import sys
import time
import requests

ENDPOINT = "https://api.smallest.ai/waves/v1/pulse/get_text"
LANGUAGE = "en"
MAX_RETRIES = 5
RETRY_DELAY = 5  # seconds between retries on transient errors
QPS_INTERVAL = 0.2  # seconds between requests to avoid rate limiting


def transcribe(audio_path: str, api_key: str) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "audio/wav",
    }
    params = {"language": LANGUAGE}

    with open(audio_path, "rb") as f:
        audio_bytes = f.read()

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.post(
                ENDPOINT,
                headers=headers,
                params=params,
                data=audio_bytes,
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            text = data.get("transcription") or data.get("text") or ""
            return text.strip()
        except requests.exceptions.HTTPError as e:
            # 429 rate-limit or 5xx server error — retry
            if resp.status_code in (429, 500, 502, 503) and attempt < MAX_RETRIES:
                sys.stderr.write(
                    f"HTTP {resp.status_code} on attempt {attempt}, retrying in {RETRY_DELAY}s...\n"
                )
                time.sleep(RETRY_DELAY)
            else:
                sys.stderr.write(f"ERROR: {e}\n")
                return ""
        except Exception as e:
            sys.stderr.write(f"ERROR on attempt {attempt}: {e}\n")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                return ""

    return ""


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.stderr.write("Usage: asr_api.py <wav.scp> <output_trans> <api_key_file>\n")
        sys.exit(1)

    scp_path, out_path, key_file = sys.argv[1], sys.argv[2], sys.argv[3]

    with open(key_file, "r") as f:
        api_key = f.read().strip()

    with open(scp_path, "r", encoding="utf8") as scp, \
         open(out_path, "w", encoding="utf8") as out:

        lines = [l.strip() for l in scp if l.strip()]
        total = len(lines)

        for n, line in enumerate(lines):
            parts = line.split("\t", 1)
            if len(parts) != 2:
                sys.stderr.write(f"Skipping malformed line: {line}\n")
                continue

            audio_id, audio_path = parts
            sys.stderr.write(f"{n}\tid:{audio_id}\taudio:{audio_path}\n")
            sys.stderr.flush()

            time.sleep(QPS_INTERVAL)
            text = transcribe(audio_path, api_key)
            out.write(f"{audio_id}\t{text}\n")
            out.flush()

            sys.stderr.write(f"[PROGRESS] {n + 1}/{total}\n")
            sys.stderr.flush()
