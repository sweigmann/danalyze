#!/usr/bin/env python3
# flake8: noqa: E501
import pytest      # noqa: F401
import subprocess
import os


class Test_danalyze(object):
    # end-to-end tests
    def test_process(self):
        p = subprocess.run(
            ["python3", os.path.join("src", "danalyze", "danalyze.py"), "--help"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        assert p.returncode == 0
        assert "usage: danalyze [-h] " in p.stdout

    def test_danalyze_file_ssdeep(self):
        p = subprocess.run(
            ["python3", os.path.join("src", "danalyze", "danalyze.py"), os.path.join("test", "1"), os.path.join("test", "2")],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        assert p.returncode == 0
        assert "filepath" in p.stdout
        assert "file1_ssdeep" in p.stdout
        assert "file2_ssdeep" in p.stdout
        assert "ssdeep_score" in p.stdout
        assert '"file.txt"' in p.stdout
        assert (
            "3:AXGBicFlgVNhBGcL6wCrFQE3:AXGHsNhxLsr2s,3:AXGBicFlIHBGcL6wCrFQE3:AXGH6xLsr2s,22"
            in p.stdout
        )

    def test_danalyze_file_ssdeeper(self):
        p = subprocess.run(
            [
                "python3",
                os.path.join("src", "danalyze", "danalyze.py"),
                "-s",
                "ssdeeper",
                os.path.join("test", "1"),
                os.path.join("test", "2"),
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        assert p.returncode == 0
        assert "filepath" in p.stdout
        assert "file1_ssdeeper" in p.stdout
        assert "file2_ssdeeper" in p.stdout
        assert "ssdeeper_score" in p.stdout
        assert '"file.txt"' in p.stdout
        assert (
            "3:AN8gu5QklJgVNhyEgcGwFEBQJab:VgDhxFkb,3:AN8gu5QklJuXgcGwFEBQJab:VglxFkb,28"
            in p.stdout
        )
