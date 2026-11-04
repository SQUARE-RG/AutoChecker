import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class BatchRunnerTests(unittest.TestCase):
    def test_failure_and_exclusion_do_not_stop_later_cves(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cve_file = root / 'cve.txt'
            cve_file.write_text(
                '# selected cases\n'
                'CVE-2022-25842\n'
                'CVE-2022-32287  # excluded\n'
                'CVE-2021-30181\n'
                'CVE-2022-25842\n')
            batch = root / 'batch'
            script = Path(__file__).resolve().parents[3] / 'autoql_scripts' / 'run_autoql_batch.py'
            result = subprocess.run([
                sys.executable, str(script), str(cve_file),
                '--exclude', 'CVE-2022-32287',
                '--python', '/bin/false',
                '--output', str(batch),
            ], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            summary = json.loads((batch / 'summary.json').read_text())
            self.assertEqual(summary['requested_count'], 3)
            self.assertEqual(summary['excluded'], ['CVE-2022-32287'])
            self.assertEqual([item['cve'] for item in summary['results']], [
                'CVE-2022-25842', 'CVE-2021-30181'])
            self.assertEqual([item['status'] for item in summary['results']], [
                'failed', 'failed'])


if __name__ == '__main__':
    unittest.main()
