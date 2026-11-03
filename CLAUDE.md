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

## Owner feedback on the first new-format episode (30.10.2026)

Better overall, and he likes the humour style. To fix:
- The opening announced "the two decisions we read today". Instead, state the fixed format:
  every day, one procedural decision and one from substantive law.
- Case numbers must be read digit by digit (see TTS rules).
- Too many jokes: nearly every other line was a punchline, which felt forced. Dose the humour.
- The football references were good but too many: at most two per episode. Use a wider range of
  references: Israeli culture, TV, music and this week's news (checked).
- Arkia's outcome got lost. Say plainly what the court ordered: leave granted? appeal allowed?
  sent back? claim dismissed?
- The facts were read sentence by sentence, like a ritual. Tell them in flowing paragraphs with
  natural cut-ins, so it does not sound pre-scripted.

## Owner feedback on the 1.11.2026 episode (3.11.2026)

- Too fast. Delivery is now unhurried: `tts.tempo` is 1.0 (no speed-up in mastering), the voice
  styles ask for a relaxed pace, and `produce.py` adds `tts.pace` to every turn's direction.
  Never direct a turn to be fast, brisk, rapid or rushed.
- Uninteresting details, e.g. the deadline for filing the amended settlement and the date the
  judge set for her own follow-up. Every detail must earn its place (see Script rules).
- The class-action settlement decision met the selection rules but was not interesting: an
  interim step in which the court asked for more paperwork. Hence the interest test in step 2.
- Wording: a court or judge `קבע` (or `פסק`, `הורה`, `דחה`, `קיבל`), never `אמר`.

## Owner feedback on the 3.11.2026 episode (3.11.2026)

- Never put the owner's production notes into the dialogue (the 3.11 cold open joked that
  listeners complained the hosts talk too fast). His notes change how the show is made, not
  what the hosts talk about.
- Fake sponsors must not be real businesses or legal entities. Before using a name, run a web
  search for the exact name, alone, with the product and with `בע"מ`; if anything real turns
  up, pick another. Prefer plainly invented, absurd products.
- Michal's bottom line must come from the decision's holding. On 3.11 her line on the
  procedural decision was a general tip about public contracts, unrelated to the ruling on
  amending pleadings. For a procedural or evidentiary decision, her bottom line is the
  litigation lesson (what to do, or not do, in your own case), in everyday language.
- Humour: he liked the corridor-and-parlor joke (the judge's own allusion to Pirkei Avot turned
  against the facts: no corridor and no parlor, just a skeleton), and liked the house-committee
  comparison less. Prefer humour that grows from the decision's own words and facts over stock
  comparisons, and rest the house-committee trope.
- Pronunciation: רבותא is revota, not revuta (`רְבוֹתָא` in `script-tts.txt`).

## Producing an episode

0. **Ask first.** The owner's standing rule (2.11.2026): ask him before producing each new episode,
   and produce only after he says yes. In the question, include his Claude usage for the week if it
   can be read (claude.ai/settings/usage through a browser on his computer, one attempt); otherwise
   give him that link. Episodes stay unpublished (`"publish": false`) until he says otherwise.
1. **Source.** Nevo's newsletters in the connected Gmail (eladmoshmb@gmail.com). They come from
   `no-reply@nevopublishing.co.il`, not nevo.co.il: search `from:nevopublishing.co.il newer_than:3d`.
   Use every case-law issue (subject `Padi-Mail - NNN/26 - Psika`) and class-action issue
   (`נבו ייצוגיות - גיליון NNN`) that arrived since the last produced episode (the last folder
   under `episodes/`; widen `newer_than` if needed), so there is more to choose from, and skip
   decisions already logged in `continuity.md`. Skip legislation (`Hakika`) and anything marked
   `(פרסומת)`.
   If no issue arrived, stop and say so. Never invent or substitute decisions.
   An issue runs to 60–90K characters, so `get_message` saves it to a file: extract
   `plaintextBody` with python, strip the URLs, and list the decisions (Psika: the lines ending in
   `(court; judge; dd/mm/yy)`; ייצוגיות: the "עדכונים בתיקים" section, which holds judgments and
   decisions, whereas "בקשות חדשות" are new filings, i.e. allegations only).
