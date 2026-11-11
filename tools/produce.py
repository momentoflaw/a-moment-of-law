"""Produce one episode: script-tts.txt -> Gemini multi-speaker TTS -> mastered MP3.

Usage: python tools/produce.py episodes/<name> <out_dir> [--mock]

The script file has one turn per line: "<speaker>: <text>" or
"<speaker> [<delivery style>]: <text>", where <speaker> is a key of "speakers"
in podcast.json and the optional bracket replaces that speaker's default style
for this turn only. Every turn's style starts with the speaker's voice anchor
(speakers.<name>.anchor) and ends with tts.pace, so a direction changes the
emotion of a line but never the host's voice. Inline vocal tags such as <laugh>
or <short pause> pass through to the model. meta.json may override voices with
"voices": {"<speaker>": "<voice name>"}.

Turns are grouped into requests of at most tts.max_words_per_request words
(never splitting a turn), each request goes to the Interactions API, and the
WAV parts are joined and mastered to MP3. Separate requests can come back with
audibly different voices, so the limit is set to fit a whole episode in one
request; a request whose audio looks cut off is flagged in the log.
--mock replaces the API with placeholder audio, for local testing.
"""
import base64, json, pathlib, re, subprocess, sys, tempfile, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "podcast.json").read_text(encoding="utf-8"))
TTS = CFG["tts"]
LINE = re.compile(r"^(\S+?)(?:\s*\[([^\]]*)\])?:\s+(.+)$")
FALLBACKS = []  # requests that had to drop the optional speech settings
NO_RETRY = ("INVALID_ARGUMENT", "PERMISSION_DENIED", "API key", "Missing key",
            " 400", " 401", " 403", " 404")


def words(text):
    return len(re.sub(r"<[^>]+>", " ", text).split())


def parse_script(path):
    turns = []
    for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        m = LINE.match(line)
        if not m or m.group(1) not in CFG["speakers"]:
            sys.exit(f"{path}:{n}: expected '<speaker> [style]: text' with a known speaker: {line[:60]}")
        turns.append((m.group(1), (m.group(2) or "").strip() or None, m.group(3)))
    if not turns:
        sys.exit(f"{path}: empty script")
    return turns


def chunk(turns):
    """Group whole turns into about equal requests of at most max_words_per_request
    words, so the last request is never a short tail with a different sound."""
    limit = TTS["max_words_per_request"]
    n = max(1, -(-sum(words(t[2]) for t in turns) // limit))
    target = sum(words(t[2]) for t in turns) / n
    chunks, cur, count = [], [], 0
    for turn in turns:
        w = words(turn[2])
        if cur and (count + w > limit or (count >= target and len(chunks) < n - 1)):
            chunks.append(cur)
            cur, count = [], 0
        cur.append(turn)
        count += w
    if cur:
        chunks.append(cur)
    return chunks


def turn_style(speaker, style):
    """The style sent with one turn: the speaker's voice anchor, then the turn's
    own direction (or the speaker's default style when it has none), then tts.pace.
    The anchor comes first on every turn, so a direction never replaces the host's
    voice identity (owner, 11.11.2026: both voices changed mid-episode when the
    directions replaced the default style)."""
    spk = CFG["speakers"][speaker]
    body = f"Emotion for this line: {style.strip(' .')}" if style else spk["style"].strip(" .")
    parts = [spk.get("anchor", "").strip(" ."), body]
    pace = TTS.get("pace", "").strip(" .")
    if pace and pace not in body:
        parts.append(pace)
    return ". ".join(p for p in parts if p) + "."


def request_audio(turns, voices, full=True):
    """One Interactions API call. full=False drops optional speech settings
    (conversational mode, language) in case the API rejects them."""
    from google import genai  # imported here so --mock runs without the SDK
    client = genai.Client()  # reads GEMINI_API_KEY from the environment
    content = [{
        "type": "text",
        "text": text,
        "annotations": [{
            "type": "speech_metadata",
            "speaker": CFG["speakers"][speaker]["id"],
            "style": turn_style(speaker, style),
        }],
    } for speaker, style, text in turns]
    speakers = []
    for key, s in CFG["speakers"].items():
        entry = {"speaker": s["id"], "voice": voices[key]}
        if full and TTS.get("language"):
            entry["language"] = TTS["language"]
        speakers.append(entry)
    speech_config = {"speakers": speakers}
    if full and TTS.get("conversational_mode"):
        speech_config["mode"] = "conversational"
    interaction = client.interactions.create(
        model=TTS["model"],
        input=[{"type": "user_input", "content": content}],
        response_format={"type": "audio"},
        # sent as raw JSON so REST-only fields such as "mode" reach the API
        extra_body={"generation_config": {"speech_config": speech_config}},
    )
    audio = getattr(interaction, "output_audio", None)
    if not audio or not audio.data:
        raise RuntimeError(f"no audio in response (status={getattr(interaction, 'status', None)})")
    # token usage and status, to learn how many output tokens a second of audio takes
    print(f"    status={getattr(interaction, 'status', None)} usage={getattr(interaction, 'usage', None)}",
          flush=True)
    return base64.b64decode(audio.data)


def ff(*args):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *map(str, args)],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr[-3000:])


