# Industrial Agent MCP Server

[![CI](https://github.com/Jancapboy/industrial-agent-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/Jancapboy/industrial-agent-mcp/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Connect AI agents to factory data via the Model Context Protocol (MCP)

This project demonstrates production-grade integration of AI agents with industrial manufacturing systems. It provides structured access to equipment status, SOPs, and production data through the MCP protocol.

## 🚀 Features

- **Real-time Equipment Monitoring**: Query CNC, assembly lines, and other equipment with AI-augmented diagnostics
- **SOP Search**: Semantic search across Standard Operating Procedures
- **Production Analytics**: Shift-level and historical production statistics
- **Extensible Architecture**: Mock data layer can be replaced with real MES/ERP integrations

## 🛠️ Tools Provided

| Tool | Description | Use Case |
|------|-------------|----------|
| `query_equipment` | Get equipment status + AI diagnostics | Predictive maintenance, anomaly detection |
| `search_sop` | Search procedures by keyword/category | Operator training, troubleshooting |
| `get_production_stats` | Retrieve output/defect/downtime data | Daily reports, KPI tracking |

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/Jancapboy/industrial-agent-mcp.git
cd industrial-agent-mcp

# Install with development dependencies
pip install -e ".[dev]"
```

## 🔧 Usage

### As an MCP Server (for Claude/Cursor/Kimi)

Add to your MCP settings:

```json
{
  "mcpServers": {
    "industrial-agent": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "cwd": "/path/to/industrial-agent-mcp"
    }
  }
}
```

### Programmatic Usage

```python
from mcp_server import query_equipment, EquipmentQueryParams

# Query equipment status
params = EquipmentQueryParams(line_id="LINE_A01", equipment_type="cnc")
result = query_equipment(params)
print(result["ai_analysis"])
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test
pytest tests/test_mcp_server.py::TestEquipmentQuery
```

## 🏗️ Architecture

```
┌─────────────────┐     MCP Protocol     ┌──────────────────┐
│   AI Agent      │ ◄──────────────────► │  MCP Server      │
│ (Claude/Kimi)   │                      │  (This Project)  │
└─────────────────┘                      └────────┬─────────┘
                                                  │
                           ┌──────────────────────┼──────────────────────┐
                           │                      │                      │
                    ┌──────▼──────┐      ┌───────▼────────┐     ┌───────▼──────┐
                    │ Equipment   │      │ SOP Database   │     │ Production   │
                    │ Monitor     │      │ (Searchable)   │     │ Analytics    │
                    └─────────────┘      └────────────────┘     └──────────────┘
```

## 🔄 CI/CD Pipeline

- **Lint**: Ruff + Black for code quality
- **Type Check**: MyPy for static analysis
- **Test**: Pytest across Python 3.10/3.11/3.12
- **Coverage**: Codecov integration

## 🗺️ Roadmap

- [ ] Real database connectors (PostgreSQL, InfluxDB)
- [ ] OPC UA / MQTT integration for live data
- [ ] LLM-based diagnostics (currently rule-based)
- [ ] Web dashboard for manual oversight
- [ ] Docker deployment

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

## 🙋 About

Built as part of an industrial AI agent learning journey. Demonstrates:
- MCP protocol implementation
- Manufacturing domain knowledge
- Production-ready Python engineering
- CI/CD best practices

---

**Star ⭐ if this helps your learning!**
