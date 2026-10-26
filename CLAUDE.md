# רגע של משפט – production manual for Claude

Daily Hebrew legal podcast "רגע של משפט" (A Moment of Law) with two AI hosts, Omri (male) and
Michal (female). The owner is an Israeli commercial litigator. Talk to him in Hebrew; when
guiding him in Hebrew, put any English (UI labels, terms) on its own line.

Pipeline: Claude writes `episodes/<YYYY-MM-DD>/{script.txt, script-tts.txt, meta.json}` and
pushes to `main`. That triggers `.github/workflows/produce.yml`, which generates the audio with
Gemini TTS (voices and styles in `podcast.json`), masters an MP3, attaches it to the release
`ep-<folder>`, and rebuilds `docs/feed.xml` from episodes whose `meta.json` has `"publish": true`.

## Owner feedback on the first beta (26.10.2026) – the bar to clear

The beta (`episodes/2026-10-26-beta/`) was judged boring. Do NOT imitate its style. Its faults:
hosts sounded gloomy, slow and monotone; no chemistry, they just read texts; punchlines fell
flat; far too much technical detail (costs, security deposits, the court expert's name, every
argument and piece of evidence, all six respondents); not funny enough.
What he wants: light, flowing, fun; a story told with humour; two hosts who react to each other.

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
   - Prefer decisions with a story (a conflict people can picture). Avoid cases where humour
     would land on vulnerable private people (minors, illness, bereavement).
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
4. **Write `script.txt`** (rules below). Hard limit: **1,400 spoken words** (labels excluded);
   episodes must not exceed 12 minutes. Shorter and punchier is better than complete.
5. **Write `script-tts.txt`**: the same turns, with delivery directions (rules below).
6. **Write `meta.json`**: `title`, `date`, `publish` (false unless the owner said to publish),
   `description` (one paragraph, ending with the AI and not-legal-advice disclaimer), and
   `sources` (title + Nevo link for each decision).
7. **QA before pushing** (all must pass):
   - Every case number, court, judge, party name and date in the script appears verbatim in the
     full text (allowing for Hebrew spelling of Latin names).
   - The holding and outcome match the operative part of each decision; nothing invented; no
     party allegation presented as a finding.
   - Both decisions include the mandatory spoken elements.
   - Funny enough? Each decision has at least three real jokes, and the hosts react to each
     other rather than taking turns reading. If not, rewrite before pushing.
   - Word count ≤ 1,400; every line starts with `עמרי` or `מיכל`; `script.txt` has no
     parentheses, emojis, headings, Markdown or tags; `script-tts.txt` contains no digits.
8. **Publish to GitHub**: commit to `main` and push, which starts the workflow. Wait for it and
   check the release with REST calls (`gh api repos/momentoflaw/a-moment-of-law/...`; GitHub
   GraphQL is blocked from Claude sessions, so `gh run list` and `gh release list` fail).
   Never commit MP3 files.
9. **Deliver**: email eladmoshe1992@gmail.com (subject `רגע של משפט | <date> | <title>`) with the
   release link, the two decisions with their Nevo links (the appendix), and the script.

## Script rules

- One turn per line: `עמרי: ...` or `מיכל: ...`. Omri uses masculine forms, Michal feminine.
  Spoken dialogue only in `script.txt`.
- Shape: cold open with banter and the AI disclaimer, a fake sponsor line, decision 1,
  a short bridge, decision 2, a quick outro with one takeaway per decision, and the sign-off
  `זה היה רגע של משפט`.
- AI disclaimer at the start of every episode: the show is written and recorded entirely by AI
  and keeps improving, and if listeners hear something absurd (house example: a contract formed
  when the offer went into the green bin and the acceptance came back in the orange bin) it may
  not have happened. Keep the core, vary the absurd example, keep it quick.
- Mandatory spoken elements for each decision, woven in naturally: case number, court, judge(s)
  (a registrar is `הרשם, השופט ...`), the main parties only (not every respondent), and the
  decision date.
- Tell each decision as a story: a hook, who wants what from whom, the twist, what the court
  did and the one or two reasons that carry it, and the practical takeaway. Leave out costs,
  security deposits, fees, expert names, procedural history, side issues, and arguments or
  evidence that are not the heart of the decision.