def synth(turns, voices, out_wav, mock):
    if mock:
        seconds = max(1, sum(words(t) for _, _, t in turns) / 2.4)
        ff("-f", "lavfi", "-i", "sine=frequency=180:sample_rate=24000", "-af", "volume=0.1",
           "-t", f"{seconds:.1f}", out_wav)
        return
    full = True
    attempt = 0
    while True:
        attempt += 1
        try:
            data = request_audio(turns, voices, full)
            break
        except Exception as e:  # noqa: BLE001 - report and decide whether to retry
            msg = str(e)
            if any(k in msg for k in NO_RETRY):
                if full and ("INVALID_ARGUMENT" in msg or " 400" in msg):
                    print(f"::warning::TTS rejected the optional speech settings (conversational mode, "
                          f"language); retrying without them: {msg[:300]}", flush=True)
                    full = False
                    FALLBACKS.append(msg[:200])
                    continue
                sys.exit(f"TTS request rejected (not retrying): {msg[:1500]}")
            if attempt >= 6:
                sys.exit(f"TTS failed after {attempt} attempts: {msg[:500]}")
            wait = min(120, 15 * 2 ** (attempt - 1))
            print(f"TTS attempt {attempt} failed: {msg[:300]} - retrying in {wait}s", flush=True)
            time.sleep(wait)
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
    tempo = float(TTS.get("tempo", 1.0))
    pre = f"atempo={tempo}," if abs(tempo - 1.0) > 1e-3 else ""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(joined), "-af",
                        f"{pre}loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rfind("{"):r.stderr.rfind("}") + 1])
    if m["input_i"] in ("-inf", "inf") or float(m["input_i"]) < -70:
        sys.exit("mastering: the joined audio is silent - check the TTS output")
    af = (f"{pre}loudnorm=I=-16:TP=-1.5:LRA=11:linear=true:"
          f"measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
          f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}")
    ff("-i", joined, "-af", af, "-ar", 44100, "-ac", 1, "-c:a", "libmp3lame", "-b:a", TTS["mp3_bitrate"],
       "-metadata", f"title={title}", "-metadata", f"artist={CFG['title']}",
       "-metadata", f"album={CFG['title']}", "-metadata", "genre=Podcast",
       "-metadata", "comment=נכתב והוקלט בידי בינה מלאכותית. אינו ייעוץ משפטי.",
       "-id3v2_version", 3, out_mp3)
    return duration(out_mp3)


def notes(meta):
    lines = [meta["description"], ""]
    if meta.get("sources"):
        lines += ["המקורות:"] + [f"- {s['title']}: {s['url']}" for s in meta["sources"]]
    return "\n".join(lines) + "\n"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    mock = "--mock" in sys.argv
    ep, out_dir = pathlib.Path(args[0]), pathlib.Path(args[1])
    meta = json.loads((ep / "meta.json").read_text(encoding="utf-8"))
    voices = {k: s["voice"] for k, s in CFG["speakers"].items()}
    voices.update(meta.get("voices", {}))
    turns = parse_script(ep / "script-tts.txt")
    chunks = chunk(turns)
    print(f"{ep.name}: {len(turns)} turns, {sum(words(t) for _, _, t in turns)} words, "
          f"{len(chunks)} TTS requests, voices {voices}", flush=True)
    tmp = pathlib.Path(tempfile.mkdtemp())
    wavs = []
    for i, c in enumerate(chunks, 1):
        wav = tmp / f"req{i:02d}.wav"
        synth(c, voices, wav, mock)
        n_words, secs = sum(words(t) for _, _, t in c), duration(wav)
        print(f"  request {i}/{len(chunks)}: {n_words} words -> {secs:.0f}s audio", flush=True)
        cap = TTS.get("output_token_limit", 16384) / TTS.get("audio_tokens_per_second", 32)
        if not mock and (secs < n_words * TTS.get("min_seconds_per_word", 0.45) or secs >= 0.97 * cap):
            print(f"::warning::request {i}: {secs:.0f}s of audio for {n_words} words; the audio may be "
                  f"cut off (expected about {n_words * 0.52:.0f}s, assumed output cap {cap:.0f}s)", flush=True)
        wavs.append(wav)
        if not mock and i < len(chunks):
            time.sleep(TTS["pause_seconds"])
    out_dir.mkdir(parents=True, exist_ok=True)
    mp3 = out_dir / f"{CFG['file_prefix']}-{ep.name}.mp3"
    secs = master(wavs, mp3, meta["title"])
    info = {"file": mp3.name, "bytes": mp3.stat().st_size, "duration_seconds": round(secs),
            "tts_settings": "minimal" if FALLBACKS else "full", "tempo": TTS.get("tempo", 1.0)}
    (out_dir / "episode.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "notes.md").write_text(notes(meta), encoding="utf-8")
    print(f"done: {mp3.name}, {secs / 60:.1f} min, {info['bytes'] / 1e6:.1f} MB", flush=True)
    limit = CFG.get("script", {}).get("max_minutes", 12)
    if secs > limit * 60 and not mock:
        print(f"::warning::episode length {secs / 60:.1f} min is over the {limit}-minute limit", flush=True)


if __name__ == "__main__":
    main()
