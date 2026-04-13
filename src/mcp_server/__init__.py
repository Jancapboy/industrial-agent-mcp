"""Industrial Agent MCP Server.

Provides AI agents with structured access to factory data including:
- Equipment status and diagnostics
- SOP (Standard Operating Procedure) search
- Production statistics
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Literal

from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    TextContent,
    Tool,
)
from pydantic import BaseModel, Field

# ─────────────────────────────────────────────────────────
# Mock data stores (replace with real DB/API connections)
# ─────────────────────────────────────────────────────────

EQUIPMENT_DB = {
    "LINE_A01": {
        "cnc": {
            "status": {
                "running": True,
                "temperature_c": 45,
                "spindle_rpm": 3500,
                "oee": 0.92,
            },
            "alarms": [],
            "last_maintenance": "2024-03-01",
        },
        "assembly": {
            "status": {
                "running": False,
                "temperature_c": 25,
                "cycle_time_s": 45,
                "oee": 0.0,
            },
            "alarms": ["PNEUMATIC_PRESSURE_LOW"],
            "last_maintenance": "2024-02-15",
        },
    },
    "LINE_B02": {
        "cnc": {
            "status": {
                "running": True,
                "temperature_c": 78,
                "spindle_rpm": 2800,
                "oee": 0.85,
            },
            "alarms": [],
            "last_maintenance": "2024-03-10",
        },
        "assembly": {
            "status": {
                "running": True,
                "temperature_c": 120,
                "cycle_time_s": 38,
                "oee": 0.45,
            },
            "alarms": ["OVERHEATING", "CYCLE_TIME_VARIATION"],
            "last_maintenance": "2024-01-20",
        },
    },
}

SOP_DB = [
    {
        "id": "SOP-CNC-001",
        "title": "CNC Machine Daily Startup Check",
        "category": "operation",
        "steps": 8,
        "keywords": ["CNC", "startup", "checklist", "daily"],
    },
    {
        "id": "SOP-CNC-002",
        "title": "CNC Tool Change Procedure",
        "category": "operation",
        "steps": 12,
        "keywords": ["CNC", "tool", "change", "procedure"],
    },
    {
        "id": "SOP-ASM-001",
        "title": "Assembly Line Safety Protocol",
        "category": "safety",
        "steps": 15,
        "keywords": ["assembly", "safety", "protocol", "PPE"],
    },
    {
        "id": "SOP-MNT-001",
        "title": "Preventive Maintenance for Spindle",
        "category": "maintenance",
        "steps": 20,
        "keywords": ["maintenance", "spindle", "preventive", "CNC"],
    },
    {
        "id": "SOP-QC-001",
        "title": "Welding Quality Inspection",
        "category": "quality",
        "steps": 10,
        "keywords": ["welding", "quality", "inspection", "QC"],
    },
]

PRODUCTION_DB = {
    "2024-03-15": {
        "morning": {"output": 450, "defects": 12, "downtime_min": 30},
        "afternoon": {"output": 480, "defects": 8, "downtime_min": 15},
        "night": {"output": 320, "defects": 15, "downtime_min": 45},
    },
    "2024-03-14": {
        "morning": {"output": 430, "defects": 10, "downtime_min": 20},
        "afternoon": {"output": 460, "defects": 9, "downtime_min": 10},
        "night": {"output": 310, "defects": 18, "downtime_min": 60},
    },
}


# ─────────────────────────────────────────────────────────
# Pydantic models for tool parameters
# ─────────────────────────────────────────────────────────

class EquipmentQueryParams(BaseModel):
    line_id: str = Field(description="Production line identifier, e.g. LINE_A01")
    equipment_type: Literal["cnc", "assembly", "welding", "conveyor"] = Field(
        description="Type of equipment to query"
    )


class SOPSearchParams(BaseModel):
    keyword: str = Field(description="Search keyword for SOP title or keywords")
    category: Literal["operation", "safety", "maintenance", "quality", "all"] = Field(
        default="all",
        description="SOP category filter"
    )


class ProductionStatsParams(BaseModel):
    date: str = Field(description="Date in YYYY-MM-DD format")
    shift: Literal["morning", "afternoon", "night", "all"] = Field(
        default="all",
        description="Shift filter"
    )


# ─────────────────────────────────────────────────────────
# Tool implementations
# ─────────────────────────────────────────────────────────

def query_equipment(params: EquipmentQueryParams) -> dict:
    """Query real-time equipment status with AI-augmented diagnostics."""
    line = EQUIPMENT_DB.get(params.line_id)
    if not line or params.equipment_type not in line:
        return {
            "error": f"Equipment '{params.equipment_type}' on '{params.line_id}' not found.",
            "available_lines": list(EQUIPMENT_DB.keys()),
            "available_types": (
                list(next(iter(EQUIPMENT_DB.values())).keys())
                if EQUIPMENT_DB else []
            ),
        }

    data = line[params.equipment_type]
    status = data["status"]
    alarms = data["alarms"]

    # Simple rule-based AI analysis (replace with LLM call if desired)
    ai_analysis = []
    if status["temperature_c"] > 100:
        ai_analysis.append(
            f"CRITICAL: Equipment is in error state (temperature {status['temperature_c']}°C). "
            "Immediate shutdown and cooling cycle recommended."
        )
    elif status["temperature_c"] > 80:
        ai_analysis.append(
            f"WARNING: Temperature {status['temperature_c']}°C exceeds normal operating range. "
            "Check coolant levels and ventilation."
        )
    else:
        ai_analysis.append(
            f"Temperature {status['temperature_c']}°C is within normal operating range."
        )

    if alarms:
        ai_analysis.append(f"Active alarms: {', '.join(alarms)}. Maintenance attention required.")
    else:
        ai_analysis.append("No active alarms. Equipment operating normally.")

    if status.get("oee", 1.0) < 0.5 and status["running"]:
        ai_analysis.append(
            f"OEE is low ({status['oee']:.0%}). Investigate cycle time losses and quality defects."
        )

    return {
        "line_id": params.line_id,
        "equipment_type": params.equipment_type,
        "status": status,
        "alarms": alarms,
        "last_maintenance": data["last_maintenance"],
        "ai_analysis": ai_analysis,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


def search_sop(params: SOPSearchParams) -> dict:
    """Search Standard Operating Procedures by keyword and category."""
    keyword_lower = params.keyword.lower()
    results = []

    for sop in SOP_DB:
        if params.category != "all" and sop["category"] != params.category:
            continue
        match = (
            keyword_lower in sop["title"].lower()
            or any(keyword_lower in k.lower() for k in sop["keywords"])
        )
        if match:
            results.append(sop)

    return {
        "keyword": params.keyword,
        "category": params.category,
        "results_count": len(results),
        "results": results,
    }


def get_production_stats(params: ProductionStatsParams) -> dict:
    """Retrieve production statistics for a given date and shift."""
    day_data = PRODUCTION_DB.get(params.date, {})

    if not day_data:
        return {
            "date": params.date,
            "shift": params.shift,
            "summary": {
                "total_output": 0,
                "total_defects": 0,
                "defect_rate_percent": 0.0,
                "total_downtime_min": 0,
            },
            "shift_breakdown": [],
        }

    shifts_to_include = (
        [params.shift] if params.shift != "all" else ["morning", "afternoon", "night"]
    )

    total_output = 0
    total_defects = 0
    total_downtime = 0
    shift_breakdown = []

    for shift in shifts_to_include:
        if shift in day_data:
            sdata = day_data[shift]
            total_output += sdata["output"]
            total_defects += sdata["defects"]
            total_downtime += sdata["downtime_min"]
            shift_breakdown.append({
                "shift": shift,
                "output": sdata["output"],
                "defects": sdata["defects"],
                "downtime_min": sdata["downtime_min"],
                "defect_rate_percent": (
                    round(sdata["defects"] / sdata["output"] * 100, 2)
                    if sdata["output"] else 0.0
                ),
            })

    defect_rate = (
        round(total_defects / total_output * 100, 2) if total_output else 0.0
    )

    result = {
        "date": params.date,
        "shift": params.shift,
        "summary": {
            "total_output": total_output,
            "total_defects": total_defects,
            "defect_rate_percent": defect_rate,
            "total_downtime_min": total_downtime,
        },
        "shift_breakdown": shift_breakdown,
    }

    if params.shift != "all" and shift_breakdown:
        result["shift_detail"] = shift_breakdown[0]

    return result


# ─────────────────────────────────────────────────────────
# MCP Server setup
# ─────────────────────────────────────────────────────────

server = Server("industrial-agent-mcp")


@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    return [
        Resource(
            uri="factory://lines",
            name="Production Lines",
            description="List of active production lines",
            mimeType="application/json",
        ),
        Resource(
            uri="factory://sops",
            name="Standard Operating Procedures",
            description="Indexed SOP library",
            mimeType="application/json",
        ),
    ]


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(
            name="query_equipment",
            description="Query real-time equipment status and get AI diagnostics",
            inputSchema=EquipmentQueryParams.model_json_schema(),
        ),
        Tool(
            name="search_sop",
            description="Search Standard Operating Procedures by keyword and category",
            inputSchema=SOPSearchParams.model_json_schema(),
        ),
        Tool(
            name="get_production_stats",
            description="Get production statistics for a specific date and shift",
            inputSchema=ProductionStatsParams.model_json_schema(),
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list:
    arguments = arguments or {}

    if name == "query_equipment":
        params = EquipmentQueryParams.model_validate(arguments)
        result = query_equipment(params)
        return [TextContent(type="text", text=str(result))]

    if name == "search_sop":
        params = SOPSearchParams.model_validate(arguments)
        result = search_sop(params)
        return [TextContent(type="text", text=str(result))]

    if name == "get_production_stats":
        params = ProductionStatsParams.model_validate(arguments)
        result = get_production_stats(params)
        return [TextContent(type="text", text=str(result))]

    raise ValueError(f"Unknown tool: {name}")


async def main() -> None:
    async with stdio_server(server) as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="industrial-agent-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