2. **Pick exactly 2 decisions.**
   - Fields: commercial and consumer law (class actions included), evidence law, civil
     procedure, and civil decisions where law meets technology. Nothing criminal (see below).
   - Mix: one procedural or evidentiary decision, one substantive decision (commercial or
     consumer). A class-action certification decision fills the procedural slot when it turns on
     the certification requirements, and the substantive slot when it turns on the cause of
     action.
   - Courts: Supreme or District first. A Magistrate decision may take a slot when its story is
     clearly better than the best higher-court candidate for that slot (owner, 3.11.2026: a
     strong Magistrate story beats a dry District decision), when it is exceptionally
     unprecedented, or when no suitable higher-court decision exists that day.
   - Exclude anything criminal (ע"פ, רע"פ, בש"פ, ת"פ, מ"ת, המ"ע, criminal evidence). A civil
     claim arising from an offence is fine.
   - Skip decisions under a publication ban; keep anonymised parties anonymised.
   - **Interest test** (owner, 3.11.2026). Shortlist 4–6 candidates that pass the rules above
     and score each 0–2 on: (a) it decides a real dispute: a judgment, an appeal or leave
     decided, a claim struck out or let in, an award; (b) a rule a litigator or a business
     person can use tomorrow morning; (c) a story: who wants what from whom, a twist,
     recognisable parties or places, real stakes; (d) surprise: the expected side loses, or the
     court intervenes or criticises. Add the owner's preference points below, then take the top
     procedural and the top substantive candidate.
   - **The owner's preferences** (3.11.2026), added to the interest score:
     - +2 where law meets technology, especially AI: algorithms, platforms and apps, data and
       privacy, digital assets, AI-generated content, AI used in litigation. To find these,
       scan every issue for terms such as בינה מלאכותית, AI, אלגוריתם, ChatGPT, אפליקציה,
       פלטפורמה, פרטיות, מאגר מידע, סייבר, קריפטו, דיגיטלי.
     - +2 a class action at a deciding stage: a motion to certify granted or denied, or a
       certified class action allowed or dismissed. Not new filings, settlements or withdrawals.
     - +1 consumer law, or +2 instead when it is a Supreme Court consumer judgment.
     - Procedural or evidentiary slot: +2 for a Supreme Court decision.
   - Do not pick: interim or case-management decisions (deadlines, amended filings, reports,
     scheduling, "fix it and come back"); approvals of agreed settlements or withdrawals with no
     contested legal question; decisions that turn only on credibility or facts with no lesson.
   - Prefer decisions with a story (a conflict people can picture). Avoid cases where humour
     would land on vulnerable private people (minors, illness, bereavement).
   - Keep the shortlist: the delivery email lists the runners-up, one line each with why they
     lost, so the owner can steer the selection.
3. **Read the full text** with the Nevo connector: `init_session`, then `search_legal_context`
   (case number + parties, `analyzeQuery: true`), `get_documents_full_text`, and
   `get_document_link` for the official link. Every search and retrieval is metered against the
   owner's account: aim for about 2 searches and 2 retrievals. Large results are saved to a file;
   read all of it (python character slices). A search by case number with `analyzeQuery` often
   returns every chunk of the decision (and of earlier decisions in the same case): when the
   chunkIds run unbroken from the header to the operative part and signature, merge them (they
   overlap) and skip `get_documents_full_text`. `get_document_link` gives the
   `Highlighter2.aspx?verdictid=` link for `meta.json`.
   - Nevo inserts fake strings into texts. Ignore them and never cite them, e.g.
     `12-34-56-78 צ'כוב נ' מדינת ישראל, פ'ד נא (2)`, `ההתיישבות העותומנית [נוסח ישן] 1916`,
     `הועתק מנבו`, `ענורמה אסורה`.
   - Separate the court's holdings from the parties' arguments and from obiter. State as a
     finding only what the court decided, with its own caveats. Note minority opinions if any.
