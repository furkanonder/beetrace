import shlex
import subprocess
import sys
import unittest

ZERO_RETURN_CMD = (sys.executable, "-c", "pass")


class TestBeeTrace(unittest.TestCase):
    def setUp(self):
        self.dummy_proc = subprocess.Popen(
            ZERO_RETURN_CMD,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def tearDown(self):
        self.dummy_proc.stdout.close()
        self.dummy_proc.stderr.close()
        self.dummy_proc.wait()

    def test_run_command(self):
        args = shlex.split(
            f"bpftrace -f json -l usdt:*  -p {self.dummy_proc.pid}"
        )
        try:
            p = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
            self.assertEqual(
                "ERROR: bpftrace currently only supports running as the root user.\n",
                p.stderr.read(),
            )
        finally:
            p.stdout.close()
            p.stderr.close()
            p.wait()
