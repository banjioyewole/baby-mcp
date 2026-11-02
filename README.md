# baby-mcp

**weatherboy**, a very small MCP server that checks the weather and writes it on a split-flap board.

weatherboy uses [FastMCP](https://github.com/modelcontextprotocol/python-sdk) to turn a few HTTP APIs into MCP tools in about a hundred lines of Python. FastMCP reads each function's type hints and docstring and passes them to the model as the tool's description.

## Tools

| Tool | What it does |
| --- | --- |
| `get_forecast(latitude, longitude)` | Real forecast for the next five periods, from the US National Weather Service |
| `get_alerts(state)` | Active severe-weather alerts for a two-letter US state code |
| `send_missive(missive)` | Writes up to 128 characters to the split-flap display board |
| `get_missive()` | Reads what the board currently says |

Ask something like "check the weather in San Francisco and put it on the board". The model finds the coordinates, calls `get_forecast`, shortens the result to fit, and calls `send_missive`.

The weather tools work for anyone, but only for US locations, because they use the NWS API. The board tools post to a display server at `http://127.0.0.1:5001/`, so they only work when that server is running.

## Setup

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

## Local harness usage

Run it from a local agent harness such as Claude Code. The harness starts the server itself, so you never run `weatherboy.py` directly. It talks to the server over stdin and stdout. `local.json` holds the config for that:

```json
{
    "mcpServers": {
        "weatherboy": {
            "command": "/absolute/path/to/baby-mcp/venv/bin/python",
            "args": ["/absolute/path/to/baby-mcp/weatherboy.py"]
        }
    }
}
```

The paths in `local.json` are for the machine it was written on. Change them to wherever you cloned the repo, then point the harness at the file:

```bash
claude --mcp-config local.json
```