4. **Write `script.txt`** (rules below). Hard limit: **1,250 spoken words** (labels excluded);
   episodes must not exceed 12 minutes. At the relaxed pace the TTS speaks about 105–115 words a
   minute, so aim for 1,000–1,150. Shorter and punchier is better than complete.
   Before writing, check the show's memory in `continuity.md` (see "Show memory" below): read
   the last five entries, and grep the rest for today's case numbers, parties and topics.
   Also check, with one web search of that day's Hebrew sports news, whether Maccabi Tel Aviv's
   football team (not basketball) had a notable win or won a title in the last day or two (see
   Michal below).
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
   - Any callback to an earlier episode matches its `continuity.md` entry.
   - Any sports fact (opponent, score, competition, scorers, title) matches that day's news.
   - Humour in measure: two or three real jokes per decision, not a punchline every other line;
     at most two football references; at least one other cultural or topical reference. The
     hosts react to each other rather than taking turns reading. If not, rewrite before pushing.
   - The facts flow in paragraphs, and each decision's outcome is stated plainly in its own turn.
   - No procedural dates other than the decision dates; no deadlines, follow-up dates or sums
     that do not carry the story. Judges `קבע`, never `אמר`. No direction asks for speed.
   - Nothing in the dialogue refers to the owner's feedback or to how the show is made, beyond
     the AI disclaimer. The fake sponsor's name was searched and is not a real business or
     entity. Each of Michal's bottom lines follows from that decision's holding.
   - Word count ≤ 1,250; every line starts with `עמרי` or `מיכל`; `script.txt` has no
     parentheses, emojis, headings, Markdown or tags; `script-tts.txt` contains no digits.
8. **Publish to GitHub**: add the episode's entry at the end of `continuity.md`, commit it with
   the episode files to `main` and push, which starts the workflow. Wait for it and
   check the release with REST calls (`gh api repos/momentoflaw/a-moment-of-law/...`; GitHub
   GraphQL is blocked from Claude sessions, so `gh run list` and `gh release list` fail).
   Never commit MP3 files.
9. **Deliver**: email eladmoshe1992@gmail.com (subject `רגע של משפט | <date> | <title>`) with the
   release link, the two decisions with their Nevo links (the appendix), the runners-up (one
   line each, why they lost), and the script.

## Script rules

- One turn per line: `עמרי: ...` or `מיכל: ...`. Omri uses masculine forms, Michal feminine.
  Spoken dialogue only in `script.txt`.
- Shape: cold open with banter, the AI disclaimer and the format line (every day, one procedural
  decision and one from substantive law; never "the two decisions we read today"), a fake
  sponsor line (an invented product, checked not to be a real business), decision 1, a short bridge, decision 2, a quick outro with one takeaway per
  decision, and the sign-off `זה היה רגע של משפט`.
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
- Every detail must earn its place: if a listener would not miss it, cut it. The only
  procedural date spoken is the decision date. Leave out deadlines given to the parties (e.g.
  file an amended settlement by X), the next hearing, the date a judge set for her own
  follow-up, the dates of earlier filings and hearings, and sums that do not carry the story.
  A year inside the story may stay when it is the point (a building closed since 2018).
- Courts and judges `קבע`, `פסק`, `הורה`, `דחה` or `קיבל`; never `אמר`. A verbatim quote is
  introduced with `כתב` or `כתבה`.
- Facts in flowing paragraphs: the host telling the story speaks in short paragraphs (two to four
  connected sentences, up to about 60 words), and the other cuts in naturally with a reaction, a
  question or the end of a sentence. No sentence-by-sentence ping-pong when laying out the facts.
- The outcome gets its own clear moment: one host states plainly what the court ordered (e.g.
  leave to appeal granted, appeal allowed, the award cancelled and the claim dismissed; or the
  case sent back), never right after a punchline or folded into a joke. Michal's bottom line,
  the practical lesson of the holding, comes after it, separately.
- Audience: Israeli lawyers and business people, but accessible to non-lawyers. When a legal or
  Aramaic term appears, the other host translates it, briefly and funnily.

## Hosts, chemistry and humour

Voices: pair A (Omri `Algieba`, Michal `Leda`), chosen by the owner on 26.10.2026.

Full character bible (background, education, culture, habits, catchphrases, running gags):
`hosts.md`. Read it before writing. Background details are seasoning, not a quota: use one
only when it grows naturally out of the decision or the conversation, and many episodes will use
none. Never force one in. What every episode has is the personalities, the dynamic and the
recurring segments.

- **Omri, the law nerd.** A genuine legal geek with a warm, articulate radio voice. Fluent and
  precise, speaks in well-formed sentences, reads Supreme Court decisions for fun late at night,
  lights up at elegant reasoning, procedural details and Aramaic, gently corrects terminology.
  Endearing, never arrogant. Has no idea what anything costs.
  Recurring bit, "הפינה של עמרי": one short line from the decision that he finds beautiful,
  read with real emotion.
