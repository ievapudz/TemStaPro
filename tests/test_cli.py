"""Pytest golden tests for the TemStaPro CLI."""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "tests" / "outputs"
TEMSTAPRO_BIN = REPO_ROOT / "temstapro"


@dataclass(frozen=True)
class Step:
    """One CLI invocation plus any cleanup that surrounds it."""

    args: tuple[str, ...]
    cleanup_before: tuple[str, ...] = ()
    cleanup_after: tuple[str, ...] = ()


@dataclass(frozen=True)
class Case:
    """Full golden test case, potentially with multiple CLI invocations."""

    case_id: str
    steps: tuple[Step, ...]
    cleanup_before: tuple[str, ...] = ()
    cleanup_after: tuple[str, ...] = ()


def _remove_patterns(patterns: Iterable[str]) -> None:
    """Delete files matching the given glob patterns relative to the repo root."""
    for pattern in patterns:
        for path in REPO_ROOT.glob(pattern):
            if path.is_file():
                path.unlink()


def _normalize_output(output: str) -> str:
    """Normalize unstable output fragments before golden comparison."""
    output = re.sub(r"at (.*) line \d+\.", r"at \1 line 999.", output)
    output = re.sub(r".*: beginning", "2000-01-01: beginning", output)
    output = re.sub(r".*: finished", "2000-01-01: finished", output)
    output = re.sub(r".*: time to", "0:00:00.0001: time to", output)
    return output


