import os
import re

def check_bgp_prefix_limit(config_data, limit=100):
    if not re.search(r"router bgp \d+", config_data, re.IGNORECASE):
        print("\033[33mKhông Áp Dụng:\033[0m Thiết bị không cấu hình BGP.")
        return

    matches = re.findall(r"neighbor \S+ maximum-prefix (\d+)", config_data)
    issues = [int(m) for m in matches if int(m) > limit]

    if issues:
        print("\033[31mKhông Tuân Thủ:\033[0m Không giới hạn số lượng các BGP prefix nhận quảng bá. Tìm thấy các cấu hình vượt giới hạn:")
        for issue in issues:
            print(f"  - {issue} prefix")
    elif matches:
        print("\033[32mTuân Thủ:\033[0m Đã giới hạn số lượng các BGP prefix nhận quảng bá trong giới hạn.")
    else:
        print("\033[31mKhông Tuân Thủ:\033[0m Không tìm thấy cấu hình giới hạn số lượng các BGP prefix nhận quảng bá.")

# Hàm gọi kiểm tra file log
def run_module(folder_path):
    log_files = [f for f in os.listdir(folder_path) if f.endswith('.log') or f.endswith('.txt')]

    if not log_files:
        print("Không tìm thấy file log nào.")
        return

    for log_file in log_files:
        print(f"\nĐang kiểm tra file: {log_file}")
        with open(os.path.join(folder_path, log_file), "r", encoding="utf-8") as file:
            config_data = file.read()
            check_bgp_prefix_limit(config_data)

# Chạy module
if __name__ == "__main__":
    folder_path = r"C:\Users\admin\Desktop\automation\Test"  # Thay đường dẫn tới thư mục file log của bạn
    run_module(folder_path)
