# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3 (BƯỚC 3 — SUBMISSION ARTIFACT)

> **Họ và Tên Học viên:** Nguyễn Văn Sơn  
> **Mã Sinh Viên / Mã Học viên:** 2A202602744 (STT: 03)  
> **Chủ đề Lựa chọn:** 🚗 **Trợ lý Dịch vụ & Đặt lịch Bảo dưỡng Xe điện VinFast (VinFast EV Smart Service Agent)** *(Nhóm Đề tài Mở / Dịch vụ Khách hàng & Vận hành Hệ sinh thái VinFast)*  
> **Mô hình LLM Thực thi:** **Google Gemini API thật (gemini-3.1-flash-lite) — 100% Native Function Calling**

---

## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX (ĐÁNH GIÁ CHỦ ĐỀ)

| Tiêu chí Đánh giá | Mức độ (1 - 5) | Giải trình chi tiết lý do chọn điểm |
| :--- | :---: | :--- |
| **1. Multi-step Reasoning** | **5 / 5** | Bài toán kiểm tra bảo dưỡng và đặt lịch dịch vụ đòi hỏi chuỗi suy luận nối tiếp bắt buộc: Phải tra cứu dữ liệu viễn thông (Telemetry) của xe để biết số ODO (ví dụ 12.450 km > 12.000 km) và xưởng ruột trước, sau đó LLM tự phân tích và tiến hành bước đặt lịch hẹn tiếp theo. |
| **2. Tool Interaction** | **5 / 5** | Hệ thống tương tác hai chiều với MCP Server độc lập qua giao thức JSON-RPC 2.0: Công cụ tra cứu đọc dữ liệu (`vehicle_status_query`) và công cụ ghi dữ liệu đặt lịch hẹn (`book_service_appointment`). |
| **3. Dynamic Decision** | **5 / 5** | Quyết định bước tiếp theo hoàn toàn phụ thuộc vào Observation: Nếu xe chưa đến mốc bảo dưỡng hoặc mã biển số không tồn tại (`NOT_FOUND`), LLM dừng lại không đặt lịch bừa bãi, giải thích trung thực tránh hiện tượng ảo giác (Anti-Hallucination). |
| **4. Long Horizon Goal** | **4 / 5** | Duy trì mục tiêu xuyên suốt từ lúc nhận câu hỏi của chủ xe, lập luận logic qua Native Function Calling, gọi tool qua MCP Server và tổng hợp câu trả lời chuyên nghiệp gửi lại người dùng. |
| **TỔNG ĐIỂM AGENTIC FIT** | **19 / 20** | *Tổng điểm 19/20 (> 12/20): Bài toán hoàn toàn phù hợp và phát huy tối đa sức mạnh của hệ thống Tác tử ReAct Agent.* |

---

## 2. TRÍCH XUẤT KẾT QUẢ WATERFALL TRACE LOG (NGHIỆM THU TRÊN GOOGLE GEMINI 3.1 FLASH-LITE THẬT)

Đoạn trích xuất log tiêu biểu từ tệp `docs/trace_waterfall.json` thể hiện trọn vẹn chuỗi suy luận ReAct đa bước (Multi-step ReAct: Bước 1 Tra cứu ➔ Bước 2 Đặt lịch ➔ Bước 3 Tổng hợp) do mô hình **gemini-3.1-flash-lite** trực tiếp thực thi và trích xuất tham số:

