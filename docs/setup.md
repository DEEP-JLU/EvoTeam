# Setup Guide

This guide covers the external tool package required by the EvoTeam runtime, its module responsibilities and compatibility notes, and setup checks for benchmark-specific dependencies.

## Tool Package

EvoTeam requires a compatible Python package named `tools`. This package
provides execution tools, agent communication, orchestration primitives, and
reflection operations. Installing the Python dependencies alone does not
install this package.

### Prepare the tool package

Place the tool implementation directory at the repository root:

```text
EvoTeam/
├── tools/
│   ├── __init__.py
│   ├── bash.py
│   ├── read_file.py
│   ├── write_file.py
│   ├── web_search.py
│   ├── web_fetch.py
│   ├── docker_bash.py
│   ├── docker_str_replace_editor.py
│   ├── loca_mcp.py
│   ├── messaging.py
│   ├── primitives.py
│   └── reflection.py
├── core/
├── benchmarks/
└── runtime_pool.py
```

From the repository root, copy an existing compatible tool package:

```bash
cp -R "/path/to/compatible/tools" ./tools
```

Alternatively, link to an existing directory:

```bash
ln -s "/path/to/compatible/tools" ./tools
```

Use either command when `./tools` does not already exist. The runtime loads
execution tools from this directory. Setting `MIXED_DATA_ROOT` does not
replace this requirement.

### Tool groups

| Group | Modules | Purpose |
|---|---|---|
| Local execution | `bash`, `read_file`, `write_file` | Execute commands and access task workspace files. |
| Web access | `web_search`, `web_fetch` | Search the web and retrieve webpage text. |
| Container execution | `docker_bash`, `docker_str_replace_editor` | Run commands and edit files inside BeyondSWE containers. |
| LOCA environment | `loca_mcp` | Access the MCP tools initialized for each LOCA-Bench task. |
| Agent communication | `messaging` | Exchange messages, wait for replies, and inspect agent status. |
| Orchestration | `primitives` | Provide agent lifecycle and task submission operations. |
| Reflection | `reflection` | Provide prompt patch, skill, and teammate profile update operations. |

Teammate Profile Reflection maintains the Chairman's recruitment memory.
It is separate from team-template and handoff-rule evolution. The external
tool package's legacy `skip_l2_reflection` tool and internal `l2_reflection`
protocol remain for compatibility; these names refer to profile maintenance.

The benchmark-specific execution tools are:

| Benchmark | Execution tools |
|---|---|
| GAIA | `read_file`, `write_file`, `bash`, `web_search`, `web_fetch` |
| LoCoBench | `read_file`, `write_file`, `bash` |
| LOCA-Bench | `read_file`, `write_file`, `bash`, `loca_mcp` |
| BeyondSWE | `read_file`, `docker_bash`, `docker_str_replace_editor` |

Communication, orchestration, and reflection modules support the shared
runtime across benchmarks. Individual benchmarks may require additional
dependencies from their own installation instructions.

### Configure web search

The compatible web search implementation selects a provider in this order:

1. Serper when `SERPER_KEY_ID` is configured.
2. SerpAPI when `SERPAPI_API_KEY` is configured.
3. DuckDuckGo when neither key is configured.

To use Serper, add the following to `.env`:

```dotenv
SERPER_KEY_ID=your-serper-api-key
```

Alternatively, use SerpAPI:

```dotenv
SERPAPI_API_KEY=your-serpapi-api-key
```

DuckDuckGo does not require an API key. Web search and webpage retrieval
require network access.

### Additional runtime requirements

BeyondSWE requires a running Docker daemon and access to the container images
used by its tasks. Check Docker availability with:

```bash
docker info
```

For LOCA-Bench, install the dependencies required by the task-configured MCP
servers. The adapter initializes the environment and MCP tools for each task;
`loca_mcp` becomes available through that initialization.

### Verify tool loading

Run this check from the repository root:

```bash
python3 -B - <<'PY'
import importlib
from pathlib import Path
from core.tool_registry import ToolRegistry

required = {
    "bash",
    "read_file",
    "write_file",
    "web_search",
    "web_fetch",
    "docker_bash",
    "docker_str_replace_editor",
    "loca_mcp",
}

registry = ToolRegistry(str(Path("tools").resolve()))
missing = required - set(registry.all_names())
if missing:
    raise SystemExit(f"Missing execution tools: {sorted(missing)}")

for name in ("messaging", "primitives", "reflection"):
    importlib.import_module(f"tools.{name}")

print("Tool package loaded successfully.")
PY
```

This check verifies module imports and execution tool registration. Benchmark
data, API access, Docker images, and MCP services must be configured separately.
