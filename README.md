# Advanced prompt engineering for journalists — starter kit

A starter repo for the [Knight Center](https://knightcenter.utexas.edu/) MOOC on using AI coding tools from the command line. Fork this repo, clone your fork, `cd` into it, and run `claude`. Everything you need for the four modules is already here.

**Course site:** [mooc.amditis.tech](https://mooc.amditis.tech)

---

### Instructor

**Joe Amditis** | [Center for Cooperative Media](https://centerforcooperativemedia.org), Montclair State University

[GitHub](https://github.com/jamditis) | [Substack](https://strugglestreet.substack.com) | [Twitter](https://twitter.com/jsamditis)

---

## What this repo is

Your workspace for all four modules. By the end of the course, it'll be a working AI-assisted journalism toolkit you've filled in with your own beat details — documented, version-controlled, and shareable.

- A **context file scaffold** (`CLAUDE.md`) with teaching comments and a fully worked example
- **Memory and lessons files** (`MEMORY.md`, `LESSONS.md`) showing the patterns from video A2
- **Real Claude Code skills** (`skills/`) with YAML frontmatter — the shape from video B1
- **Slash commands** (`.claude/commands/`) for beat briefings, SIFT-based claim checks, and cross-model review
- **A one-way-door hook** (`.claude/hooks.json`) — the guardrail pattern
- **A minimal plugin skeleton** (`plugin/`) — the shape from video B2
- **Staged pipeline scripts** (`scripts/pipeline/`) — the fetch → clean → process → save pattern
- **A GitHub Actions workflow** (`.github/workflows/weekly-digest.yml`) — the cloud-detect side of the hybrid pattern
- **Module 4 documentation** (`docs/context-management.md`, `docs/cross-model-review.md`, `docs/four-questions.md`)
- **A worked mini example** (`examples/mamdani-mini/`) — the shape of the video B1 pipeline demo with synthetic data
- **Sample journalism documents** (`sample-docs/`) — fictional Greenfield city council beat fixtures
- **Stubs for Codex and Gemini users** (`AGENTS.md`, `GEMINI.md`) — if you're not using Claude

Everything in the repo maps to a specific module and video in [docs/module-map.md](docs/module-map.md). Start there if you want the index.

## Getting started

### 1. Fork this repo

Click **Fork** at the top right of the GitHub page. That gives you your own copy you can push to freely.

### 2. Clone your fork

```bash
git clone https://github.com/YOUR-USERNAME/mooc-starter-kit.git
cd mooc-starter-kit
```

Replace `YOUR-USERNAME` with your GitHub username.

### 3. Install one AI CLI tool

You need Node.js (version 20+) and one of these:

| Tool | Install | Cost |
|------|---------|------|
| **Claude Code** | `npm install -g @anthropic-ai/claude-code` | Requires a Claude subscription or API key |
| **Gemini CLI** | `npm install -g @google/gemini-cli` | Free tier: 1,000 requests/day with a Google account |
| **Codex CLI** | `npm install -g @openai/codex` | Requires an OpenAI API key |

The course exercises are shown in Claude Code. The patterns work in all three tools. If you're using Codex, see `AGENTS.md`. If you're using Gemini, see `GEMINI.md`.

### 4. Run it

```bash
cd mooc-starter-kit
claude
```

Your first session should be boring on purpose — say hi, type `/init` (if you're in Claude Code) and see what it does, read `CLAUDE.md`, and then pick up the [Module 1 exercise](https://mooc.amditis.tech/module-1/) on the course site.

## Which module uses what

| Module | Week | Read this | Work with these files |
|--------|------|-----------|------------------------|
| **Module 1 — From chat window to command line** | 1 | Videos A1, A2 | `CLAUDE.md`, `MEMORY.md`, `LESSONS.md`, `examples/worked-claude-md/`, `sample-docs/` |
| **Module 2 — Custom skills, commands, hooks, plugins** | 2 | Videos B1, B2 | `skills/`, `.claude/commands/`, `.claude/hooks.json`, `plugin/` |
| **Module 3 — Automation, pipelines, triggered workflows** | 3 | Videos C1, C2 | `scripts/pipeline/`, `.github/workflows/`, `examples/mamdani-mini/` |
| **Module 4 — Advanced prompting patterns** | 4 | Videos D1, D2, D3, D4 | `docs/context-management.md`, `docs/cross-model-review.md`, `docs/four-questions.md` |
| **Final project** | 4 | — | Build something on your beat using anything in the kit |

See [docs/module-map.md](docs/module-map.md) for the full file-to-video index.

## What's in each folder

```
mooc-starter-kit/
|
|-- CLAUDE.md                   Project context scaffold (Module 1)
|-- MEMORY.md                   Memory index: four memory types
|-- LESSONS.md                  Rolling log where corrections become rules
|-- AGENTS.md                   Codex users read this
|-- GEMINI.md                   Gemini users read this
|
|-- sample-docs/                Greenfield city council beat fixtures
|   |-- council-minutes-excerpt.md
|   |-- press-release-park-closure.md
|   |-- interview-notes-martinez.md
|   |-- tip-email.md
|   |-- viral-claim-example.md
|   |-- sample-article.html
|   +-- sample-transcript.txt
|
|-- .claude/                    Commands and hooks Claude Code auto-loads
|   |-- commands/
|   |   |-- beat-brief.md       /beat-brief
|   |   |-- cross-review.md     /cross-review
|   |   +-- verify-claim.md     /verify-claim
|   |-- hooks.json              One-way-door guardrail
|   +-- hooks.md                What the hook is for
|
|-- skills/                     Real Claude Code skills (Module 2)
|   |-- newsroom-style/
|   |   +-- SKILL.md
|   +-- first-skill/
|       +-- SKILL.md
|
|-- plugin/                     Minimal plugin skeleton (Module 2)
|   |-- plugin.json
|   +-- skills/
|       +-- beat-brief/
|           +-- SKILL.md
|
|-- scripts/
|   |-- pipeline/               Staged pipeline (Module 3)
|   |   |-- 01-fetch.sh
|   |   |-- 02-clean.sh
|   |   |-- 03-process.sh
|   |   |-- 04-save.sh
|   |   |-- run-all.sh
|   |   +-- README.md
|   +-- legacy/                 The "before" version of the scripts
|       |-- summarize-article.sh
|       |-- batch-process.sh
|       +-- README.md
|
|-- .github/workflows/
|   |-- weekly-digest.yml       Scheduled pipeline (Module 3, video C2)
|   +-- README.md
|
|-- examples/
|   |-- worked-claude-md/       A fully filled-in CLAUDE.md example
|   |   +-- CLAUDE.md
|   |-- mamdani-mini/           The video B1 pipeline shape, synthetic data
|   |   |-- README.md
|   |   |-- sample-data/
|   |   |-- prompts/
|   |   +-- dashboard-skeleton.html
|   +-- rag-archive/            Optional: local RAG over your own docs
|       +-- README.md
|
|-- mcp-configs/                Optional advanced: MCP examples
|   |-- README.md
|   +-- filesystem-example.json
|
|-- docs/
|   |-- module-map.md           File-to-video index
|   |-- context-management.md   Module 4: /effort, /context, /compact, sub-agents
|   |-- cross-model-review.md   Module 4: Copilot CLI and Codex with -p
|   |-- four-questions.md       Module 4: tool selection framework
|   +-- superpowers/specs/      Design docs for the kit itself
|
+-- og-image.png                Social preview
```

## Related repositories

- **[Journalism skills library](https://github.com/jamditis/claude-skills-journalism)** — 50+ pre-built Claude Code skills for journalism (source verification, FOIA requests, data journalism, editorial workflows, newsroom style, web archiving, and more) plus more than a dozen workflow hooks. Browse for ideas or install the whole library.
- **[NICAR 2026: Skills in Codex and Claude](https://github.com/amkessler/nicar2026_skills_in_codex_claude)** — Aaron Kessler's NICAR session repo. Examples of building and using skills across Claude Code and Codex CLI for data journalism.
- **[AI tools for newsrooms](https://github.com/jamditis/tools)** — A curated collection of AI tools and resources for journalists and newsrooms.
- **[skills.amditis.tech](https://skills.amditis.tech)** — Browsable catalog of Joe's skills and plugins, including the ones demoed in the course videos.
- **[tools.amditis.tech](https://tools.amditis.tech)** — Joe's working list of AI tools for journalists.

## License

Course materials are licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). You may share and adapt for any purpose with attribution.

**Attribution:** Joe Amditis, Center for Cooperative Media, Montclair State University. Course hosted by the Knight Center for Journalism in the Americas at the University of Texas at Austin.
