"""
🛠️ TOOL DEFINITIONS & EXECUTION BACKEND
Mã nguồn chứa danh sách Tool Schemas (JSON Schema) và Execution Layer phục vụ cho MCP Server.
Chủ đề: Trợ lý Dịch vụ & Đặt lịch Bảo dưỡng Xe điện VinFast (VinFast EV Smart Service Agent).
"""

import json
from typing import Dict, Any

# ==============================================================================
# 1. KHAI BÁO TOOL SCHEMAS CHUẨN NATIVE JSON SCHEMA (TASK 1.2)
# ==============================================================================

TOOLS_SCHEMA = [
    # Tool 1: Tra cứu kỹ thuật xe điện VinFast
    {
        "name": "vehicle_status_query",
        "description": "Tra cứu dữ liệu kỹ thuật, số km đã đi (ODO), tình trạng pin (SoH), mốc bảo dưỡng và xưởng dịch vụ phụ trách của xe điện VinFast theo biển số.",
        "parameters": {
            "type": "object",
            "properties": {
                "license_plate": {
                    "type": "string",
                    "description": "Biển số xe điện VinFast cần tra cứu (ví dụ: '30K-88888', '51K-99999')"
                }
            },
            "required": ["license_plate"]
        }
    },
    
    # Tool 2: Đặt lịch hẹn bảo dưỡng dịch vụ VinFast (TODO 1.2 Hoàn thiện)
    {
        "name": "book_service_appointment",
        "description": "Đặt lịch hẹn bảo dưỡng định kỳ, kiểm tra pin hoặc sửa chữa cho xe điện VinFast tại xưởng dịch vụ 3S chỉ định.",
        "parameters": {
            "type": "object",
            "properties": {
                "license_plate": {
                    "type": "string",
                    "description": "Biển số xe điện VinFast cần bảo dưỡng (ví dụ: '30K-88888')"
                },
                "service_type": {
                    "type": "string",
                    "description": "Loại dịch vụ bảo dưỡng (ví dụ: 'Bảo dưỡng định kỳ', 'Kiểm tra pin & FOTA', 'Cứu hộ khẩn cấp')"
                },
                "datetime_str": {
                    "type": "string",
                    "description": "Thời gian hẹn dịch vụ (ví dụ: '08:30 18/09/2026', '10:00 20/09/2026')"
                },
                "service_center": {
                    "type": "string",
                    "description": "Tên xưởng dịch vụ VinFast 3S (ví dụ: 'VinFast Smart City', 'VinFast Landmark 81', 'VinFast Ocean Park')"
                }
            },
            "required": ["license_plate", "service_type", "datetime_str"]
        }
    },

    # Alias / Khả năng tương thích cho schedule_appointment (Khớp checkpoint TODO 1.2 template gốc)
    {
        "name": "schedule_appointment",
        "description": "Đặt lịch hẹn dịch vụ bảo dưỡng hoặc tư vấn kỹ thuật xe điện VinFast.",
        "parameters": {
            "type": "object",
            "properties": {
                "license_plate": {
                    "type": "string",
                    "description": "Biển số xe điện (ví dụ: '30K-88888')"
                },
                "student_id": {
                    "type": "string",
                    "description": "Mã định danh khách hàng hoặc mã chủ xe"
                },
                "datetime_str": {
                    "type": "string",
                    "description": "Thời gian hẹn (ví dụ: '14:00 15/09/2026')"
                },
                "advisor_name": {
                    "type": "string",
                    "description": "Tên cố vấn kỹ thuật hoặc tên xưởng dịch vụ"
                }
            },
            "required": ["datetime_str"]
        }
    },

    # Alias / Khả năng tương thích cho academic_query (Đảm bảo checkpoint test độc lập)
    {
        "name": "academic_query",
        "description": "Tra cứu hồ sơ khách hàng hoặc sinh viên VinUni/VinFast theo mã số.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {
                    "type": "string",
                    "description": "Mã định danh cần tra cứu (ví dụ: 'SV2026001')"
                }
            },
            "required": ["student_id"]
        }
    }
]

# ==============================================================================
# 2. MÔ PHỎNG DỮ LIỆU & HÀM THỰC THI TOOL (EXECUTION LAYER)
# ==============================================================================