- **Michal, the bottom line.** Young, giggly, mischievous and cynical, with a business brain.
  She studied law and knows commercial law well, but on principle never sat the bar exam; she is
  by-the-book with money and sharp on investments (for metaphors, never investment advice).
  A die-hard Maccabi Tel Aviv football fan: the day after a notable or unusual win, or a title,
  she brings it up briefly, usually in the cold open, with verified facts only.
  Sees every decision through cost, risk and "what do I do tomorrow morning". Brings Omri down
  to earth, teases his enthusiasm, laughs easily (often at him), and translates legalese into
  business and everyday language (contractors, Yad2, asking for a raise). Impatient with long
  reasoning, sharp when it counts.
  Recurring bit, "השורה התחתונה של מיכל": the practical lesson of the holding in one sentence:
  the business lesson for a substantive decision, the litigation lesson for a procedural or
  evidentiary one.
- Dynamic: Omri brings the why (law as an art), Michal brings the so-what (money and real life).
  Each decision gets at least one Omri enthusiasm spike that Michal deflates, and ends with her
  bottom line.
- Real interaction: quick banter, reactions ("רגע, מה?"), finishing each other's sentences,
  cut-ins, teasing, callbacks to earlier jokes. Storytelling comes in paragraphs (see Script
  rules). Avoid monologues; no turn over about 60 words.
- Dose the humour: two or three real jokes per decision, with straight stretches between them so
  the story breathes. Not every line is a punchline. Football: at most two references per
  episode. Vary the references: Israeli TV, music, culture and this week's news (checked).
- The comic engine: high-register legal doctrine applied with tragic seriousness to petty
  Israeli daily life (the supermarket queue, the gym membership that renews itself), and
  escalation in threes. The best jokes grow from the decision's own words and facts (3.11: the
  judge's "corridor and parlor" for a building that is only a skeleton).
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

## Show memory (`continuity.md`)

Omri and Michal remember what they have covered. `continuity.md` logs every episode: for each
decision the case number, court, judges, date, main parties, a one-line holding, topic keywords
and the Nevo link; lines worth calling back; and canon, the facts about the hosts said on air.

- When today's decision connects to one covered before (the same doctrine, an opposite result,
  the same parties, or a later stage of the same case), the hosts may bring the earlier one up
  as a short anecdote, recapping it in a sentence so a new listener can follow. Only when it
  adds something; at most one or two per episode; facts only as logged.
- If a decision covered before was reversed or changed on appeal, say so on air.
- Canon binds: once a fact about a host is said on air, it stays true. Log new facts.

## TTS rules (`script-tts.txt`)

- Same turns as `script.txt`. Each line may carry a delivery direction in English square
  brackets after the speaker name, used as that turn's style:
  `מיכל [laughing, teasing]: ...`, `עמרי [mock-solemn announcer]: ...`. Use them on most lines,
  especially setups and punchlines. Delivery overall: lively, warm and smiling, never gloomy, at
  a relaxed, unhurried pace with natural pauses (the owner found the 1.11 episode too fast).
  Never write fast, brisk, rapid, rushing or speeding up in a direction.
- Vocal tags inside the text: `<laugh>` 2–4 times per episode where something is genuinely
  funny, `<short pause>` right before a punchline. No other tags.
- Write numbers, dates, years, percentages and sums in Hebrew words, e.g.
  `25 באוקטובר 2026` → `עשרים וחמישה באוקטובר, אלפיים עשרים ושש`.
- Read case numbers digit by digit, every group (the owner's rule: 17254 is
  `אחד שבע שתיים חמש ארבע`), e.g. `57113-02-26` → `חמש שבע אחד אחד שלוש, אפס שתיים, שתיים שש`.
- Expand abbreviations: בע"מ → בערבון מוגבל, ע"א → ערעור אזרחי, חו"ל → חוץ לארץ.
- Add nikud to surnames, Aramaic and ambiguous words, e.g. כֻּלֵּי עָלְמָא, קַל וָחֹמֶר,
  מַשּׂוֹא פָּנִים, הַנּוֹשָׁה, עֲרֻבָּה, אִמְרַת אַגַּב, פְּסִיקְתָּא, רְבוֹתָא (revota).
- Latin company names may stay in Latin. Use `...` to hand a sentence over to the other host.
- Voice samples to compare: `episodes/2026-10-26-voices-a|b|c/`.
