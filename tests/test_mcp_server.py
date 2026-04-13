import pytest  # noqa: F401

from mcp_server import (
    EquipmentQueryParams,
    ProductionStatsParams,
    SOPSearchParams,
    get_production_stats,
    query_equipment,
    search_sop,
)


class TestEquipmentQuery:
    """Test equipment status queries."""

    def test_query_existing_equipment(self):
        """Test querying existing equipment."""
        params = EquipmentQueryParams(line_id="LINE_A01", equipment_type="cnc")
        result = query_equipment(params)

        assert "error" not in result
        assert result["line_id"] == "LINE_A01"
        assert result["equipment_type"] == "cnc"
        assert "status" in result
        assert "ai_analysis" in result
        assert result["status"]["oee"] == 0.92

    def test_query_nonexistent_equipment(self):
        """Test querying non-existent equipment."""
        params = EquipmentQueryParams(line_id="LINE_Z99", equipment_type="cnc")
        result = query_equipment(params)

        assert "error" in result
        assert "available_lines" in result

    def test_high_temperature_warning(self):
        """Test AI analysis for high temperature."""
        params = EquipmentQueryParams(line_id="LINE_B02", equipment_type="assembly")
        result = query_equipment(params)

        # This equipment has temp 120 (error state)
        assert any("error state" in a or "temperature" in a for a in result["ai_analysis"])


class TestSOPSearch:
    """Test SOP search functionality."""

    def test_search_by_keyword(self):
        """Test searching SOPs by keyword."""
        params = SOPSearchParams(keyword="CNC", category="operation")
        result = search_sop(params)

        assert result["results_count"] >= 1
        assert any("CNC" in r["title"] for r in result["results"])

    def test_search_by_category(self):
        """Test filtering by category."""
        params = SOPSearchParams(keyword="maintenance", category="maintenance")
        result = search_sop(params)

        assert all(r["category"] == "maintenance" for r in result["results"])

    def test_no_results(self):
        """Test search with no matches."""
        params = SOPSearchParams(keyword="xyz_nonexistent", category="operation")
        result = search_sop(params)

        assert result["results_count"] == 0


class TestProductionStats:
    """Test production statistics queries."""

    def test_get_stats_for_date(self):
        """Test getting stats for a specific date."""
        params = ProductionStatsParams(date="2024-03-15", shift="all")
        result = get_production_stats(params)

        assert result["date"] == "2024-03-15"
        assert result["summary"]["total_output"] == 1250
        assert "defect_rate_percent" in result["summary"]
        assert "shift_breakdown" in result

    def test_get_stats_for_shift(self):
        """Test getting stats for specific shift."""
        params = ProductionStatsParams(date="2024-03-15", shift="morning")
        result = get_production_stats(params)

        assert "shift_detail" in result
        assert result["shift_detail"]["shift"] == "morning"
        assert result["shift_detail"]["output"] == 450

    def test_get_stats_for_missing_date(self):
        """Test getting stats for date with no data."""
        params = ProductionStatsParams(date="2020-01-01", shift="all")
        result = get_production_stats(params)

        assert result["summary"]["total_output"] == 0
