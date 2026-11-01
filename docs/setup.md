# Setup Guide

This guide covers external services and benchmark environments used by
EvoTeam. Framework coordination and post-task evolution are runtime features;
they do not require a separate user-installed package or compatibility
protocol.

## Model endpoint

Configure the model endpoint in `.env` (or in the file selected by
`EVOTEAM_ENV_FILE`):

```dotenv
LLM_PROVIDER=dev
DEV_API_BASE=https://your-openai-compatible-endpoint/v1
DEV_API_KEY=your-api-key
EVOTEAM_MODEL=gpt-5.6-luna
```

Install the Python dependencies from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e .
```

## Web search and webpage access

GAIA tasks that require web evidence use the configured web-search provider and
webpage retrieval. The provider is selected in this order:

1. Serper when `SERPER_KEY_ID` is configured;
2. SerpAPI when `SERPAPI_API_KEY` is configured;
3. DuckDuckGo when neither key is configured.

To use Serper, add this to `.env`:

```dotenv
SERPER_KEY_ID=your-serper-api-key
```

Alternatively, configure SerpAPI:

```dotenv
SERPAPI_API_KEY=your-serpapi-api-key
```

DuckDuckGo requires no API key. Web search and webpage retrieval require
network access.

## Docker and BeyondSWE

BeyondSWE tasks execute in the benchmark-provided Docker environments. Install
Docker, make sure the daemon is running, and verify it from the shell:

```bash
docker info
```

The required BeyondSWE images and task data must be available under the
external benchmark directory before running the corresponding track.

## LOCA-Bench MCP environment

LOCA-Bench initializes the MCP servers declared by each task. Install the
dependencies required by the task-configured MCP servers and make those
servers available in the LOCA-Bench environment. EvoTeam initializes and
cleans up the task MCP session automatically.

## External data layout

Keep large datasets and benchmark checkouts outside the repository when
desired. Set the external root and, for BeyondSWE, the JSONL file explicitly:

```bash
export MIXED_DATA_ROOT="/absolute/path/to/external-assets"
export BEYONDSWE_DATA_FILE="/absolute/path/to/beyondswe.jsonl"
```

The external root must preserve the following repository-relative layout:

```text
<MIXED_DATA_ROOT>/
├── data/
│   └── gaia/
└── benchmarks/
    ├── LoCoBench/
    ├── LOCA-bench/
    └── BeyondSWE/
```

GAIA requires its split files and attachments under `data/gaia/`. LoCoBench
and LOCA-Bench use their benchmark installations under `benchmarks/`; BeyondSWE
uses the configured JSONL file or one of the supported files under
`benchmarks/BeyondSWE/`.

## Quick checks

Run these checks before a benchmark experiment:

```bash
python3 -m benchmarks.mixed_native.gaia_backend --help
python3 -m benchmarks.mixed_native.locobench_backend --help
python3 -m benchmarks.mixed_native.locabench_backend --help
python3 -m benchmarks.mixed_native.beyondswe_backend --help
docker info  # required for BeyondSWE
```

The adapters report any missing benchmark data or environment service when a
run starts.
