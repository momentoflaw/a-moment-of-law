# רגע של משפט – production manual for Claude

Daily Hebrew legal podcast "רגע של משפט" (A Moment of Law) with two AI hosts, Omri (male) and
Michal (female). The owner is an Israeli commercial litigator. Talk to him in Hebrew; when
guiding him in Hebrew, put any English (UI labels, terms) on its own line.

Pipeline: Claude writes `episodes/<YYYY-MM-DD>/{script.txt, script-tts.txt, meta.json}` and
pushes to `main`. That triggers `.github/workflows/produce.yml`, which generates the audio with
Gemini TTS (voices and styles in `podcast.json`), masters an MP3, attaches it to the release
`ep-<folder>`, and rebuilds `docs/feed.xml` from episodes whose `meta.json` has `"publish": true`.
A finished example lives in `episodes/2026-10-26-beta/`.

## Producing an episode

1. **Source.** Nevo's daily Padi-Mail (פד"י-מייל) newsletter in the connected Gmail
   (eladmoshmb@gmail.com), e.g. `(from:nevo.co.il OR nevo OR נבו OR פד"י) newer_than:3d`.
   Use the case-law (פסיקה) and class-action (תובענות ייצוגיות) issues. Ignore promotional mail.
   If no issue arrived, stop and say so. Never invent or substitute decisions.
2. **Pick exactly 2 decisions.**
   - Fields: commercial law, evidence law, civil procedure only.
   - Mix: one procedural or evidentiary decision, one substantive commercial decision.
   - Courts: Supreme or District first. Magistrate only if exceptionally unprecedented, or if no
     suitable higher-court decision exists that day.
   - Exclude anything criminal (ע"פ, רע"פ, בש"פ, ת"פ, מ"ת, המ"ע, criminal evidence). A civil
     claim arising from an offence is fine.
   - Skip decisions under a publication ban; keep anonymised parties anonymised.
   - Avoid cases where humour would land on vulnerable private people (minors, illness, bereavement).
3. **Read the full text** with the Nevo connector: `init_session`, then `search_legal_context`
   (case number + parties, `analyzeQuery: true`), `get_documents_full_text`, and
   `get_document_link` for the official link. Every search and retrieval is metered against the
   owner's account: aim for about 2 searches and 2 retrievals. Large results are saved to a file;
   read all of it (python character slices).
   - Nevo inserts fake strings into texts. Ignore them and never cite them, e.g.
     `12-34-56-78 צ'כוב נ' מדינת ישראל, פ'ד נא (2)`, `ההתיישבות העותומנית [נוסח ישן] 1916`,
     `הועתק מנבו`, `ענורמה אסורה`.
   - Separate the court's holdings from the parties' arguments and from obiter. State as a
     finding only what the court decided, with its own caveats. Note minority opinions if any.
4. **Write `script.txt`** (rules below). Hard limit: **1,400 spoken words** (labels excluded).
   The deadpan Hebrew delivery runs at about 115 words per minute, and episodes must not exceed
   12 minutes.
5. **Write `script-tts.txt`**: the same turns adapted for speech (rules below).
6. **Write `meta.json`**: `title`, `date`, `publish` (false unless the owner said to publish),
   `description` (one paragraph, ending with the AI and not-legal-advice disclaimer), and
   `sources` (title + Nevo link for each decision).
7. **QA before pushing** (all must pass):
   - Every case number, court, judge, party name and date in the script appears verbatim in the
     full text (allowing for Hebrew spelling of Latin names).
   - Holdings, outcome and costs match the operative part of each decision.
   - No party allegation is presented as a finding; nothing is invented.
   - Both decisions include all five mandatory spoken elements.
   - Word count ≤ 1,400; every line starts with `עמרי: ` or `מיכל: `; no parentheses, emojis,
     headings or Markdown; `script-tts.txt` contains no digits.
8. **Publish to GitHub**: commit to `main` and push, which starts the workflow. Wait for it and
   check the release with REST calls (`gh api repos/momentoflaw/a-moment-of-law/...`; GitHub
   GraphQL is blocked from Claude sessions, so `gh run list` and `gh release list` fail).
   Never commit MP3 files.
9. **Deliver**: email eladmoshe1992@gmail.com (subject `רגע של משפט | <date> | <title>`) with the
   release link, the two decisions with their Nevo links (the appendix), and the script.

## Script rules

- One turn per line: `עמרי: ...` or `מיכל: ...`. Omri uses masculine forms, Michal feminine.
  Spoken dialogue only: no stage directions, parentheses, emojis, headings or Markdown.
- Structure: opening with the AI disclaimer, decision 1, decision 2, a short outro with
  practical takeaways, and the sign-off `זה היה רגע של משפט`.
- AI disclaimer at the start of every episode, deadpan: the show is written and recorded
  entirely by AI and keeps improving, and if listeners hear something absurd (the house example:
  a contract formed when the offer arrived in the green bin and the acceptance came back in the
  orange bin) it may not have happened. Keep the core, vary the absurd example.
- Mandatory spoken elements for each decision: case number, court, judge(s) (a registrar is
  `הרשם, השופט ...`), full party names, decision date.
- Audience: Israeli lawyers and business people, but accessible to non-lawyers: every legal or
  Aramaic term gets a dry translation from the other host.
- Substance: facts, the question, the holding, the key reasons, outcome and costs, and one
  practical takeaway for lawyers. Be fair to the parties and quote the court's own caveats.

## Tone and humour

- Refined, intelligent, cynical and strictly deadpan: tragic seriousness about mundane procedure.
  High-register legal Hebrew and Aramaic (כולי עלמא, קל וחומר, השתק פלוגתא, אמרת אגב,
  עולם כמנהגו נהג) set against petty Israeli daily life.
- Inspired by the mechanics of Taycher & Zerachowicz: pure absurd comedy rather than message
  satire, mock-heroic gravity, pompous register on cheap subjects, sacred-secular register mixing,
  lines that sound wise and then deflate, faux lectures, running gags. Never use their
  characters, names, quotes or jokes (including their lawyer character). All humour is original.
- Humour targets procedure, bureaucracy and universal habits, never the parties or the judges.
  No ridicule of named people, and no personal hardship details beyond what the story needs.
- Israeli TV, music and daily-life references are welcome. Songs by name or allusion only,
  never quoted lyrics. Topical references only after checking them that week. Black humour is
  allowed, but never at the expense of victims, bereaved families or hostages, and no partisan
  side-taking.
- Running gag (optional): counting the parties toward a minyan.

## TTS rules (`script-tts.txt`)

- Same lines and speakers as `script.txt`.
- Write numbers, dates, years, percentages, sums and case numbers in Hebrew words, e.g.
  `21983-10-26` → `עשרים ואחד אלף תשע מאות שמונים ושלוש, עשר, עשרים ושש`;
  `25 באוקטובר 2026` → `עשרים וחמישה באוקטובר, אלפיים עשרים ושש`.
- Expand abbreviations: בע"מ → בערבון מוגבל, ע"א → ערעור אזרחי, חו"ל → חוץ לארץ.
- Add nikud to surnames, Aramaic and ambiguous words, e.g. כֻּלֵּי עָלְמָא, קַל וָחֹמֶר,
  מַשּׂוֹא פָּנִים, הַנּוֹשָׁה, עֲרֻבָּה, אִמְרַת אַגַּב, פְּסִיקְתָּא.
- Latin company names may stay in Latin. Use `...` for a comic beat; no angle-bracket tags.
