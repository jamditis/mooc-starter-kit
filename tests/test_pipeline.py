"""Exercise isolated shell runs with a fake model; never call a real model."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import textwrap
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts' / 'pipeline'


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.pipeline = self.root / 'scripts' / 'pipeline'
        self.pipeline.parent.mkdir()
        shutil.copytree(SCRIPTS, self.pipeline, ignore=shutil.ignore_patterns('.runs', 'work', 'output', '.run-lock'))
        self.source = self.root / 'sample-docs'
        self.source.mkdir()
        (self.source / 'one.md').write_text('First document')
        bindir = self.root / 'bin'
        bindir.mkdir()
        fake = bindir / 'claude'
        fake.write_text('''#!/usr/bin/env python3
import json, os, pathlib, sys, time
text = sys.stdin.read()
if os.getenv('BLOCK_MODEL'):
    pathlib.Path(os.environ['BLOCK_MODEL']).write_text('started')
    while not pathlib.Path(os.environ['RELEASE_MODEL']).exists():
        time.sleep(.02)
if os.getenv('FAIL_MODEL'):
    sys.exit(9)
if os.getenv('INVALID_MODEL'):
    print('not JSON')
    sys.exit(0)
print(json.dumps({'summary': text.rsplit('---', 1)[-1].strip(), 'key_facts': [], 'named_entities': [], 'unverified_claims': []}))
''')
        fake.chmod(0o755)
        self.env = dict(os.environ, PATH=str(bindir) + os.pathsep + os.environ['PATH'])
        self.env.pop('ANTHROPIC_API_KEY', None)
        self.command = ['bash', str(self.pipeline / 'run-all.sh'), str(self.source)]

    def run_pipeline(self, **env):
        return subprocess.run(self.command, env=dict(self.env, **env), text=True, capture_output=True, timeout=15)

    def published(self):
        return {p.name: p.read_bytes() for p in (self.pipeline / 'output').glob('*') if p.is_file()}

    def test_failed_later_stage_preserves_previous_publication(self):
        first = self.run_pipeline()
        self.assertEqual(first.returncode, 0, first.stderr)
        before = self.published()
        (self.source / 'one.md').write_text('Changed document')
        failed = self.run_pipeline(FAIL_MODEL='1')
        self.assertNotEqual(failed.returncode, 0)
        self.assertEqual(self.published(), before)
        self.assertTrue((self.pipeline / 'output' / 'manifest.json').is_file())

    def test_removed_source_does_not_reappear_in_next_digest(self):
        (self.source / 'removed.txt').write_text('OLD DOCUMENT MUST DISAPPEAR')
        first = self.run_pipeline()
        self.assertEqual(first.returncode, 0, first.stderr)
        (self.source / 'removed.txt').unlink()
        second = self.run_pipeline()
        self.assertEqual(second.returncode, 0, second.stderr)
        digest = next((self.pipeline / 'output').glob('digest-*.md')).read_text()
        self.assertNotIn('OLD DOCUMENT MUST DISAPPEAR', digest)

    def test_overlapping_run_fails_without_publishing(self):
        blocked = self.root / 'blocked'
        release = self.root / 'release'
        first = subprocess.Popen(self.command, env=dict(self.env, BLOCK_MODEL=str(blocked), RELEASE_MODEL=str(release)), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            deadline = time.monotonic() + 10
            while not blocked.exists() and time.monotonic() < deadline:
                time.sleep(.02)
            self.assertTrue(blocked.exists(), 'fake model was not reached')
            second = self.run_pipeline()
            self.assertNotEqual(second.returncode, 0, second.stdout)
            self.assertIn('another run', second.stderr)
            self.assertFalse((self.pipeline / 'output').exists())
        finally:
            release.touch()
            stdout, stderr = first.communicate(timeout=10)
        self.assertEqual(first.returncode, 0, stderr)
        self.assertTrue((self.pipeline / 'output' / 'manifest.json').is_file())

    def test_failed_save_cannot_replace_previous_digest(self):
        first = self.run_pipeline()
        self.assertEqual(first.returncode, 0, first.stderr)
        before = self.published()
        with (self.pipeline / '04-save.sh').open('a') as script:
            script.write('\nprintf "partial" > ./output/partial.md\nexit 9\n')
        failed = self.run_pipeline()
        self.assertNotEqual(failed.returncode, 0)
        self.assertEqual(self.published(), before)
        self.assertFalse((self.pipeline / '.run-lock').exists())

    def test_invalid_model_output_keeps_previous_publication(self):
        first = self.run_pipeline()
        self.assertEqual(first.returncode, 0, first.stderr)
        before = self.published()
        failed = self.run_pipeline(INVALID_MODEL='1')
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn('run validation:', failed.stderr)
        self.assertEqual(self.published(), before)

    def test_manifest_hashes_belong_to_published_run(self):
        result = self.run_pipeline()
        self.assertEqual(result.returncode, 0, result.stderr)
        output = (self.pipeline / 'output').resolve()
        manifest = json.loads((output / 'manifest.json').read_text())
        self.assertEqual(manifest['run_id'], output.parent.name)
        for name, entry in manifest['stages']['output'].items():
            data = (output / name).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), entry['sha256'])
            self.assertEqual(len(data), entry['bytes'])

    def test_old_run_cannot_promote_without_owning_lock(self):
        result = self.run_pipeline()
        self.assertEqual(result.returncode, 0, result.stderr)
        published = (self.pipeline / 'output').resolve()
        result = subprocess.run([sys.executable, str(self.pipeline / 'validate-run.py'),
                                 'publish', str(published.parent)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.pipeline / 'output').resolve(), published)

    def test_source_stem_collision_fails_before_model(self):
        (self.source / 'one.txt').write_text('Conflicting second input')
        result = self.run_pipeline()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('distinct stems', result.stderr)
        self.assertFalse((self.pipeline / 'output').exists())

    def test_prior_stage_tampering_fails_before_publication(self):
        with (self.pipeline / '02-clean.sh').open('a') as script:
            script.write('\nprintf "changed raw input" >> ./work/01-raw/one.md\n')
        result = self.run_pipeline()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('raw artifacts changed', result.stderr)
        self.assertFalse((self.pipeline / 'output').exists())

    def test_legacy_output_is_preserved(self):
        output = self.pipeline / 'output'
        output.mkdir()
        (output / 'keep.md').write_text('Previous result')
        result = self.run_pipeline()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('legacy directory', result.stderr)
        self.assertEqual((output / 'keep.md').read_text(), 'Previous result')

    def test_standalone_save_cannot_modify_published_snapshot(self):
        first = self.run_pipeline()
        self.assertEqual(first.returncode, 0, first.stderr)
        before = self.published()
        work = self.pipeline / 'work' / '03-processed'
        work.mkdir(parents=True)
        (work / 'new.json').write_text('{}')
        result = subprocess.run(['bash', str(self.pipeline / '04-save.sh')],
                                cwd=self.pipeline, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('published snapshot', result.stderr)
        self.assertEqual(self.published(), before)

    def test_workflow_copies_only_the_complete_current_snapshot(self):
        workflow = (SCRIPTS.parents[1] / '.github/workflows/weekly-digest.yml').read_text()
        step = workflow.split('      - name: run pipeline\n', 1)[1].split('      # 5b.', 1)[0]
        command = textwrap.dedent(step.split('        run: |\n', 1)[1])
        old = self.root / 'output'
        old.mkdir()
        (old / 'digest-old.md').write_text('Previous publication')
        result = subprocess.run(['bash', '-e', '-c', command], cwd=self.root, env=self.env,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        before = {p.name: p.read_bytes() for p in old.iterdir()}
        self.assertNotIn('digest-old.md', before)
        self.assertIn('manifest.json', before)
        self.assertEqual(len(before), 2)
        failed = subprocess.run(['bash', '-e', '-c', command], cwd=self.root,
                                env=dict(self.env, FAIL_MODEL='1'), capture_output=True, text=True)
        self.assertNotEqual(failed.returncode, 0)
        self.assertEqual({p.name: p.read_bytes() for p in old.iterdir()}, before)


if __name__ == '__main__':
    unittest.main()
