import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[1]
SUITE_DIR = ROOT / "benchmarks" / "MIXED-BENCHMARK"
if str(SUITE_DIR) not in sys.path:
    sys.path.insert(0, str(SUITE_DIR))

from mixed_scheduler import MixedScheduler, aggregate_rollout_summaries


def _aggregate_avg3_module():
    path = ROOT / "scripts" / "aggregate_avg3.py"
    spec = importlib.util.spec_from_file_location("aggregate_avg3", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _tracks():
    return [
        ("gaia", "test_100", {}, "gaia-1", 0.5, None),
        ("locobench", "python", {"category": "feature_implementation"}, "fi-1", 0.7, 3.5),
        ("locobench", "python", {"category": "cross_file_refactoring"}, "cr-1", 0.8, 4.0),
        ("locabench", "8k", {}, "loca-1", 1.0, None),
        ("beyondswe", "crossrepo", {}, "crossrepo-1", 1.0, None),
        ("beyondswe", "depmigrate", {}, "depmigrate-1", 0.4, None),
    ]


def _expected_tasks():
    return [
        {
            "phase": "test",
            "enabled": True,
            "mixed_task_id": task_id,
            "source": {
                "benchmark": benchmark,
                "split": split,
                "adapter_args": adapter_args,
            },
        }
        for benchmark, split, adapter_args, task_id, _score, _lcbs in _tracks()
    ]


def _run_rows(run_index):
    rows = []
    for benchmark, split, adapter_args, task_id, score, lcbs in _tracks():
        native_record = {}
        if lcbs is not None:
            native_record = {
                "lcbs": lcbs,
                "task_category": adapter_args["category"],
            }
        rows.append({
            "phase": "test",
            "mixed_task_id": task_id,
            "source_benchmark": benchmark,
            "source_split": split,
            "source_adapter_args": adapter_args,
            "native_score": score,
            "is_correct": score >= 0.6,
            "official_score_eligible": True,
            "native_record": native_record,
            "rollout_run_id": f"r{run_index}",
        })
    return rows


def test_avg3_reports_six_tracks_and_continuous_lcbs():
    module = _aggregate_avg3_module()
    runs = [_run_rows(1), _run_rows(2), _run_rows(3)]
    for rows, lcbs in zip(runs, (2.9, 3.1, 4.5)):
        fi = next(row for row in rows if row["mixed_task_id"] == "fi-1")
        fi["native_record"]["lcbs"] = lcbs
        fi["native_score"] = lcbs / 5.0
        fi["is_correct"] = lcbs >= 3.0
    result = module.aggregate_records(
        ["r1", "r2", "r3"],
        runs,
        _expected_tasks(),
    )

    assert sorted(result["benchmark_summary"]) == [
        "beyondswe_crossrepo",
        "beyondswe_depmigrate",
        "gaia",
        "locabench",
        "locobench_cr",
        "locobench_fi",
    ]
    fi = result["benchmark_summary"]["locobench_fi"]
    assert fi["primary_metric"] == "lcbs"
    assert fi["avg_at_k_primary_score"] == 3.5
    assert fi["avg_at_k_lcbs"] == 3.5
    assert fi["avg_at_k_native_score"] == 0.7
    assert fi["avg_at_k_success_rate"] == 0.6667
    assert result["benchmark_summary"]["locobench_cr"]["avg_at_k_primary_score"] == 4.0
    assert result["complete"]


def test_scheduler_rollout_summary_preserves_track_boundaries():
    expected_ids = {
        "gaia": ["gaia-1"],
        "locobench_fi": ["fi-1"],
        "locobench_cr": ["cr-1"],
        "locabench": ["loca-1"],
        "beyondswe_crossrepo": ["crossrepo-1"],
        "beyondswe_depmigrate": ["depmigrate-1"],
    }
    summaries = []
    for index in range(1, 4):
        rows = []
        for benchmark, split, adapter_args, task_id, score, lcbs in _tracks():
            metric = {
                "gaia": "gaia",
                "locobench": (
                    "locobench_fi"
                    if adapter_args.get("category") == "feature_implementation"
                    else "locobench_cr"
                ),
                "locabench": "locabench",
                "beyondswe": f"beyondswe_{split}",
            }[benchmark]
            rows.append({
                "mixed_task_id": task_id,
                "source_benchmark": benchmark,
                "source_split": split,
                "metric_key": metric,
                "lcbs": lcbs,
                "native_score": score,
                "is_correct": score >= 0.6,
                "official_score_eligible": True,
                "infrastructure_failure": False,
            })
        summaries.append({
            "run_id": f"r{index}",
            "expected_test_tasks_by_benchmark": {
                key: len(value) for key, value in expected_ids.items()
            },
            "expected_test_task_ids_by_benchmark": expected_ids,
            "test_task_results": rows,
        })

    result = aggregate_rollout_summaries(summaries)
    assert sorted(result["benchmark_summary"]) == sorted(expected_ids)
    assert result["benchmark_summary"]["locobench_cr"]["primary_score"] == 4.0
    assert result["benchmark_summary"]["locobench_cr"]["avg_lcbs"] == 4.0
    assert result["benchmark_summary"]["locobench_cr"]["native_avg_score"] == 0.8


@pytest.mark.parametrize("completed", [0, 3, 6])
def test_scheduler_summary_keeps_expected_tracks_when_results_are_missing(tmp_path, completed):
    # Isolated synthetic cases: no benchmark execution or real result files.
    rows = _run_rows(1)[:completed]
    evolution_row = dict(_run_rows(1)[1], phase="evolve", mixed_task_id="evolve-fi")
    cases = []
    for index, row in enumerate([*rows, evolution_row]):
        case = tmp_path / str(index)
        case.mkdir()
        (case / "result.json").write_text(json.dumps(row), encoding="utf-8")
        cases.append(case)
    tasks = [
        SimpleNamespace(
            enabled=True,
            mixed_task_id=task["mixed_task_id"],
            source=SimpleNamespace(**task["source"]),
        )
        for task in _expected_tasks()
    ]
    scheduler = object.__new__(MixedScheduler)
    scheduler.manifest = SimpleNamespace(
        suite_id="synthetic-suite",
        tasks_for_phase=lambda *args, **kwargs: tasks,
    )
    scheduler.run_mgr = SimpleNamespace(
        run_id="synthetic-run",
        list_cases=lambda: cases,
        list_team_versions=lambda: [],
    )
    scheduler.team_name = "synthetic-team"
    scheduler.ledger = SimpleNamespace(path=tmp_path / "manifest.json")

    result = scheduler.summary()
    metrics = result["benchmark_summary"]
    assert set(metrics) == {
        "gaia", "locobench_fi", "locobench_cr", "locabench",
        "beyondswe_crossrepo", "beyondswe_depmigrate",
    }
    assert len(result["test_task_results"]) == completed
    assert sum(metric["assigned"] for metric in metrics.values()) == completed
    for metric in metrics.values():
        assert metric["expected_test_tasks"] == 1
        if not metric["assigned"]:
            assert metric["eligible"] == 0
            assert metric["primary_score"] is None
            assert metric["avg_lcbs"] is None
            assert metric["success_rate"] is None
    if completed:
        fi = metrics["locobench_fi"]
        assert fi["primary_metric"] == "lcbs"
        assert fi["primary_score"] == fi["avg_lcbs"] == 3.5
        assert fi["native_avg_score"] == 0.7
        assert fi["success_rate"] == 1.0

    aggregate = aggregate_rollout_summaries([result] * 3)
    assert set(aggregate["benchmark_summary"]) == set(metrics)
    for key, metric in metrics.items():
        averaged = aggregate["benchmark_summary"][key]
        assert averaged["primary_score"] == metric["primary_score"]
        assert averaged["complete_avg_at_tasks"] == metric["eligible"]


def test_avg3_legacy_rows_and_incomplete_rollouts():
    module = _aggregate_avg3_module()
    runs = [_run_rows(1), _run_rows(2), _run_rows(3)]
    for rows in runs:
        for row in rows:
            # Older mixed result files retain category only in native_record.
            row.pop("source_adapter_args")
    runs[1][1]["infrastructure_failure"] = True
    runs[2][2]["official_score_eligible"] = False
    runs[2] = [row for row in runs[2] if row["mixed_task_id"] != "depmigrate-1"]

    result = module.aggregate_records(["r1", "r2", "r3"], runs, _expected_tasks())
    assert not result["complete"]
    assert len(result["benchmark_summary"]) == 6
    for key in ("locobench_fi", "locobench_cr", "beyondswe_depmigrate"):
        metric = result["benchmark_summary"][key]
        assert metric["complete_avg_at_tasks"] == 0
        assert metric["incomplete_tasks"] == 1
        assert metric["avg_at_k_primary_score"] is None
        assert metric["rollout_coverage"] == 0.6667
    assert result["benchmark_summary"]["locobench_fi"]["infrastructure_failures"] == 1
    assert result["benchmark_summary"]["gaia"]["complete_avg_at_tasks"] == 1
