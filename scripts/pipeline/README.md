# Pipeline scripts

Track active work in [MOOC starter kit maintenance](https://github.com/users/jamditis/projects/26).

A staged journalism pipeline: fetch → clean → process → save. Each stage is its own bash script in this folder, and each one only does one thing.

## The stages

| Stage | Script | Owns | Reads from | Writes to |
|-------|--------|------|------------|-----------|
| 1 | `01-fetch.sh` | grabbing the bytes | a source directory | `./work/01-raw/` |
| 2 | `02-clean.sh` | making text safe to feed a model | `./work/01-raw/` | `./work/02-clean/` |
| 3 | `03-process.sh` | the model call and prompt shape | `./work/02-clean/` | `./work/03-processed/` |
| 4 | `04-save.sh` | final artifact and naming | `./work/03-processed/` | `./output/digest-YYYY-MM-DD.md` |

Stages communicate through files in `./work/` (staging) and `./output/` (final), relative to their working directory. The full runner gives each run its own working directory; standalone stages use your current directory.

## Why stages

- **One job per script.** When something breaks, you know which stage owns it.
- **Testable.** You can re-run stage 3 without re-fetching or re-cleaning. The work directory is the cache.
- **Swappable.** Swap `02-clean.sh` for a Python cleaner, or `03-process.sh` for a different model. The contract is the directory layout, not the language.
- **Chainable.** Add a stage 5 (publish to a CMS, post to Slack, append to a sheet) without touching the earlier ones.

This ties to video C1 — "don't write one big script that does everything."

## Run the full pipeline

```bash
cd scripts/pipeline
./run-all.sh
```

That runs 01 → 02 → 03 → 04 against `sample-docs/` by default. Pass a different source directory as the first argument:

```bash
./run-all.sh /path/to/my/beat-docs
```

The full runner requires Bash, Perl, Python 3.8 or newer, the Claude CLI, and a filesystem that supports symlinks (Linux or macOS). Each run uses `.runs/run.*` and validates artifact names and content hashes after each stage. A completed run atomically replaces the `output` symlink. The published directory contains one digest and `manifest.json`, which records the run ID, filenames, byte counts, and SHA-256 hashes for each stage.

Source files must have distinct stems: `article.md` and `article.txt` in the same input set are rejected before processing. Model output must be a JSON object with a string summary and arrays for facts, entities, and unverified claims.

A failed stage leaves the previous publication unchanged. A competing run fails with `another run` before processing documents. The `.run-lock` directory is removed on ordinary exit. After an uncatchable termination, confirm that the previous runner and its children have stopped before removing the stale lock. Its `run-id` file identifies the workspace it owns.

If an older version created a real `output/` directory, move it to a backup before the first full run. The runner stops rather than overwriting it. Previous and failed runs remain in `.runs/` for diagnosis. Remove only inactive runs you no longer need, and keep the run referenced by `output`. These directories can contain source documents and model results; they stay ignored by Git.

The weekly workflow copies the validated digest and manifest to the repository-root `output/` and commits them together. That directory holds the current result. Older committed digests remain in Git history. Workflow publishers are serialized per branch.

Or run individual stages from a separate scratch directory:

```bash
PIPELINE_DIR="$PWD"
mkdir -p /tmp/my-pipeline-example
cd /tmp/my-pipeline-example
bash "$PIPELINE_DIR/01-fetch.sh"
bash "$PIPELINE_DIR/02-clean.sh"
# inspect ./work/02-clean/ here
bash "$PIPELINE_DIR/03-process.sh"
bash "$PIPELINE_DIR/04-save.sh"
```

Standalone stages are for manual experiments. They do not run validation or atomic publication. `04-save.sh` refuses to write through the full runner's published `output` symlink.

## Tests without a model

From the repository root, run `python3 -m unittest discover -s tests -v`. The suite uses a fake `claude` executable and temporary directories. It checks failures, overlap, removed inputs, manifest hashes, filename collisions, changed prior-stage artifacts, and publication ownership. It never calls a real model.

## Test small

Don't run this on 5,000 files the first time. Run it on 5. The `sample-docs/` folder has 7 — that's the right size to learn the shape. Once you trust the pipeline, point it at your real corpus.

## Secret hygiene

- `claude` reads `ANTHROPIC_API_KEY` from your environment. Don't hardcode it in any script.
- Don't commit your `./work/` or `./output/` folders if they contain anything sensitive — add them to `.gitignore`.
- If you swap in another API in stage 3, put its key in an env var too. Never paste keys into prompts, comments, or filenames.

## Why not one big script

You can write one 200-line script that does all four jobs. People do. Then a stage breaks and you re-run the whole thing. Then you want to swap the cleaner and you can't because it's tangled with the fetcher. Then you can't tell which step is slow. Stages cost you 30 seconds of structure and pay you back every time you debug.
