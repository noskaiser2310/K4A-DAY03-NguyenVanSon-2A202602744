"""
🚀 CORE AGENT APPLICATION (DAY 03: CHATBOT VS REACT AGENT)
Thực thi so sánh giữa Chatbot Baseline (Cấp 2) và ReAct Agent kết nối MCP Server (Cấp 3).
Đề tài: Trợ lý Dịch vụ & Đặt lịch Bảo dưỡng Xe điện VinFast (VinFast EV Smart Service Agent).
"""

import json
import os
import sys
import time
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from mcp_server import MCPAcademicServer
from prompts import (
    CHATBOT_BASELINE_PROMPT,
    REACT_AGENT_SYSTEM_PROMPT,
    MAX_ITERATIONS
)
from providers import get_llm_provider

load_dotenv()

def load_test_cases():
    """Tải danh sách 5 test cases từ config/test_cases.json hoặc config/test_cases.example.json"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")
    if not os.path.exists(config_path):
        example_path = os.path.join(base_dir, "config", "test_cases.example.json")
        if os.path.exists(example_path):
            print("⚠️ [CONFIG NOTICE]: Chưa thấy file 'config/test_cases.json'. Đang dùng mẫu 'config/test_cases.example.json'.")
            print("👉 Hãy chạy: copy config/test_cases.example.json config/test_cases.json và viết test cases theo đề tài của bạn!\n")
            config_path = example_path
        else:
            config_path = "test_cases.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_waterfall_trace(trace_data: list, append: bool = True):
    """
    Ghi vết log Waterfall Trace Log ra file docs/trace_waterfall.json
    - append=True (mặc định): Lưu tích lũy toàn bộ các lượt chat / test cases vào lịch sử.
    - append=False: Ghi mới từ đầu (dùng khi chạy benchmark sạch toàn bộ test suite).
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_dir = os.path.join(base_dir, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    trace_path = os.path.join(docs_dir, "trace_waterfall.json")
    
    import datetime
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    stamped_data = []
    for item in trace_data:
        new_item = dict(item)
        if "timestamp" not in new_item:
            new_item["timestamp"] = current_time
        stamped_data.append(new_item)

    existing_data = []
    if append and os.path.exists(trace_path):
        try:
            with open(trace_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    existing_data = []
        except Exception:
            existing_data = []

    combined_data = existing_data + stamped_data
    with open(trace_path, "w", encoding="utf-8") as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=2)
    print(f"📊 [OBSERVABILITY]: Đã lưu tích lũy {len(combined_data)} sự kiện Waterfall Trace (+{len(stamped_data)} sự kiện mới) tại '{trace_path}'!")


def run_baseline_chatbot(user_query: str, provider):
    """Chạy Chatbot gốc (Cấp 2) không có công cụ gọi Tool"""
    print(f"\n💬 [CHATBOT BASELINE] Câu hỏi: {user_query}")
    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    print(f"🤖 Chatbot phản hồi:\n{response}")


def run_react_agent(user_query: str, provider, mcp_server: MCPAcademicServer, chat_history: list = None) -> list:
    """
    [REACT AGENT LOOP] Thực thi vòng lặp Thought -> Action -> Observation với MCP Server
    Hỗ trợ suy luận linh hoạt đơn bước, đa bước và hội thoại đa lượt (Multi-turn Memory).
    Trả về danh sách trace log của phiên thực thi.
    """
    print(f"\n🤖 [REACT AGENT] Câu hỏi: {user_query}")
    
    step = 0
    trace_logs = []
    tools_list = mcp_server.list_tools()
    
    # Nạp lịch sử đàm thoại trước đó nếu có (Multi-turn Memory / Slot-Filling)
    conversation_prefix = ""
    if chat_history:
        history_lines = []
        for msg in chat_history:
            role_label = "Khách hàng" if msg.get("role") == "user" else "Trợ lý Agent"
            history_lines.append(f"{role_label}: {msg.get('content', '')}")
        conversation_prefix = "Lịch sử hội thoại trước đó:\n" + "\n".join(history_lines) + "\n\n"
    
    current_prompt = f"{conversation_prefix}Yêu cầu hiện tại của khách hàng: {user_query}" if conversation_prefix else user_query
    accumulated_context = []
    
    while step < MAX_ITERATIONS:
        step += 1
        step_start_time = time.time()
        print(f"\n--- 🔄 Vòng lặp ReAct Loop (Step {step}/{MAX_ITERATIONS}) ---")
        
        # Gọi LLM với Native Tool Calling Specs
        llm_response = provider.generate_with_tools(current_prompt, tools_list, system_prompt=REACT_AGENT_SYSTEM_PROMPT)
        latency_ms = round((time.time() - step_start_time) * 1000, 2)
        
        thought = llm_response.get("thought", "Đang phân tích yêu cầu...")
        print(f"🧠 [Thought]: {thought}")
        
        # Trường hợp 1: LLM quyết định trả lời bằng văn bản trực tiếp
        if llm_response.get("type") == "text":
            final_content = llm_response.get("content", "")
            print(f"🏁 [Final Answer]:\n{final_content}")
            trace_logs.append({
                "step": step,
                "query": user_query,
                "action_type": "FINAL_ANSWER",
                "thought": thought,
                "output": final_content,
                "latency_ms": latency_ms
            })
            break
            
        # Trường hợp 2: LLM đề xuất gọi Tool (Action)
        elif llm_response.get("type") == "tool_call":
            tool_name = llm_response.get("tool_name")
            arguments = llm_response.get("arguments", {})
            
            print(f"🛠️ [Action Proposed]: {tool_name}({arguments})")
            
            # Thực thi Tool qua MCP Server
            mcp_result = mcp_server.call_tool(tool_name, arguments)
            obs_data = mcp_result.get("result", {})
            
            if not obs_data:
                print(f"👁️ [Observation từ MCP Server]: {{}}")
                print(f"⚠️ [CHÚ Ý]: MCP Server trả về kết quả rỗng!")
                final_answer = "Chưa thể xử lý chi tiết do chưa nhận được phản hồi từ MCP Server."
                trace_logs.append({
                    "step": step,
                    "query": user_query,
                    "action_type": "TOOL_EXECUTION",
                    "tool_name": tool_name,
                    "arguments": arguments,
                    "observation": {},
                    "latency_ms": latency_ms
                })
                trace_logs.append({
                    "step": step + 1,
                    "query": user_query,
                    "action_type": "FINAL_ANSWER",
                    "thought": "MCP Server trả về kết quả rỗng, kết thúc xử lý.",
                    "output": final_answer,
                    "latency_ms": 5.0
                })
                break
            else:
                obs_str = json.dumps(obs_data, ensure_ascii=False)
                print(f"👁️ [Observation từ MCP Server]: {obs_str}")
                
                trace_logs.append({
                    "step": step,
                    "query": user_query,
                    "action_type": "TOOL_EXECUTION",
                    "tool_name": tool_name,
                    "arguments": arguments,
                    "observation": obs_data,
                    "latency_ms": latency_ms
                })
                
                # Cập nhật prompt ngữ cảnh cho vòng lặp tiếp theo
                accumulated_context.append(f"[Observation từ công cụ {tool_name}]: {obs_str}")
                current_prompt = (
                    f"Yêu cầu ban đầu: {user_query}\n\n"
                    f"Tiến trình thực thi trước đó:\n" + "\n".join(accumulated_context) + "\n\n"
                    f"Hãy xem xét kỹ kết quả trên. Nếu đã có đầy đủ thông tin để trả lời trọn vẹn yêu cầu ban đầu của khách hàng, hãy đưa ra câu trả lời chi tiết bằng văn bản (không gọi thêm tool). "
                    f"Nếu yêu cầu của khách hàng cần thực hiện thêm bước tiếp theo (ví dụ: cần đặt lịch hẹn sau khi tra cứu), hãy gọi tiếp công cụ thích hợp."
                )

    # Đảm bảo nếu chạm MAX_ITERATIONS mà chưa có FINAL_ANSWER thì xuất fallback
    if trace_logs and trace_logs[-1]["action_type"] != "FINAL_ANSWER":
        last_obs = trace_logs[-1].get("observation", {})
        fallback_msg = last_obs.get("message") or json.dumps(last_obs, ensure_ascii=False)
        trace_logs.append({
            "step": step + 1,
            "query": user_query,
            "action_type": "FINAL_ANSWER",
            "thought": "Đã hoàn thành vòng lặp xử lý ReAct.",
            "output": f"Đã hoàn thành các bước xử lý qua hệ thống MCP: {fallback_msg}",
            "latency_ms": 10.0
        })

    return trace_logs


if __name__ == "__main__":
    print("==========================================================")
    print("🚗 VINFAST EV SMART SERVICE - DAY 03: CHATBOT VS REACT AGENT")
    print("==========================================================")
    
    provider = get_llm_provider()
    mcp_server = MCPAcademicServer(server_name="vinfast-ev-service-mcp-server")
    
    print(f"🔌 LLM Provider: {provider.__class__.__name__}")
    print(f"🌐 MCP Server: {mcp_server.server_name}\n")
    
    tests = load_test_cases()
    print(f"✅ Đã tải thành công {len(tests)} Test Cases thử nghiệm.\n")
    
    if "--interactive" in sys.argv:
        print("🎮 [INTERACTIVE MODE] Trò chuyện trực tiếp với Trợ lý Xe điện VinFast:")
        print("💡 Gợi ý câu hỏi thử nghiệm:")
        print("   - Câu hỏi chung: 'Xe điện VinFast VF8 cần bảo dưỡng định kỳ sau mỗi bao nhiêu km?'")
        print("   - Tra cứu xe: 'Hãy tra cứu tình trạng kỹ thuật và số ODO của xe biển số 30K-88888'")
        print("   - Đặt lịch hẹn: 'Đặt lịch bảo dưỡng định kỳ cho xe 30K-88888 vào 08:30 ngày 18/09/2026 tại VinFast Smart City'")
        print("   - Suy luận đa bước: 'Kiểm tra xem xe 30K-88888 đã đến hạn bảo dưỡng chưa, nếu đến hạn rồi thì đặt lịch giúp tôi'")
        print("   - So sánh đối đầu: Gõ 'compare <câu hỏi>' để so sánh Chatbot Baseline vs ReAct Agent.")
        print("   - Gõ 'exit' hoặc 'quit' để kết thúc phiên trò chuyện.\n")
        session_traces = []
        chat_history = []
        while True:
            try:
                user_input = input("👤 Khách hàng hỏi: ").strip()
                if not user_input or user_input.lower() in ["exit", "quit"]:
                    print("👋 Tạm biệt Quý khách! Kết thúc phiên trò chuyện.")
                    break
                if user_input.lower() == "clear":
                    chat_history = []
                    session_traces = []
                    print("🧹 Đã làm mới lịch sử đàm thoại!")
                    continue
                if user_input.lower().startswith("compare "):
                    query = user_input[8:].strip()
                    print("\n--- 🤖 1. Phản hồi từ Chatbot Baseline ---")
                    run_baseline_chatbot(query, provider)
                    print("\n--- 🚀 2. Phản hồi từ ReAct Agent ---")
                    logs = run_react_agent(query, provider, mcp_server, chat_history=chat_history)
                    final_ans = next((l["output"] for l in reversed(logs) if l.get("action_type") == "FINAL_ANSWER"), "")
                    chat_history.append({"role": "user", "content": query})
                    if final_ans:
                        chat_history.append({"role": "assistant", "content": final_ans})
                    session_traces.extend(logs)
                    save_waterfall_trace(logs, append=True)
                    continue

                logs = run_react_agent(user_input, provider, mcp_server, chat_history=chat_history)
                final_ans = next((l["output"] for l in reversed(logs) if l.get("action_type") == "FINAL_ANSWER"), "")
                chat_history.append({"role": "user", "content": user_input})
                if final_ans:
                    chat_history.append({"role": "assistant", "content": final_ans})
                session_traces.extend(logs)
                save_waterfall_trace(logs, append=True)
            except (KeyboardInterrupt, EOFError):
                print("\n👋 Đã thoát phiên tương tác.")
                break
    elif "--compare" in sys.argv:
        compare_idx = sys.argv.index("--compare")
        if compare_idx + 1 < len(sys.argv) and not sys.argv[compare_idx + 1].startswith("--"):
            compare_query = sys.argv[compare_idx + 1]
        else:
            compare_query = "Kiểm tra xem xe 30K-88888 đã đến hạn bảo dưỡng chưa, nếu đến hạn rồi thì đặt lịch giúp tôi"
        
        print("⚔️ [CHẾ ĐỘ SO SÁNH ĐỐI ĐẦU]: Chatbot Baseline (Cấp 2) vs ReAct Agent (Cấp 3)\n")
        print("=" * 60)
        print("1️⃣ [CHATBOT BASELINE] Thử nghiệm với Chatbot không có Tool:")
        run_baseline_chatbot(compare_query, provider)
        print("\n" + "=" * 60)
        print("2️⃣ [REACT AGENT] Thử nghiệm với Tác tử ReAct trang bị MCP Tools:")
        agent_logs = run_react_agent(compare_query, provider, mcp_server)
        save_waterfall_trace(agent_logs, append=True)
    elif "--all" in sys.argv:
        print("🚀 [TEST SUITE MODE] Kiểm tra 5 Test Cases:")
        completed_count = 0
        todo_count = 0
        all_traces = []
        
        for tc in tests:
            print(f"\n==================================================")
            print(f"🧪 [{tc['id']}] Loại test: {tc['type']} (Độ phức tạp: {tc['complexity']})")
            print(f"📌 Kỳ vọng: {tc['expected_behavior']}")
            
            if tc["question"].strip().startswith("TODO"):
                print(f"⏸️ [CHƯA KÍCH HOẠT - ĐANG LÀ TODO]: {tc['question']}")
                todo_count += 1
            else:
                logs = run_react_agent(tc["question"], provider, mcp_server)
                all_traces.extend(logs)
                completed_count += 1
                
        print(f"\n==================================================")
        print(f"📊 [KẾT QUẢ TEST SUITE]: Đã thực thi {completed_count}/{len(tests)} Test Cases | {todo_count} Đang chờ (TODO)")
        if all_traces:
            save_waterfall_trace(all_traces, append=False)
        print(f"💡 Để trò chuyện trực tiếp: Chạy 'python src/app.py --interactive'")
    else:
        # Chế độ mặc định
        print("ℹ️ HƯỚNG DẪN SỬ DỤNG CHƯƠNG TRÌNH:")
        print("  1. Chat trực tiếp liên tục:   python src/app.py --interactive")
        print("  2. So sánh đối đầu:           python src/app.py --compare \"<câu hỏi>\"")
        print("  3. Chạy toàn bộ Test Cases:    python src/app.py --all\n")
        
        sample_query = tests[1]["question"]
        print(f"--- 🏁 DEMO CHẠY THỬ 1 TEST CASE MẪU (TC02: Tra cứu xe VinFast) ---")
        logs = run_react_agent(sample_query, provider, mcp_server)
        save_waterfall_trace(logs, append=True)
        print("\n💡 Hãy thử ngay lệnh: python src/app.py --all để kiểm thử toàn bộ 5 test cases!")
