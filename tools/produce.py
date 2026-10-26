"""Produce one episode: script-tts.txt -> Gemini multi-speaker TTS -> mastered MP3.

Usage: python tools/produce.py episodes/<name> <out_dir> [--mock]

The script file has one turn per line, "<speaker>: <text>", where <speaker> is a
key of "speakers" in podcast.json. Turns are grouped into requests of at most
tts.max_words_per_request words (never splitting a turn), each request is sent
to the Interactions API, and the WAV parts are joined and mastered to MP3.
--mock replaces the API with silent placeholder audio, for local testing.
"""
import base64, json, pathlib, re, subprocess, sys, tempfile, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "podcast.json").read_text(encoding="utf-8"))
TTS = CFG["tts"]


def parse_script(path):
    turns = []
    for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        m = re.match(r"^(\S+?):\s+(.+)$", line)
        if not m or m.group(1) not in CFG["speakers"]:
            sys.exit(f"{path}:{n}: expected '<speaker>: text' with a known speaker: {line[:60]}")
        turns.append((m.group(1), m.group(2)))
    if not turns:
        sys.exit(f"{path}: empty script")
    return turns


def chunk(turns):
    chunks, cur, words = [], [], 0
    for speaker, text in turns:
        w = len(text.split())
        if cur and words + w > TTS["max_words_per_request"]:
            chunks.append(cur)
            cur, words = [], 0
        cur.append((speaker, text))
        words += w
    if cur:
        chunks.append(cur)
    return chunks


def request_audio(turns):
    from google import genai  # imported here so --mock runs without the SDK
    client = genai.Client()  # reads GEMINI_API_KEY from the environment
    content = [{
        "type": "text",
        "text": text,
        "annotations": [{
            "type": "speech_metadata",
            "speaker": CFG["speakers"][speaker]["id"],
            "style": CFG["speakers"][speaker]["style"],
        }],
    } for speaker, text in turns]
    interaction = client.interactions.create(
        model=TTS["model"],
        input=[{"type": "user_input", "content": content}],
        response_format={"type": "audio"},
        generation_config={"speech_config": {"speakers": [
            {"speaker": s["id"], "voice": s["voice"]} for s in CFG["speakers"].values()
        ]}},
    )
    audio = getattr(interaction, "output_audio", None)
    if not audio or not audio.data:
        raise RuntimeError(f"no audio in response (status={getattr(interaction, 'status', None)})")
    return base64.b64decode(audio.data)


def ff(*args):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *map(str, args)],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr[-3000:])


def synth(turns, out_wav, mock):
    if mock:
        seconds = max(1, sum(len(t.split()) for _, t in turns) / 2.4)
        ff("-f", "lavfi", "-i", "sine=frequency=180:sample_rate=24000", "-af", "volume=0.1",
           "-t", f"{seconds:.1f}", out_wav)
        return
    for attempt in range(1, 7):
        try:
            data = request_audio(turns)
            break
        except Exception as e:  # noqa: BLE001 - report and decide whether to retry
            msg = str(e)
            if any(k in msg for k in ("INVALID_ARGUMENT", "PERMISSION_DENIED", "API key", "Missing key",
                                      " 400", " 401", " 403", " 404")):
                sys.exit(f"TTS request rejected (not retrying): {msg[:1500]}")
            wait = min(120, 15 * 2 ** (attempt - 1))
            print(f"TTS attempt {attempt} failed: {msg[:300]} - retrying in {wait}s", flush=True)
            time.sleep(wait)
    else:
        sys.exit("TTS failed after 6 attempts")
    if data[:4] == b"RIFF":
        out_wav.write_bytes(data)
    else:  # headerless 24 kHz 16-bit mono PCM
        raw = out_wav.with_suffix(".pcm")
        raw.write_bytes(data)
        ff("-f", "s16le", "-ar", "24000", "-ac", "1", "-i", raw, out_wav)


def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return float(r.stdout.strip())


def master(parts, out_mp3, title):
    tmp = pathlib.Path(tempfile.mkdtemp())
    gap, edge = tmp / "gap.wav", tmp / "edge.wav"
    ff("-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", TTS["gap_between_requests_seconds"], gap)
    ff("-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", 0.4, edge)
    seq = [edge]
    for i, p in enumerate(parts):
        norm = tmp / f"n{i:02d}.wav"
        ff("-i", p, "-ar", 44100, "-ac", 1, "-c:a", "pcm_s16le", norm)
        seq += [norm] + ([gap] if i < len(parts) - 1 else [])
    seq.append(edge)
    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{s}'\n" for s in seq))
    joined = tmp / "joined.wav"
    ff("-f", "concat", "-safe", 0, "-i", lst, "-c", "copy", joined)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(joined), "-af",
                        "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rfind("{"):r.stderr.rfind("}") + 1])
    if m["input_i"] in ("-inf", "inf") or float(m["input_i"]) < -70:
        sys.exit("mastering: the joined audio is silent - check the TTS output")
    af = ("loudnorm=I=-16:TP=-1.5:LRA=11:linear=true:"
          f"measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
          f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}")
    ff("-i", joined, "-af", af, "-ar", 44100, "-ac", 1, "-c:a", "libmp3lame", "-b:a", TTS["mp3_bitrate"],
       "-metadata", f"title={title}", "-metadata", f"artist={CFG['title']}",
       "-metadata", f"album={CFG['title']}", "-metadata", "genre=Podcast",
       "-metadata", "comment=נכתב והוקלט בידי בינה מלאכותית. אינו ייעוץ משפטי.",
       "-id3v2_version", 3, out_mp3)
    return duration(out_mp3)


def notes(meta):
    lines = [meta["description"], "", "המקורות:"]
    lines += [f"- {s['title']}: {s['url']}" for s in meta.get("sources", [])]
    return "\n".join(lines) + "\n"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    mock = "--mock" in sys.argv
    ep, out_dir = pathlib.Path(args[0]), pathlib.Path(args[1])
    meta = json.loads((ep / "meta.json").read_text(encoding="utf-8"))
    turns = parse_script(ep / "script-tts.txt")
    chunks = chunk(turns)
    print(f"{ep.name}: {len(turns)} turns, {sum(len(t.split()) for _, t in turns)} words, "
          f"{len(chunks)} TTS requests", flush=True)
    tmp = pathlib.Path(tempfile.mkdtemp())
    wavs = []
    for i, c in enumerate(chunks, 1):
        wav = tmp / f"req{i:02d}.wav"
        synth(c, wav, mock)
        print(f"  request {i}/{len(chunks)}: {sum(len(t.split()) for _, t in c)} words -> "
              f"{duration(wav):.0f}s audio", flush=True)
        wavs.append(wav)
        if not mock and i < len(chunks):
            time.sleep(TTS["pause_seconds"])
    out_dir.mkdir(parents=True, exist_ok=True)
    mp3 = out_dir / f"{CFG['file_prefix']}-{ep.name}.mp3"
    secs = master(wavs, mp3, meta["title"])
    info = {"file": mp3.name, "bytes": mp3.stat().st_size, "duration_seconds": round(secs)}
    (out_dir / "episode.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "notes.md").write_text(notes(meta), encoding="utf-8")
    print(f"done: {mp3.name}, {secs / 60:.1f} min, {info['bytes'] / 1e6:.1f} MB", flush=True)
    if not 8 * 60 <= secs <= 16 * 60 and not mock:
        print(f"::warning::episode length {secs / 60:.1f} min is outside 8-16 min", flush=True)


if __name__ == "__main__":
    main()
