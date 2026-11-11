"""Synthetic offline gateway regressions. No external GitHub/M365 tool calls."""
from __future__ import annotations
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engineering_frontier import FrontierError, build_packet
from frontier_gateway import Gateway, _env


def git(root: Path, *args: str) -> str:
    return subprocess.run(['git','-C',str(root),*args], check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True).stdout.strip()


class GatewayTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        git(self.root, 'init', '-q')
        git(self.root, 'config', 'user.name', 'Synthetic')
        git(self.root, 'config', 'user.email', 'synthetic@example.invalid')
        def add(path: str, content: str):
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
        add('AGENTS.md', 'Root context: nothing private here')
        add('conductor/index.md', '# Context')
        add('docs/targeted-testing.md', '# Tests')
        add('portfolio/repos.json', json.dumps({'components': [
            {'name':'mod-a','path':'modules/mod-a','materialization':'integrated-source'}]}))
        add('modules/mod-a/AGENTS.md','Module context')
        add('modules/mod-a/src/file.py','SECRET-SYNTHETIC-UNTRUSTED')
        add('portfolio-scripts/engine.py','print("synthetic")')
        add('portfolio-scripts/engineering_frontier.py','pass')
        add('portfolio-scripts/frontier_gateway.py','pass')
        add('portfolio-scripts/checks/test_engineering_frontier.py', 'def test_a(): pass')
        add('portfolio-scripts/checks/test_frontier_gateway.py', 'def test_a(): pass')
        add('portfolio-scripts/run_tests.py', 'print("only synthetic")')
        # Exact reviewed source inventory is required by the gateway.
        inventory = sorted(str(path.relative_to(self.root).as_posix())
                           for path in self.root.rglob('*') if path.is_file() and '.git' not in path.relative_to(self.root).parts)
        add('PUBLIC_SOURCE_FILES.json', json.dumps({'schemaVersion': 1,
                                                    'files': sorted([*inventory, 'PUBLIC_SOURCE_FILES.json']),
                                                    'gitlinks': {}}))
        git(self.root, 'add', '.')
        git(self.root, 'commit', '-qm', 'synthetic fixture')
        self.sha = git(self.root, 'rev-parse', 'HEAD')
        self.packet = build_packet(self.root,'EF-02.03',self.sha,['modules/mod-a/src/file.py'])
        self.gateway = Gateway(self.root,self.packet)

    def tearDown(self):
        self.temp.cleanup()

    def test_read_committed_owned_file_and_content_free_receipt(self):
        raw, receipt = self.gateway.read('modules/mod-a/src/file.py')
        self.assertEqual(raw, b'SECRET-SYNTHETIC-UNTRUSTED')
        self.assertEqual(receipt['bytes'],len(raw))
        self.assertNotIn('SECRET',json.dumps(receipt))
        self.assertEqual(receipt['source_sha'],self.sha)

    def test_read_bounded_context(self):
        raw, receipt = self.gateway.read('AGENTS.md')
        self.assertEqual(raw,b'Root context: nothing private here')
        self.assertEqual(receipt['qualification'],'committed-source-read')

    def test_reject_out_of_scope_and_traversal(self):
        for name in ('portfolio-scripts/engine.py','../AGENTS.md','/etc/passwd','modules/mod-a/../../AGENTS.md'):
            with self.subTest(name=name),self.assertRaises(FrontierError):
                self.gateway.read(name)

    def test_packet_expanded_permissions_cannot_authorize_anything(self):
        packet=json.loads(json.dumps(self.packet))
        packet['tools']['allowed'].append('tenant:write')
        with self.assertRaisesRegex(FrontierError,'packet-tampered'):
            Gateway(self.root,packet)

    def test_packet_changes_context_or_sha_refused(self):
        for change in ('context','source','task'):
            with self.subTest(change=change):
                packet=json.loads(json.dumps(self.packet))
                if change=='context':packet['context'][0]['sha256']='0'*64
                if change=='source':packet['source']['commit']='e'*40
                if change=='task':packet['task']['owner']='careops'
                with self.assertRaises(FrontierError):Gateway(self.root,packet)

    def test_mutable_working_tree_is_not_used_as_context(self):
        (self.root/'AGENTS.md').write_text('new private content')
        raw,_=self.gateway.read('AGENTS.md')
        self.assertNotIn(b'new private',raw)

    def test_read_refuses_symlink_even_if_target_was_committed(self):
        path=self.root/'modules/mod-a/src/file.py'
        path.unlink()
        path.symlink_to(self.root/'AGENTS.md')
        with self.assertRaisesRegex(FrontierError,'read-unsafe-file'):
            self.gateway.read('modules/mod-a/src/file.py')

    def test_read_refuses_huge_committed_blob(self):
        path=self.root/'modules/mod-a/src/file.py'
        path.write_bytes(b'x'*131073)
        git(self.root,'add','.')
        git(self.root,'commit','-qm','large synthetic blob')
        sha=git(self.root,'rev-parse','HEAD')
        packet=build_packet(self.root,'EF-02.03',sha,['modules/mod-a/src/file.py'])
        with self.assertRaisesRegex(FrontierError,'read-size-limit'):
            Gateway(self.root,packet).read('modules/mod-a/src/file.py')

    def test_focused_test_requires_explicit_trusted_checkout(self):
        packet=build_packet(self.root,'EF-03.01',self.sha,['portfolio-scripts/frontier_gateway.py'])
        gateway=Gateway(self.root,packet)
        with self.assertRaisesRegex(FrontierError,'trusted-checkout'):
            gateway.test('test_frontier_gateway.py',Path(sys.executable))
        with self.assertRaisesRegex(FrontierError,'test-selector-denied'):
            gateway.test('test_unlisted.py',Path(sys.executable),trusted_checkout=True)
        with self.assertRaisesRegex(FrontierError,'test-selector-denied'):
            gateway.test('../../m.py',Path(sys.executable),trusted_checkout=True)

    def test_focused_test_refuses_dirty_checkout(self):
        packet=build_packet(self.root,'EF-03.01',self.sha,['portfolio-scripts/frontier_gateway.py'])
        gateway=Gateway(self.root,packet)
        (self.root/'portfolio-scripts/engine.py').write_text('modified')
        exe=self.root/'.venv/bin/python'
        exe.parent.mkdir(parents=True)
        exe.write_bytes(b'fake')
        with self.assertRaisesRegex(FrontierError,'test-dirty-checkout'):
            gateway.test('test_frontier_gateway.py',exe,trusted_checkout=True)

    def test_focused_test_refuses_untracked_import_shadowing(self):
        packet = build_packet(self.root, 'EF-03.01', self.sha,
                              ['portfolio-scripts/frontier_gateway.py'])
        gateway = Gateway(self.root, packet)
        (self.root / 'portfolio-scripts' / 'injected_helper.py').write_text(
            'raise RuntimeError("untrusted import")')
        exe = self.root / '.venv/bin/python'
        exe.parent.mkdir(parents=True)
        exe.write_bytes(b'fake')
        with self.assertRaisesRegex(FrontierError, 'test-dirty-checkout'):
            gateway.test('test_frontier_gateway.py', exe, trusted_checkout=True)

    def test_runtime_must_be_local_and_exact_pinned(self):
        packet=build_packet(self.root,'EF-03.01',self.sha,['portfolio-scripts/frontier_gateway.py'])
        gateway=Gateway(self.root,packet)
        with self.assertRaisesRegex(FrontierError,'test-runtime-outside-checkout'):
            gateway.test('test_frontier_gateway.py',Path(sys.executable),trusted_checkout=True)
        exe=self.root/'.venv/bin/python'
        exe.parent.mkdir(parents=True)
        exe.symlink_to(Path(sys.executable))
        with patch('frontier_gateway.run_isolated',
                   return_value=subprocess.CompletedProcess([], 1)):
            with self.assertRaisesRegex(FrontierError,'test-runtime-unqualified'):
                gateway.test('test_frontier_gateway.py',exe,trusted_checkout=True)

    def test_runtime_rejects_disguised_or_escaping_executable(self):
        packet=build_packet(self.root,'EF-03.01',self.sha,['portfolio-scripts/frontier_gateway.py'])
        gateway=Gateway(self.root,packet)
        exe=self.root/'.venv/bin/runner-malicious'
        exe.parent.mkdir(parents=True)
        exe.write_text('not Python')
        with self.assertRaisesRegex(FrontierError,'test-runtime-invalid'):
            gateway.test('test_frontier_gateway.py',exe,trusted_checkout=True)
        exe.unlink()
        with self.assertRaisesRegex(FrontierError,'test-runtime-invalid|test-runtime-outside'):
            gateway.test('test_frontier_gateway.py',self.root/'../bin/sh',trusted_checkout=True)

    def test_runtime_args_are_allowlisted_and_output_not_logged(self):
        packet=build_packet(self.root,'EF-03.01',self.sha,['portfolio-scripts/frontier_gateway.py'])
        gateway=Gateway(self.root,packet)
        exe=self.root/'.venv/bin/python'
        exe.parent.mkdir(parents=True)
        exe.write_bytes(b'fake')
        seen=[]
        def fake_run(root, argv, **kwargs):
            seen.append((argv,kwargs))
            if argv[2] == 'portfolio-scripts/run_tests.py':
                kwargs['stdout'].write(b'SYNTHETIC PRIVATE OUTPUT')
                kwargs['stderr'].write(b'synthetic failure?')
            return subprocess.CompletedProcess(argv,0)
        with patch('frontier_gateway.run_isolated', side_effect=fake_run):
            receipt=gateway.test('test_frontier_gateway.py',exe,trusted_checkout=True)
        self.assertEqual(receipt.status,'passed')
        self.assertNotIn('SYNTHETIC PRIVATE',str(receipt))
        self.assertEqual(receipt.stdout_bytes,len(b'SYNTHETIC PRIVATE OUTPUT'))
        self.assertEqual(seen[1][0][2:7],[
            'portfolio-scripts/run_tests.py','--runner','unittest','--mode','focused'])
        self.assertNotIn('env', seen[1][1])
        self.assertFalse(seen[1][1].get('shell', False))

    def test_missing_os_sandbox_does_not_fall_back_to_python(self):
        packet = build_packet(self.root, 'EF-03.01', self.sha,
                              ['portfolio-scripts/frontier_gateway.py'])
        gateway = Gateway(self.root, packet)
        exe = self.root / '.venv/bin/python'
        exe.parent.mkdir(parents=True)
        exe.write_bytes(b'fake')
        with patch('frontier_gateway.run_isolated',
                   side_effect=FrontierError('sandbox-bubblewrap-unavailable')) as isolated:
            with patch('frontier_gateway.subprocess.run') as direct:
                with self.assertRaisesRegex(FrontierError, 'sandbox-bubblewrap-unavailable'):
                    gateway.test('test_frontier_gateway.py', exe, trusted_checkout=True)
                isolated.assert_called_once()
                direct.assert_not_called()

    def test_unreviewed_tracked_source_cannot_be_read(self):
        (self.root/'portfolio-scripts/unreviewed.py').write_text('fictional private fixture')
        git(self.root,'add','.')
        git(self.root,'commit','-qm','unreviewed tracked fixture')
        sha=git(self.root,'rev-parse','HEAD')
        packet=build_packet(self.root,'EF-02.03',sha,['portfolio-scripts/unreviewed.py'])
        with self.assertRaisesRegex(FrontierError,'source-not-admitted'):
            Gateway(self.root,packet)

    def test_gateway_does_not_require_external_model_or_cloud(self):
        self.assertEqual(self.packet['tools']['allowed'],['repo:read','runner:focused-test'])
        self.assertFalse(self.packet['qualification']['native'])
        self.assertNotIn('OPENAI_API_KEY',_env())

if __name__=='__main__':unittest.main()
