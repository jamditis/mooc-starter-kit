#!/usr/bin/env python3
"""Validate stage identities and publish a completed run with one symlink swap."""
import hashlib
import json
import os
from pathlib import Path
import sys

STAGES = {'raw': 'work/01-raw', 'clean': 'work/02-clean',
          'processed': 'work/03-processed', 'output': 'output'}


def snapshot(directory):
    return {p.name: {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                     'bytes': p.stat().st_size}
            for p in sorted(directory.iterdir()) if p.is_file()}


def validate(stage, run):
    manifest_path = run / 'manifest.json'
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {
        'run_id': run.name, 'stages': {}}
    if manifest['run_id'] != run.name:
        raise ValueError('manifest belongs to a different run')
    for previous, expected in manifest['stages'].items():
        if snapshot(run / STAGES[previous]) != expected:
            raise ValueError(f'{previous} artifacts changed after validation')
    index = list(STAGES).index(stage)
    if list(manifest['stages']) != list(STAGES)[:index]:
        raise ValueError('stages must be validated in order, once per run')
    files = snapshot(run / STAGES[stage])
    if not files:
        raise ValueError(f'{stage} produced no artifacts')
    raw = manifest['stages'].get('raw', files)
    source_names = [n for n in raw if n != '_manifest.tsv']
    stems = [Path(n).stem for n in source_names]
    if not source_names or len(set(stems)) != len(stems):
        raise ValueError('source filenames must have distinct stems to avoid overwrites')
    if stage in ('clean', 'processed'):
        suffix = '.txt' if stage == 'clean' else '.json'
        if set(files) != {stem + suffix for stem in stems}:
            raise ValueError(f'{stage} artifact names do not match this run inputs')
        if any(not entry['bytes'] for entry in files.values()):
            raise ValueError(f'{stage} produced an empty artifact')
    if stage == 'processed':
        validate_analyses(run / STAGES[stage], files)
    if stage == 'output' and (len(files) != 1 or not next(iter(files)).startswith('digest-')
                              or not next(iter(files)).endswith('.md')
                              or not next(iter(files.values()))['bytes']):
        raise ValueError('save stage must produce one nonempty digest')
    manifest['stages'][stage] = files
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')


def validate_analyses(directory, files):
    for name in files:
        data = json.loads((directory / name).read_text())
        if not isinstance(data, dict) or not isinstance(data.get('summary'), str):
            raise ValueError(f'{name} is not an analysis object with a summary')
        for key in ('key_facts', 'named_entities', 'unverified_claims'):
            if not isinstance(data.get(key), list):
                raise ValueError(f'{name} has no {key} array')


def publish(run):
    root = run.parent.parent
    if (root / '.run-lock' / 'run-id').read_text().strip() != run.name:
        raise ValueError('another run owns the publication lock')
    manifest = json.loads((run / 'manifest.json').read_text())
    if manifest['run_id'] != run.name or list(manifest['stages']) != list(STAGES):
        raise ValueError('cannot publish an incomplete or foreign run')
    for stage, expected in manifest['stages'].items():
        if snapshot(run / STAGES[stage]) != expected:
            raise ValueError(f'{stage} artifacts changed before publication')
    output = root / 'output'
    if output.exists() and not output.is_symlink():
        raise ValueError('output is a legacy directory; move it to a backup before running again')
    (run / 'output' / 'manifest.json').write_bytes((run / 'manifest.json').read_bytes())
    pending = root / ('.output-' + run.name)
    try:
        pending.symlink_to(os.path.relpath(run / 'output', root), target_is_directory=True)
        os.replace(pending, output)
    finally:
        pending.unlink(missing_ok=True)


if __name__ == '__main__':
    try:
        stage, run_arg = sys.argv[1:]
        run = Path(run_arg).resolve()
        if stage == 'publish':
            publish(run)
        else:
            validate(stage, run)
    except (OSError, ValueError, KeyError) as error:
        print(f'run validation: {error}', file=sys.stderr)
        sys.exit(1)