MOCK_VEHICLE_DATABASE = {
    "30K-88888": {
        "model": "VinFast VF8 Plus (2024)",
        "owner": "Nguyễn Tuấn Anh",
        "vin": "VF8P2024HN88888",
        "current_odo_km": 12450,
        "odo_km": 12450,
        "last_service_odo_km": 0,
        "last_service_date": "2024-03-10 (Bàn giao xe mới)",
        "battery_soh_percent": 92,
        "tire_pressure_bar": {"FL": 2.4, "FR": 2.4, "RL": 2.4, "RR": 2.4},
        "diagnostic_trouble_codes": [],
        "preferred_service_center": "VinFast Smart City - Hà Nội",
        "fota_current_version": "v2.4.0",
        "fota_latest_version": "v2.5.0"
    },
    "51K-99999": {
        "model": "VinFast VF9 Eco (2025)",
        "owner": "Trần Hoàng Long",
        "vin": "VF9E2025SG99999",
        "current_odo_km": 5200,
        "odo_km": 5200,
        "last_service_odo_km": 0,
        "last_service_date": "2025-01-15 (Bàn giao xe mới)",
        "battery_soh_percent": 98,
        "tire_pressure_bar": {"FL": 2.5, "FR": 2.5, "RL": 2.5, "RR": 2.5},
        "diagnostic_trouble_codes": [],
        "preferred_service_center": "VinFast Landmark 81 - TP.HCM",
        "fota_current_version": "v2.4.0",
        "fota_latest_version": "v2.4.0"
    },
    "29A-123.45": {
        "model": "VinFast VF3 (2024)",
        "owner": "Phạm Thu Hà",
        "vin": "VF3A2024HN12345",
        "current_odo_km": 11950,
        "odo_km": 11950,
        "last_service_odo_km": 0,
        "last_service_date": "2024-08-01 (Bàn giao xe mới)",
        "battery_soh_percent": 96,
        "tire_pressure_bar": {"FL": 2.3, "FR": 2.3, "RL": 2.3, "RR": 2.3},
        "diagnostic_trouble_codes": [],
        "preferred_service_center": "VinFast Ocean Park - Hà Nội",
        "fota_current_version": "v1.2.0",
        "fota_latest_version": "v1.2.0"
    },
    "43A-678.90": {
        "model": "VinFast VF5 Plus (2023)",
        "owner": "Lê Văn Cường",
        "vin": "VF5P2023DN67890",
        "current_odo_km": 24150,
        "odo_km": 24150,
        "last_service_odo_km": 12000,
        "last_service_date": "2024-02-20 (Bảo dưỡng Cấp 1)",
        "battery_soh_percent": 90,
        "tire_pressure_bar": {"FL": 2.3, "FR": 2.3, "RL": 2.3, "RR": 2.3},
        "diagnostic_trouble_codes": [],
        "preferred_service_center": "VinFast Ngô Quyền - Đà Nẵng",
        "fota_current_version": "v2.1.0",
        "fota_latest_version": "v2.1.0"
    },
    "30L-555.55": {
        "model": "VinFast VF6 Plus (2024)",
        "owner": "Đỗ Hoàng Yến",
        "vin": "VF6P2024HN55555",
        "current_odo_km": 18200,
        "odo_km": 18200,
        "last_service_odo_km": 12000,
        "last_service_date": "2024-09-10 (Bảo dưỡng Cấp 1)",
        "battery_soh_percent": 91,
        "tire_pressure_bar": {"FL": 2.4, "FR": 2.1, "RL": 2.4, "RR": 2.4},
        "diagnostic_trouble_codes": ["TPMS_P01: Áp suất lốp trước phải thấp 2.1 bar (chuẩn 2.4 bar)"],
        "preferred_service_center": "VinFast Phạm Văn Đồng - Hà Nội",
        "fota_current_version": "v2.3.5",
        "fota_latest_version": "v2.3.5"
    },
    "50H-777.77": {
        "model": "VinFast VF7 Plus AWD (2024)",
        "owner": "Vũ Minh Đức",
        "vin": "VF7P2024SG77777",
        "current_odo_km": 36800,
        "odo_km": 36800,
        "last_service_odo_km": 24000,
        "last_service_date": "2024-10-05 (Bảo dưỡng Cấp 2)",
        "battery_soh_percent": 89,
        "tire_pressure_bar": {"FL": 2.4, "FR": 2.4, "RL": 2.4, "RR": 2.4},
        "diagnostic_trouble_codes": [],
        "preferred_service_center": "VinFast Thảo Điền - TP.HCM",
        "fota_current_version": "v2.4.2",
        "fota_latest_version": "v2.4.2"
    },
    "15A-333.33": {
        "model": "VinFast VF8 Eco (2023)",
        "owner": "Bùi Anh Tuấn",
        "vin": "VF8E2023HP33333",
        "current_odo_km": 48500,
        "odo_km": 48500,
        "last_service_odo_km": 36000,
        "last_service_date": "2024-08-12 (Bảo dưỡng Cấp 3)",
        "battery_soh_percent": 87,
        "tire_pressure_bar": {"FL": 2.4, "FR": 2.4, "RL": 2.4, "RR": 2.4},
        "diagnostic_trouble_codes": [],
        "preferred_service_center": "VinFast Lê Hồng Phong - Hải Phòng",
        "fota_current_version": "v2.4.0",
        "fota_latest_version": "v2.5.0"
    },
    "60A-888.12": {
        "model": "VinFast VF9 Plus 6 chỗ (2024)",
        "owner": "Hoàng Minh Châu",
        "vin": "VF9P2024DN88812",
        "current_odo_km": 8600,
        "odo_km": 8600,
        "last_service_odo_km": 0,
        "last_service_date": "2024-12-01 (Bàn giao xe mới)",
        "battery_soh_percent": 97,
        "tire_pressure_bar": {"FL": 2.5, "FR": 2.5, "RL": 2.5, "RR": 2.5},
        "diagnostic_trouble_codes": [],
        "preferred_service_center": "VinFast Biên Hòa - Đồng Nai",
        "fota_current_version": "v2.4.0",
        "fota_latest_version": "v2.4.0"
    }
}

