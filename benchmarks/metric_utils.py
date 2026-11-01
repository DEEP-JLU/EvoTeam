"""Metric grouping helpers shared by mixed-benchmark summaries."""

from __future__ import annotations

from typing import Any


_DISPLAY_NAMES = {
    "gaia": "GAIA",
    "locobench_fi": "LoCoBench FI",
    "locobench_cr": "LoCoBench CR",
    "locabench": "LOCA-Bench",
    "beyondswe_crossrepo": "BeyondSWE CrossRepo",
    "beyondswe_depmigrate": "BeyondSWE DepMigrate",
}


def _normalise(value: Any) -> str:
    return str(value or "").strip().lower().replace("-", "_")


def track_for_source(
    benchmark: Any,
    split: Any = "",
    *,
    adapter_args: dict[str, Any] | None = None,
    track: Any = "",
) -> str:
    """Return the publication track used to group a source task."""
    benchmark_key = _normalise(benchmark)
    split_key = _normalise(split)
    args = adapter_args or {}
    track_key = _normalise(track or args.get("category"))

    if benchmark_key == "locobench":
        if track_key in {"feature_implementation", "fi", "feature"}:
            return "fi"
        if track_key in {"cross_file_refactoring", "cr", "cross_file"}:
            return "cr"
        return track_key or split_key
    if benchmark_key == "beyondswe":
        if split_key in {"crossrepo", "cross_repo"}:
            return "crossrepo"
        if split_key in {"depmigrate", "dep_migrate"}:
            return "depmigrate"
        return split_key
    return ""


def metric_key(
    benchmark: Any,
    split: Any = "",
    *,
    adapter_args: dict[str, Any] | None = None,
    track: Any = "",
) -> str:
    """Return one stable summary key for a benchmark/track pair."""
    benchmark_key = _normalise(benchmark)
    source_track = track_for_source(
        benchmark_key, split, adapter_args=adapter_args, track=track,
    )
    if benchmark_key in {"locobench", "beyondswe"} and source_track:
        return f"{benchmark_key}_{source_track}"
    return benchmark_key


def metric_key_from_row(row: dict[str, Any]) -> str:
    explicit_metric = _normalise(row.get("metric_key"))
    if explicit_metric in _DISPLAY_NAMES:
        return explicit_metric
    raw_track = _normalise(row.get("source_track"))
    if raw_track in _DISPLAY_NAMES:
        return raw_track
    source = row.get("source") or {}
    nested = row.get("native_record") or {}
    adapter_args = (
        row.get("source_adapter_args")
        or source.get("adapter_args")
        or {}
    )
    if not adapter_args and nested.get("task_category"):
        adapter_args = {"category": nested["task_category"]}
    return metric_key(
        row.get("source_benchmark") or source.get("benchmark"),
        row.get("source_split") or source.get("split"),
        adapter_args=adapter_args,
        track=raw_track,
    )


def display_name(metric: Any) -> str:
    key = str(metric)
    return _DISPLAY_NAMES.get(key, key)


def is_lcbs_metric(metric: Any) -> bool:
    return str(metric) in {"locobench_fi", "locobench_cr"}


def lcbs_score(row: dict[str, Any]) -> float | None:
    """Read the continuous LoCoBench score on its native 0--5 scale."""
    nested = row.get("native_record") or {}
    for value in (row.get("lcbs"), nested.get("lcbs")):
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
    native_score = row.get("native_score", row.get("score"))
    if isinstance(native_score, (int, float)) and not isinstance(native_score, bool):
        return float(native_score) * 5.0
    return None


def primary_metric(metric: Any) -> str:
    return "lcbs" if is_lcbs_metric(metric) else "native_score"


def primary_score(metric: Any, row: dict[str, Any]) -> float:
    if is_lcbs_metric(metric):
        return float(lcbs_score(row) or 0.0)
    return float(row.get("native_score", row.get("score", 0.0)) or 0.0)