def _run_step(step: Step) -> str:
    """Run a single TemStaPro CLI step and return combined stdout/stderr."""
    _remove_patterns(step.cleanup_before)
    try:
        result = subprocess.run(
            [sys.executable, str(TEMSTAPRO_BIN), *step.args],
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        return result.stdout
    finally:
        _remove_patterns(step.cleanup_after)


CASES = (
    Case(
        case_id="001",
        steps=(
            Step(
                args=(
                    "-f", "tests/data/replaced_symbol_sequence.fasta",
                    "-e", "./tests/outputs/",
                    "-d", "./ProtTrans/",
                    "--per-res-output", "./tests/outputs/001_mean.tmp",
                ),
                cleanup_after=("tests/outputs/001_mean.tmp",),
            ),
        ),
    ),
    Case(
        case_id="002",
        steps=(
            Step(
                args=(
                    "-f", "./tests/data/long_sequence_2.fasta",
                    "-e", "tests/outputs/",
                    "-d", "./ProtTrans/",
                    "--mean-out", "tests/outputs/002.tmp",
                ),
                cleanup_after=(
                    "tests/outputs/mean_52ae55d4fc194abf0e65abc9d740ffc7f84972ddacefb62e931131655083857e.pt",
                    "tests/outputs/002.tmp",
                ),
            ),
        ),
    ),
    Case(
        case_id="003",
        steps=(
            Step(args=("-d", "./ProtTrans/")),
        ),
    ),
    Case(
        case_id="004",
        steps=(
            Step(
                args=(
                    "-f", "./tests/data/long_sequence_2.fasta",
                    "-e", "tests/outputs",
                    "-d", "./ProtTrans/",
                    "--mean-out", "tests/outputs/004.tmp",
                ),
                cleanup_after=(
                    "tests/outputs/mean_52ae55d4fc194abf0e65abc9d740ffc7f84972ddacefb62e931131655083857e.pt",
                    "tests/outputs/004.tmp",
                ),
            ),
        ),
        cleanup_before=("ProtTrans/*",),
    ),
    Case(
        case_id="005",
        steps=(
            Step(
                args=(
                    "-f", "./tests/data/multiple_sequences.fasta",
                    "-e", "tests/outputs/",
                    "-d", "./ProtTrans/",
                ),
            ),
        ),
        cleanup_before=(
            "tests/outputs/mean_5d817ae8188e00eca8913c80312e2669d6551777fbed0d1764e1c09386638c0a.pt",
            "tests/outputs/mean_adc7fcd839ba2802998088a0c7b2310d3abdef0229cc020c55fcb82a492c2d8d.pt",
            "tests/outputs/mean_c425721d82cb786570760210076eaa21403b210aa6566882a41c4ac70df2defd.pt",
        ),
    ),
    Case(
        case_id="006",
        steps=(
            Step(
                args=(
                    "-f", "tests/data/long_sequence.fasta",
                    "-e", "./tests/outputs/",
                    "-d", "./ProtTrans/",
                    "--mean-output", "./tests/outputs/006_mean.tmp",
                    "--per-segment-output", "./tests/outputs/006_per_res_smooth.tmp",
                    "-c",
                    "--segment-size", "41",
                    "--window-size-predictions", "81",
                    "-p", "./tests/outputs/",
                ),
                cleanup_after=(
                    "tests/outputs/006_mean.tmp",
                    "tests/outputs/006_per_res_smooth.tmp",
                ),
            ),
        ),
        cleanup_before=(
            "tests/outputs/mean_b6f8b4d2f6602ee040278b1d64ab7cf588baa33d74a126030e252fd91ac00601.pt",
            "tests/outputs/per_res_b6f8b4d2f6602ee040278b1d64ab7cf588baa33d74a126030e252fd91ac00601.pt",
        ),
    ),
    Case(
        case_id="007",
        steps=(
            Step(
                args=(
                    "-f", "./tests/data/multiple_sequences.fasta",
                    "-e", "tests/outputs/",
                    "-d", "./ProtTrans/",
                ),
            ),
            Step(
                args=(
                    "-f", "./tests/data/multiple_sequences.fasta",
                    "-e", "tests/outputs/",
                    "-d", "./ProtTrans/",
                ),
            ),
        ),
        cleanup_before=(
            "tests/outputs/mean_5d817ae8188e00eca8913c80312e2669d6551777fbed0d1764e1c09386638c0a.pt",
            "tests/outputs/mean_adc7fcd839ba2802998088a0c7b2310d3abdef0229cc020c55fcb82a492c2d8d.pt",
            "tests/outputs/mean_c425721d82cb786570760210076eaa21403b210aa6566882a41c4ac70df2defd.pt",
        ),
    ),
    Case(
        case_id="008",
        steps=(
            Step(
                args=(
                    "-f", "./tests/data/multiple_sequences.fasta",
                    "-d", "./ProtTrans/",
                ),
            ),
        ),
    ),
    Case(
        case_id="009",
        steps=(
            Step(
                args=(
                    "-f", "./tests/data/long_sequence.fasta",
                    "-d", "./ProtTrans/",
                ),
            ),
        ),
    ),
    Case(
        case_id="010",
        steps=(
            Step(
                args=(
                    "-f", "tests/data/multiple_short_sequences.fasta",
                    "-e", "./tests/outputs/",
                    "-d", "./ProtTrans/",
                    "-p", "./tests/outputs/",
                    "--mean-output", "./tests/outputs/010_mean.tmp",
                    "--per-res-output", "./tests/outputs/010_per_res.tmp",
                ),
                cleanup_after=(
                    "tests/outputs/short_seq_?_per_residue_plot_?.svg",
                    "tests/outputs/010_mean.tmp",
                    "tests/outputs/010_per_res.tmp",
                ),
            ),
        ),
        cleanup_before=(
            "tests/outputs/mean_519c2e9a42194ade71c697d64ed3bced3175a6324803a940ebdf69bb65f301ec.pt",
            "tests/outputs/per_res_519c2e9a42194ade71c697d64ed3bced3175a6324803a940ebdf69bb65f301ec.pt",
            "tests/outputs/mean_7bdb2d9587a23bb7f744bcffba509cc7adf8c69667a9d954c3be1a4aa09f7c0a.pt",
            "tests/outputs/per_res_7bdb2d9587a23bb7f744bcffba509cc7adf8c69667a9d954c3be1a4aa09f7c0a.pt",
            "tests/outputs/mean_d2a3c93ce60d9c7ed923bda5def8fa46267df336f7310cc3e951a20f092df979.pt",
            "tests/outputs/per_res_d2a3c93ce60d9c7ed923bda5def8fa46267df336f7310cc3e951a20f092df979.pt",
            "tests/outputs/short_seq_?_per_residue_plot_?.svg",
        ),
    ),
    Case(
        case_id="011",
        steps=(
            Step(
                args=(
                    "-f", "tests/data/long_sequence.fasta",
                    "-e", "./tests/outputs/",
                    "-d", "./ProtTrans/",
                    "--mean-output", "tests/outputs/011_mean.tmp",
                    "--per-res-output", "tests/outputs/011_per_res.tmp",
                ),
                cleanup_after=(
                    "tests/outputs/011_mean.tmp",
                    "tests/outputs/011_per_res.tmp",
                ),
            ),
        ),
        cleanup_before=(
            "tests/outputs/mean_b6f8b4d2f6602ee040278b1d64ab7cf588baa33d74a126030e252fd91ac00601.pt",
            "tests/outputs/per_res_b6f8b4d2f6602ee040278b1d64ab7cf588baa33d74a126030e252fd91ac00601.pt",
        ),
    ),
    Case(
        case_id="012",
        steps=(
            Step(
                args=(
                    "-f", "tests/data/multiple_sequences.fasta",
                    "-e", "./tests/outputs/",
                    "-d", "./ProtTrans/",
                    "--mean-output", "tests/outputs/012_mean.tmp",
                    "--per-res-output", "tests/outputs/012_per_res.tmp",
                ),
                cleanup_after=(
                    "tests/outputs/012_mean.tmp",
                    "tests/outputs/012_per_res.tmp",
                ),
            ),
        ),
        cleanup_before=(
            "tests/outputs/5d817ae8188e00eca8913c80312e2669d6551777fbed0d1764e1c09386638c0a.pt",
            "tests/outputs/adc7fcd839ba2802998088a0c7b2310d3abdef0229cc020c55fcb82a492c2d8d.pt",
            "tests/outputs/c425721d82cb786570760210076eaa21403b210aa6566882a41c4ac70df2defd.pt",
        ),
    ),
    Case(
        case_id="013",
        steps=(
            Step(
                args=(
                    "-f", "./tests/data/multiple_sequences.fasta",
                    "-e", "tests/outputs/",
                    "-d", "./ProtTrans/",
                ),
            ),
            Step(
                args=(
                    "-f", "./tests/data/multiple_sequences.fasta",
                    "-e", "tests/outputs/",
                    "-d", "./ProtTrans/",
                ),
                cleanup_before=(
                    "tests/outputs/mean_5d817ae8188e00eca8913c80312e2669d6551777fbed0d1764e1c09386638c0a.pt",
                    "tests/outputs/mean_adc7fcd839ba2802998088a0c7b2310d3abdef0229cc020c55fcb82a492c2d8d.pt",
                ),
            ),
        ),
        cleanup_before=(
            "tests/outputs/mean_5d817ae8188e00eca8913c80312e2669d6551777fbed0d1764e1c09386638c0a.pt",
            "tests/outputs/mean_adc7fcd839ba2802998088a0c7b2310d3abdef0229cc020c55fcb82a492c2d8d.pt",
            "tests/outputs/mean_c425721d82cb786570760210076eaa21403b210aa6566882a41c4ac70df2defd.pt",
        ),
    ),
    Case(
        case_id="014",
        steps=(
            Step(
                args=(
                    "-f", "./tests/data/long_sequence_2.fasta",
                    "-e", "tests/outputs/",
                    "-d", "./ProtTrans/",
                    "--more-thresholds",
                ),
                cleanup_after=(
                    "tests/outputs/mean_52ae55d4fc194abf0e65abc9d740ffc7f84972ddacefb62e931131655083857e.pt",
                ),
            ),
        ),
    ),
)


@pytest.mark.parametrize("case", CASES, ids=[case.case_id for case in CASES])
def test_temstapro_cli_golden(case: Case) -> None:
    """Run the CLI scenario and compare normalized output to the golden file."""
    _remove_patterns(case.cleanup_before)
    try:
        actual = "".join(_run_step(step) for step in case.steps)
        actual = _normalize_output(actual)
        expected = (OUTPUT_DIR / f"temstapro_{case.case_id}.out").read_text(encoding="utf-8")
        assert actual == expected
    finally:
        _remove_patterns(case.cleanup_after)