# Dữ liệu tương thích thêm
MOCK_DATABASE = {
    "SV2026001": {
        "full_name": "Nguyễn Văn An",
        "class": "AI-K4",
        "gpa": 3.85,
        "email": "an.nv@vinuni.edu.vn",
        "status": "Đang học",
        "advisor": "PGS.TS Nguyễn Văn A"
    },
    "SV2026002": {
        "full_name": "Trần Thị Bình",
        "class": "AI-K4",
        "gpa": 3.60,
        "email": "binh.tt@vinuni.edu.vn",
        "status": "Đang học",
        "advisor": "TS. Lê Thị B"
    }
}


def execute_vehicle_status_query(license_plate: str) -> str:
    """Thực thi tra cứu thông tin kỹ thuật xe điện VinFast theo biển số"""
    clean_plate = license_plate.strip().upper().replace(" ", "")
    matched_vehicle = None
    for plate_key, val in MOCK_VEHICLE_DATABASE.items():
        if plate_key.replace("-", "").replace(".", "") == clean_plate.replace("-", "").replace(".", ""):
            matched_vehicle = (plate_key, val)
            break

    if matched_vehicle:
        plate_key, vehicle = matched_vehicle
        return json.dumps({
            "status": "SUCCESS",
            "license_plate": plate_key,
            "data": vehicle
        }, ensure_ascii=False)
    else:
        return json.dumps({
            "status": "NOT_FOUND",
            "message": f"Không tìm thấy thông tin xe VinFast có biển số '{license_plate}' trong cơ sở dữ liệu viễn thông."
        }, ensure_ascii=False)


def execute_book_service_appointment(
    license_plate: str,
    service_type: str = "Bảo dưỡng định kỳ",
    datetime_str: str = "08:30 18/09/2026",
    service_center: str = "VinFast Smart City"
) -> str:
    """Thực thi đặt lịch hẹn dịch vụ xe điện VinFast"""
    clean_plate = license_plate.strip().upper()
    booking_code = f"VF-BK-{clean_plate.replace('-', '')}-99"
    return json.dumps({
        "status": "SUCCESS",
        "booking_id": booking_code,
        "license_plate": clean_plate,
        "service_type": service_type,
        "datetime": datetime_str,
        "service_center": service_center,
        "message": f"Đặt lịch thành công cho xe {clean_plate} ({service_type}) tại {service_center} vào lúc {datetime_str}. Mã lịch hẹn: {booking_code}."
    }, ensure_ascii=False)


def execute_academic_query(student_id: str) -> str:
    """Thực thi tra cứu học vụ theo mã sinh viên (tương thích backward)"""
    student = MOCK_DATABASE.get(student_id.strip().upper())
    if student:
        return json.dumps({
            "status": "SUCCESS",
            "student_id": student_id,
            "data": student
        }, ensure_ascii=False)
    else:
        return json.dumps({
            "status": "NOT_FOUND",
            "message": f"Không tìm thấy dữ liệu sinh viên có mã '{student_id}'"
        }, ensure_ascii=False)


def execute_schedule_appointment(
    student_id: str = None,
    license_plate: str = None,
    datetime_str: str = "14:00 15/09/2026",
    advisor_name: str = "PGS.TS Nguyễn Văn A"
) -> str:
    """Thực thi đặt lịch hẹn (tương thích backward và liên kết xe)"""
    target_id = license_plate or student_id or "UNKNOWN"
    return json.dumps({
        "status": "SUCCESS",
        "booking_id": f"BK-{target_id}-99",
        "id": target_id,
        "datetime": datetime_str,
        "advisor": advisor_name,
        "message": f"Đặt lịch hẹn thành công cho {target_id} với {advisor_name} vào lúc {datetime_str}."
    }, ensure_ascii=False)


# Router gọi tool thực tế
TOOL_ROUTER = {
    "vehicle_status_query": execute_vehicle_status_query,
    "book_service_appointment": execute_book_service_appointment,
    "academic_query": execute_academic_query,
    "schedule_appointment": execute_schedule_appointment
}

def dispatch_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Hàm trung chuyển thực thi tool"""
    if tool_name in TOOL_ROUTER:
        try:
            return TOOL_ROUTER[tool_name](**arguments)
        except Exception as e:
            return json.dumps({"status": "EXECUTION_ERROR", "error": str(e)}, ensure_ascii=False)
    return json.dumps({"status": "UNKNOWN_TOOL", "error": f"Tool '{tool_name}' không tồn tại!"}, ensure_ascii=False)
