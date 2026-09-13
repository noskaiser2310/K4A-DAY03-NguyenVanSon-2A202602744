"""
🧪 UNIT TESTS CHO HỆ THỐNG VINFAST EV MCP & REACT AGENT
Kiểm thử tự động các thành phần độc lập:
1. Tool Schemas (JSON Schema Specification)
2. Tool Execution Backend (Query, Booking, Edge Cases)
3. MCP Server (JSON-RPC 2.0 Compliance)
4. Test Suite Configuration Integrity (5 Test Cases)
"""

import json
import os
import sys
import unittest

# Đảm bảo import được code từ src
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from tools import (
    TOOLS_SCHEMA,
    execute_vehicle_status_query,
    execute_book_service_appointment,
    dispatch_tool_call
)
from mcp_server import MCPAcademicServer, MCPEvServiceServer


class TestToolSchemas(unittest.TestCase):
    """Kiểm thử tính hợp lệ của các khai báo Tool Schemas"""

    def test_tools_schema_structure(self):
        """Mỗi Tool Schema phải có đủ name, description, parameters với type là object"""
        self.assertGreaterEqual(len(TOOLS_SCHEMA), 2)
        tool_names = [t.get("name") for t in TOOLS_SCHEMA]
        self.assertIn("vehicle_status_query", tool_names)
        self.assertIn("book_service_appointment", tool_names)

        for tool in TOOLS_SCHEMA:
            self.assertIn("name", tool)
            self.assertIn("description", tool)
            self.assertIn("parameters", tool)
            params = tool["parameters"]
            self.assertEqual(params.get("type"), "object")
            self.assertIn("properties", params)
            self.assertIsInstance(params["properties"], dict)


class TestToolExecution(unittest.TestCase):
    """Kiểm thử tầng thực thi logic Tool (Execution Layer)"""

    def test_vehicle_query_success(self):
        """Tra cứu xe hợp lệ 30K-88888 phải trả về SUCCESS kèm dữ liệu xe"""
        raw_res = execute_vehicle_status_query("30K-88888")
        data = json.loads(raw_res)
        self.assertEqual(data["status"], "SUCCESS")
        self.assertEqual(data["license_plate"], "30K-88888")
        self.assertIn("odo_km", data["data"])
        self.assertEqual(data["data"]["odo_km"], 12450)

    def test_vehicle_query_not_found(self):
        """Tra cứu xe không tồn tại 29A-99999 phải trả về NOT_FOUND (tránh hallucination)"""
        raw_res = execute_vehicle_status_query("29A-99999")
        data = json.loads(raw_res)
        self.assertEqual(data["status"], "NOT_FOUND")

    def test_booking_appointment(self):
        """Đặt lịch bảo dưỡng phải tạo mã booking và thông báo thành công"""
        raw_res = execute_book_service_appointment(
            license_plate="30K-88888",
            service_type="Bảo dưỡng Cấp 1",
            datetime_str="08:30 18/09/2026",
            service_center="VinFast Smart City"
        )
        data = json.loads(raw_res)
        self.assertEqual(data["status"], "SUCCESS")
        self.assertIn("booking_id", data)
        self.assertIn("VF-BK-", data["booking_id"])

    def test_tool_dispatcher(self):
        """Dispatcher phải gọi đúng hàm và xử lý tool không tồn tại"""
        res_ok = dispatch_tool_call("vehicle_status_query", {"license_plate": "30K-88888"})
        self.assertEqual(json.loads(res_ok)["status"], "SUCCESS")

        res_unknown = dispatch_tool_call("invalid_tool_name", {})
        self.assertEqual(json.loads(res_unknown)["status"], "UNKNOWN_TOOL")


class TestMCPServer(unittest.TestCase):
    """Kiểm thử chuẩn Model Context Protocol (JSON-RPC 2.0)"""

    def setUp(self):
        self.server = MCPAcademicServer(server_name="vinfast-ev-test-server")

    def test_server_list_tools(self):
        """MCP Server phải công bố danh sách tool schemas"""
        tools = self.server.list_tools()
        self.assertEqual(tools, TOOLS_SCHEMA)

    def test_server_call_tool_jsonrpc(self):
        """MCP call_tool phải đóng gói chuẩn JSON-RPC 2.0"""
        payload = self.server.call_tool("vehicle_status_query", {"license_plate": "30K-88888"})
        self.assertEqual(payload.get("jsonrpc"), "2.0")
        self.assertEqual(payload.get("server"), "vinfast-ev-test-server")
        self.assertEqual(payload.get("tool"), "vehicle_status_query")
        self.assertIn("result", payload)
        self.assertEqual(payload["result"].get("status"), "SUCCESS")


class TestSuiteConfig(unittest.TestCase):
    """Kiểm thử cấu hình Test Cases trong config/test_cases.json"""

    def test_test_cases_integrity(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        config_path = os.path.join(base_dir, "config", "test_cases.json")
        self.assertTrue(os.path.exists(config_path), "File config/test_cases.json phải tồn tại.")
        with open(config_path, "r", encoding="utf-8") as f:
            tcs = json.load(f)
        self.assertEqual(len(tcs), 5, "Bộ test suite phải có đủ 5 test cases.")
        for tc in tcs:
            self.assertIn("id", tc)
            self.assertIn("type", tc)
            self.assertIn("question", tc)
            self.assertFalse(tc["question"].startswith("TODO"), f"Test case {tc['id']} vẫn còn TODO")


if __name__ == "__main__":
    unittest.main()