- Audience: Israeli lawyers and business people, but accessible to non-lawyers. When a legal or
  Aramaic term appears, the other host translates it, briefly and funnily.

## Hosts, chemistry and humour

Voices: pair A (Omri `Algieba`, Michal `Leda`), chosen by the owner on 26.10.2026.

Full character bible (background, education, culture, habits, catchphrases, running gags):
`hosts.md`. Read it before writing; use one or two details per episode, never all of them.

- **Omri, the law nerd.** A genuine legal geek with a warm, articulate radio voice. Fluent and
  precise, speaks in well-formed sentences, reads Supreme Court decisions for fun late at night,
  lights up at elegant reasoning, procedural details and Aramaic, gently corrects terminology.
  Endearing, never arrogant. Has no idea what anything costs.
  Recurring bit, "הפינה של עמרי": one short line from the decision that he finds beautiful,
  read with real emotion.
- **Michal, the bottom line.** Young, giggly, mischievous and cynical, with a business brain.
  Sees every decision through cost, risk and "what do I do tomorrow morning". Brings Omri down
  to earth, teases his enthusiasm, laughs easily (often at him), and translates legalese into
  business and everyday language (contractors, Yad2, the building WhatsApp group, asking for a
  raise). Impatient with long reasoning, sharp when it counts.
  Recurring bit, "השורה התחתונה של מיכל": the business lesson in one sentence.
- Dynamic: Omri brings the why (law as an art), Michal brings the so-what (money and real life).
  Each decision gets at least one Omri enthusiasm spike that Michal deflates, and ends with her
  bottom line.
- Real interaction: short turns, reactions ("רגע, מה?"), finishing each other's sentences,
  teasing, callbacks to earlier jokes, a running gag. Avoid long monologues; no turn over
  about 45 words.
- The comic engine: high-register legal doctrine applied with tragic seriousness to petty
  Israeli daily life (the supermarket queue, the building committee WhatsApp group, the gym
  membership that renews itself), and escalation in threes.
- Inspired by the mechanics of Taycher & Zerachowicz: pure absurd comedy rather than message
  satire, total commitment to an absurd premise, mock-heroic gravity, pompous register on cheap
  subjects, sacred-secular register mixing, lines that sound wise and then deflate, fake radio
  formats (sponsor spots, a faux lecture, a listener question). Never use their characters,
  names, quotes or jokes (including their lawyer character). All humour is original.
- Humour targets procedure, bureaucracy and universal habits, never the parties or the judges.
  No ridicule of named people, and no personal hardship details.
- Israeli TV, music and daily-life references are welcome. Songs by name or allusion only,
  never quoted lyrics. Topical references only after checking them that week. Black humour is
  allowed, but never at the expense of victims, bereaved families or hostages, and no partisan
  side-taking.

## TTS rules (`script-tts.txt`)

- Same turns as `script.txt`. Each line may carry a delivery direction in English square
  brackets after the speaker name, used as that turn's style:
  `מיכל [laughing, teasing]: ...`, `עמרי [mock-solemn announcer]: ...`. Use them on most lines,
  especially setups and punchlines. Delivery overall: lively, warm, brisk, smiling, never gloomy.
- Vocal tags inside the text: `<laugh>` 2–4 times per episode where something is genuinely
  funny, `<short pause>` right before a punchline. No other tags.
- Write numbers, dates, years, percentages, sums and case numbers in Hebrew words, e.g.
  `21983-10-26` → `עשרים ואחד אלף תשע מאות שמונים ושלוש, עשר, עשרים ושש`;
  `25 באוקטובר 2026` → `עשרים וחמישה באוקטובר, אלפיים עשרים ושש`.
- Expand abbreviations: בע"מ → בערבון מוגבל, ע"א → ערעור אזרחי, חו"ל → חוץ לארץ.
- Add nikud to surnames, Aramaic and ambiguous words, e.g. כֻּלֵּי עָלְמָא, קַל וָחֹמֶר,
  מַשּׂוֹא פָּנִים, הַנּוֹשָׁה, עֲרֻבָּה, אִמְרַת אַגַּב, פְּסִיקְתָּא.
- Latin company names may stay in Latin. Use `...` to hand a sentence over to the other host.
- Voice samples to compare: `episodes/2026-10-26-voices-a|b|c/`.