```json
[
  {
    "step": 1,
    "query": "Kiểm tra xem xe VinFast biển số 30K-88888 đã đến hạn bảo dưỡng chưa, nếu đến hạn rồi thì hãy đặt lịch bảo dưỡng mốc đó vào lúc 10:00 ngày 20/09/2026 tại xưởng dịch vụ quen thuộc của xe.",
    "action_type": "TOOL_EXECUTION",
    "tool_name": "vehicle_status_query",
    "arguments": {
      "license_plate": "30K-88888"
    },
    "observation": {
      "status": "SUCCESS",
      "license_plate": "30K-88888",
      "data": {
        "model": "VinFast VF8 Plus (2024)",
        "owner": "Nguyễn Tuấn Anh",
        "vin": "VF8P2024HN88888",
        "current_odo_km": 12450,
        "odo_km": 12450,
        "last_service_odo_km": 0,
        "last_service_date": "2024-03-10 (Bàn giao xe mới)",
        "battery_soh_percent": 92,
        "tire_pressure_bar": {
          "FL": 2.4,
          "FR": 2.4,
          "RL": 2.4,
          "RR": 2.4
        },
        "diagnostic_trouble_codes": [],
        "preferred_service_center": "VinFast Smart City - Hà Nội",
        "fota_current_version": "v2.4.0",
        "fota_latest_version": "v2.5.0"
      }
    },
    "latency_ms": 6677.39,
    "timestamp": "2026-09-13 11:07:18"
  },
  {
    "step": 2,
    "query": "Kiểm tra xem xe VinFast biển số 30K-88888 đã đến hạn bảo dưỡng chưa, nếu đến hạn rồi thì hãy đặt lịch bảo dưỡng mốc đó vào lúc 10:00 ngày 20/09/2026 tại xưởng dịch vụ quen thuộc của xe.",
    "action_type": "TOOL_EXECUTION",
    "tool_name": "book_service_appointment",
    "arguments": {
      "service_type": "Bảo dưỡng định kỳ Cấp 1",
      "datetime_str": "10:00 20/09/2026",
      "license_plate": "30K-88888",
      "service_center": "VinFast Smart City - Hà Nội"
    },
    "observation": {
      "status": "SUCCESS",
      "booking_id": "VF-BK-30K88888-99",
      "license_plate": "30K-88888",
      "service_type": "Bảo dưỡng định kỳ Cấp 1",
      "datetime": "10:00 20/09/2026",
      "service_center": "VinFast Smart City - Hà Nội",
      "message": "Đặt lịch thành công cho xe 30K-88888 (Bảo dưỡng định kỳ Cấp 1) tại VinFast Smart City - Hà Nội vào lúc 10:00 20/09/2026. Mã lịch hẹn: VF-BK-30K88888-99."
    },
    "latency_ms": 3511.57,
    "timestamp": "2026-09-13 11:07:18"
  },
  {
    "step": 3,
    "query": "Kiểm tra xem xe VinFast biển số 30K-88888 đã đến hạn bảo dưỡng chưa, nếu đến hạn rồi thì hãy đặt lịch bảo dưỡng mốc đó vào lúc 10:00 ngày 20/09/2026 tại xưởng dịch vụ quen thuộc của xe.",
    "action_type": "FINAL_ANSWER",
    "thought": "Gemini phản hồi trực tiếp bằng văn bản (không cần gọi công cụ).",
    "output": "Chào anh Nguyễn Tuấn Anh,\n\nDựa trên dữ liệu kỹ thuật từ xe VinFast VF8 Plus (biển số 30K-88888) của anh, tôi xin thông báo kết quả kiểm tra và lịch hẹn như sau:\n\n**1. Tình trạng bảo dưỡng:**\n*   **Số ODO hiện tại:** 12.450 km.\n*   **Đánh giá:** Xe của anh đã vượt mốc 12.000 km (mốc bảo dưỡng định kỳ Cấp 1). Do đó, xe đã đến hạn cần thực hiện bảo dưỡng định kỳ.\n\n**2. Thông tin đặt lịch hẹn:**\nTôi đã thực hiện đặt lịch hẹn bảo dưỡng cho anh theo yêu cầu:\n*   **Loại dịch vụ:** Bảo dưỡng định kỳ Cấp 1.\n*   **Thời gian:** 10:00 ngày 20/09/2026.\n*   **Địa điểm:** Xưởng dịch vụ VinFast Smart City - Hà Nội.\n*   **Mã lịch hẹn:** **VF-BK-30K88888-99**.\n\n**3. Lưu ý thêm:**\n*   **Cập nhật phần mềm:** Hiện tại xe của anh đang ở phiên bản `v2.4.0`, trong khi phiên bản mới nhất là `v2.5.0`. Anh vui lòng nhắc cố vấn dịch vụ tại xưởng kiểm tra và thực hiện cập nhật FOTA cho xe trong lần bảo dưỡng này nhé.\n*   **Tình trạng khác:** Các thông số kỹ thuật khác như áp suất lốp (đều 2.4 bar) và tình trạng pin (SoH 92%) đều đang ở trạng thái tốt, không có mã lỗi (DTC) nào được ghi nhận.\n\nChúc anh có trải nghiệm dịch vụ hài lòng tại VinFast Smart City! Nếu cần hỗ trợ thêm, anh vui lòng cho tôi biết.",
    "latency_ms": 4361.49,
    "timestamp": "2026-09-13 11:07:18"
  }
]
```

---

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [x] **100% LLM Tự nhiên (Zero if/else keyword matching):** Toàn bộ các quyết định gọi công cụ, trích xuất tham số và tổng hợp câu trả lời được thực thi trực tiếp bởi mạng nơ-ron của mô hình `gemini-3.1-flash-lite`.
- **Tổng số Test Cases đã chạy thành công:** **5 / 5** test cases (`TC01` Direct, `TC02` Single query, `TC03` Appointment, `TC04` Multi-step ReAct, `TC05` Edge case NOT_FOUND).
- **Số lượt gọi Tool qua MCP Server chính xác:** **4** lượt gọi tool (`vehicle_status_query`, `book_service_appointment`) với 100% tham số do LLM tự động suy luận và trích xuất.
- **Quan sát hệ thống (Observability):** File log `docs/trace_waterfall.json` ghi nhận đầy đủ độ trễ mạng thực tế của API (`latency_ms` từ 2.6s - 7.7s) và chi tiết từng bước.
- **Kết quả đẩy Repo nộp bài:** [x] Mã nguồn sạch sẽ, tuân thủ kiến trúc MCP Client-Server và sẵn sàng push lên GitHub cá nhân.

---

> ✅ **HOÀN TẤT NỘP BÀI:** Sao chép đường link GitHub Repository cá nhân của bạn và dán vào ô nộp bài trên hệ thống LMS VLearn để hoàn tất Bài Lab 3!
