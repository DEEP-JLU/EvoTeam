import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUITE_DIR = ROOT / "benchmarks" / "MIXED-BENCHMARK"
sys.path.insert(0, str(SUITE_DIR))

from mixed_benchmark_manifest import MixedBenchmarkManifest
from mixed_adapter import ADAPTER_REGISTRY
from task_wrapper import MixedTaskWrapper


def test_source_package_has_required_runtime_assets():
    required_pools = {
        "pool_EvoTeam",
        "pool_GAIA_pool",
        "pool_LoCoBench",
        "pool_LOCAbench",
        "pool_BeyondSWE",
    }
    agents_dir = ROOT / "agents"
    agent_dirs = {path.name for path in agents_dir.iterdir() if path.is_dir()}
    # Frozen/evolved teams are created next to the initial pools during normal
    # use, so the test checks required entries without constraining the set.
    assert required_pools <= agent_dirs
    for pool_name in required_pools:
        assert (agents_dir / pool_name / "pool.yaml").is_file()

    benchmark_dirs = {
        path.name for path in (ROOT / "benchmarks").iterdir()
        if path.is_dir() and path.name != "__pycache__"
    }
    # External benchmark checkouts may be materialized under benchmarks/; only
    # the repository-owned scheduler and adapter packages are mandatory.
    assert {"MIXED-BENCHMARK", "mixed_native"} <= benchmark_dirs


def test_fixed_manifest_and_private_backends():
    manifest = MixedBenchmarkManifest.load(
        SUITE_DIR / "manifests" / "mixed_benchmark_official_116_seed20260828.json"
    )
    assert len(manifest.tasks_for_phase("evolve")) == 116
    assert manifest.tasks_for_phase("test") == []
    assert set(ADAPTER_REGISTRY) == {
        "gaia", "locobench", "locabench", "beyondswe"
    }
    for name, binding in manifest.benchmark_bindings.items():
        assert binding["adapter_module"] == f"benchmarks.mixed_native.{name}_backend"
        assert ADAPTER_REGISTRY[name].module == binding["adapter_module"]
    MixedTaskWrapper(manifest)

